"""Extend the frozen native-harness comparisons to larger existing models."""
import argparse
import json
import os
from pathlib import Path
import random
import subprocess
import time
import urllib.request

from calculator_harness_pilot import run, extract, verify, paired
from calculator_verified_pilot import save, sha

RUNS=Path('/home/ubuntu/storage/daycare-runs')
ROOT=RUNS/'large-model-comparison-001'
SERVER=Path('/home/ubuntu/env/llama.cpp/build-cuda/bin/llama-server')
MODELS={'qwen27':Path('/home/ubuntu/storage/models/Qwen3.8-27B-Q4_K_M.gguf'),
        'nemo30':Path('/home/ubuntu/storage/models/NVIDIA-Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf')}
SOURCES={'main':RUNS/'qwen-nemotron-comparison-001', 'clarify':RUNS/'calculator-clarification-001'}


def freeze():
    assert not (ROOT/'protocol.json').exists()
    rows=[]
    for cohort,source in SOURCES.items():
        rows.extend(dict(row,id=cohort+'::'+row['id'],source_id=row['id'],cohort=cohort)
                    for row in json.loads((source/'suite.json').read_text()))
    assert len(rows)==132 and len({r['id'] for r in rows})==132
    save(ROOT/'suite.json',rows)
    save(ROOT/'protocol.json',dict(
        purpose='Descriptive extension of existing frozen comparisons, no training or adoption claim.',
        models={k:str(v) for k,v in MODELS.items()},repeats=2,thinking=False,temperature=0,seed=42,
        server_context=16384,max_tokens=768,tools=35,cache_prompt=False,cache_ram=0,
        main='32 natural math, 20 ordinary, 16 selection, four smoke, eight supplied-expression cases.',
        clarify='24 clear math, eight underspecified/ambiguous, 20 ordinary controls.',
        scoring='Keep original frozen rubrics and answer keys. Explicit arm-hidden final-answer review; prose/units accepted. No numeric substring grading. Clarification must ask for the actual missing fact without guessing or calling tools. Plain controls require no tools. Selection requires calls and all proposed names allowed, not completed external execution. Truncated/incomplete math fails.',
        comparisons='Per-cohort per-task paired SD, SE, bootstrap CI, exact McNemar; never pool deterministic repeats.',
        limits=['Previously examined questions, not fresh holdout or independent confirmation.',
                'Qwen3.8-27B versus earlier Qwen3.5-4B confounds size with model version.',
                'Nemotron 30B-A3B is MoE, about 3.5B active, not compute-matched to dense Qwen27B.',
                'Existing server harness with blocked OS tools, not Air UI parity.',
                'Single agent semantic reviewer, not independent human adjudication.']))
    save(ROOT/'frozen.json',{str(p):sha(p) for p in [ROOT/'suite.json',ROOT/'protocol.json',
         *[s/'suite.json' for s in SOURCES.values()],SOURCES['clarify']/'question-audit.json']})


def probe(model):
    output=ROOT/f'{model}-token-bans.json'
    assert not output.exists()
    command=[str(SERVER),'-m',str(MODELS[model]),'--host','127.0.0.1','--port','8081',
             '-ngl','99','-c','16384','-np','1','--jinja','--seed','42']
    with (ROOT/f'{model}-probe-server.log').open('w') as log:
        server=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,
                                env=dict(os.environ,LLAMA_ARG_CACHE_PROMPT='0',LLAMA_ARG_CACHE_RAM='0'))
        try:
            for _ in range(120):
                if server.poll() is not None: raise RuntimeError('probe server exited')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8081/health',timeout=1) as response:
                        if response.status==200:break
                except OSError:time.sleep(1)
            else:raise TimeoutError('probe server readiness')
            old=json.loads((SOURCES['main']/'qwen-token-bans.json').read_text())
            probes=[]
            for item in old['probes']:
                req=urllib.request.Request('http://127.0.0.1:8081/tokenize',
                    data=json.dumps(dict(content=item['text'],add_special=False)).encode(),
                    headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=30) as response:tokens=json.load(response)['tokens']
                probes.append(dict(text=item['text'],tokens=tokens))
            ids=sorted({p['tokens'][0] for p in probes if len(p['tokens'])==1})
            save(output,dict(probes=probes,ids=ids,source_sha256=sha('/home/ubuntu/gameterm_beta/crates/native/src/agent/dash_free.rs')))
            with urllib.request.urlopen('http://127.0.0.1:8081/props',timeout=30) as response:save(ROOT/f'{model}-props.json',json.load(response))
        finally:
            server.terminate()
            try:server.wait(timeout=20)
            except subprocess.TimeoutExpired:server.kill();server.wait()
    print(model,'probed',len(ids),'native punctuation token bans',flush=True)


def evaluate(model,repeat):
    for p,h in json.loads((ROOT/'frozen.json').read_text()).items():assert sha(p)==h,p
    folder=ROOT/f'{model}-run-{repeat}';folder.mkdir()
    save(folder/'suite.json',json.loads((ROOT/'suite.json').read_text()))
    envelope=json.loads((SOURCES['main']/'qwen-run-1/envelope.json').read_text())
    envelope['model']=MODELS[model].stem
    envelope['logit_bias']={str(i):-100 for i in json.loads((ROOT/f'{model}-token-bans.json').read_text())['ids']}
    save(folder/'envelope.json',envelope)
    paths=[folder/'suite.json',folder/'envelope.json',ROOT/'protocol.json',ROOT/'frozen.json',
           ROOT/f'{model}-token-bans.json',MODELS[model],SERVER,Path(__file__).resolve(),
           Path('/home/ubuntu/DayCare/scripts/calculator_harness_pilot.py'),
           Path('/home/ubuntu/gameterm_beta/crates/host/tests/calculator_study.rs')]
    save(folder/'manifest.json',dict(models={'candidate':str(MODELS[model])},model_label=model,
         server=str(SERVER),gameterm='/home/ubuntu/gameterm_beta',hashes={str(p):sha(p) for p in paths}))
    run(argparse.Namespace(root=folder,arm='candidate'))


def blind():
    assert not (ROOT/'review.json').exists()
    rows=[]
    for model in MODELS:
        sub=ROOT/f'{model}-run-1';verify(sub)
        rows.extend((model,row) for row in extract(sub,'candidate'))
    random.Random(20260929).shuffle(rows)
    mapping,review={},[]
    for i,(model,row) in enumerate(rows):
        key=f'review-{i:03}';mapping[key]=dict(model=model,row=row)
        review.append(dict(key=key,id=row['id'],cohort=row['cohort'],family=row['family'],
            question=row['request'],expected=row['answer'],text=row['text'],calls=row['calls'],
            response=None,rationale=''))
    save(ROOT/'review-map.json',mapping);save(ROOT/'review.json',review)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['freeze','probe','run','blind'])
    parser.add_argument('--model',choices=MODELS)
    parser.add_argument('--repeat',type=int,default=1)
    args=parser.parse_args()
    if args.action=='freeze':freeze()
    elif args.action=='probe':probe(args.model)
    elif args.action=='run':evaluate(args.model,args.repeat)
    else:blind()
