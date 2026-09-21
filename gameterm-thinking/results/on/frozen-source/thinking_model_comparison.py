"""Matched thinking-on extension of the frozen large-model GameTerm study."""
import argparse
import json
import os
from pathlib import Path
import random
import shutil

from large_model_comparison import ROOT as BASELINE, MODELS, SERVER, SOURCES
from large_model_review import judge
from calculator_harness_pilot import run, extract, verify, paired
from calculator_verified_pilot import save, sha

ROOT=BASELINE.parent/'large-model-thinking-001'
GAMETERM=Path('/home/ubuntu/storage/worktrees/gameterm-thinking-study')


def thinking_envelope(envelope):
    envelope=json.loads(json.dumps(envelope))
    assert envelope['chat_template_kwargs']['enable_thinking'] is False
    envelope['chat_template_kwargs']['enable_thinking']=True
    return envelope


def freeze():
    ROOT.mkdir(exist_ok=False)
    protocol=json.loads((BASELINE/'protocol.json').read_text())
    protocol.update(thinking=True,baseline=str(BASELINE),
        purpose='Within-model thinking toggle; same 132 questions and 768-token output budget.',
        budget_note='Reasoning shares the output budget. Report truncation, not just final accuracy. No automatic budget changes.',
        driver_note='Isolated same-revision GameTerm checkout; only driver thinking setting now comes from envelope.')
    save(ROOT/'protocol.json',protocol)
    shutil.copy2(BASELINE/'suite.json',ROOT/'suite.json')
    paths=[ROOT/'protocol.json',ROOT/'suite.json',Path(__file__).resolve(),
           GAMETERM/'crates/host/tests/calculator_study.rs',
           Path('/home/ubuntu/DayCare/scripts/large_model_review.py'),
           BASELINE/'analysis.json',BASELINE/'review.json',BASELINE/'review-map.json',
           *[BASELINE/f'run-{r}-scored.json' for r in (1,2)]]
    for model in MODELS:
        source=BASELINE/f'{model}-run-1/envelope.json'
        save(ROOT/f'{model}-envelope.json',thinking_envelope(json.loads(source.read_text())))
        paths.extend([source,ROOT/f'{model}-envelope.json'])
    save(ROOT/'frozen.json',{str(p):sha(p) for p in paths})
    snapshots=ROOT/'frozen-source';snapshots.mkdir()
    for p in [Path(__file__).resolve(),Path('/home/ubuntu/DayCare/scripts/large_model_review.py'),
              GAMETERM/'crates/host/tests/calculator_study.rs']:
        shutil.copy2(p,snapshots/p.name)


def check_frozen():
    for p,h in json.loads((ROOT/'frozen.json').read_text()).items():
        assert sha(p)==h,p


def evaluate(model,repeat):
    check_frozen()
    folder=ROOT/f'{model}-run-{repeat}';folder.mkdir()
    shutil.copy2(ROOT/'suite.json',folder/'suite.json')
    shutil.copy2(ROOT/f'{model}-envelope.json',folder/'envelope.json')
    paths=[folder/'suite.json',folder/'envelope.json',ROOT/'frozen.json',
           Path(__file__).resolve(),SERVER,MODELS[model],
           GAMETERM/'crates/host/tests/calculator_study.rs',
           Path('/home/ubuntu/DayCare/scripts/calculator_harness_pilot.py')]
    save(folder/'manifest.json',dict(models={'candidate':str(MODELS[model])},
         server=str(SERVER),gameterm=str(GAMETERM),hashes={str(p):sha(p) for p in paths}))
    os.environ.update(LLAMA_ARG_CACHE_PROMPT='0',LLAMA_ARG_CACHE_RAM='0',
                      CARGO_TARGET_DIR='/home/ubuntu/gameterm_beta/target')
    run(argparse.Namespace(root=folder,arm='candidate'))


def blind():
    check_frozen()
    assert not (ROOT/'review.json').exists()
    rows=[]
    for model in MODELS:
        folder=ROOT/f'{model}-run-1';verify(folder)
        rows.extend((model,r) for r in extract(folder,'candidate'))
    random.Random(20260930).shuffle(rows)
    mapping,review={},[]
    for i,(model,row) in enumerate(rows):
        key=f'review-{i:03}';mapping[key]=dict(model=model,row=row)
        selection=row['family']=='selection'
        review.append(dict(key=key,id=row['id'],cohort=row['cohort'],family=row['family'],
            question=row['request'],expected=row.get('answer',row.get('right')),text=row['text'],
            calls=row['calls'],response='selection' if selection else ('wrong' if not row['text'] else None),
            rationale='Predeclared allowed tool names.' if selection else ('No final answer emitted.' if not row['text'] else '')))
    save(ROOT/'review-map.json',mapping);save(ROOT/'review.json',review)


def audit_wire(folder):
    requests=list((folder/'candidate').glob('turn-*/request-*.json'))
    assert len(requests)>=132
    reasoning_turns=set();reasoning_chunks=0;output_tokens=0
    for p in requests:
        x=json.loads(p.read_text())
        assert x['chat_template_kwargs']['enable_thinking'] is True,p
        assert len(x['tools'])==35 and x['max_tokens']==768 and x['temperature']==0,p
    for p in (folder/'candidate').glob('turn-*/*.sse'):
        for line in p.read_text().splitlines():
            if line.startswith('data: ') and line[6:]!='[DONE]':
                x=json.loads(line[6:]);output_tokens+=(x.get('usage') or {}).get('completion_tokens',0)
                for choice in x.get('choices',[]):
                    d=choice.get('delta',{})
                    if d.get('reasoning_content') or d.get('reasoning'):
                        reasoning_turns.add(p.parent.name);reasoning_chunks+=1
    return dict(requests=len(requests),reasoning_turns=len(reasoning_turns),
                reasoning_chunks=reasoning_chunks,output_tokens=output_tokens)


def analyze():
    check_frozen()
    reviews=json.loads((ROOT/'review.json').read_text());mapping=json.loads((ROOT/'review-map.json').read_text())
    assert len(reviews)==len(mapping) and {x['key'] for x in reviews}==set(mapping)
    judgments={(mapping[x['key']]['model'],x['id']):x for x in reviews}
    freeze_path=ROOT/'review-freeze.json';digest={'sha256':sha(ROOT/'review.json')}
    if freeze_path.exists():assert json.loads(freeze_path.read_text())==digest
    else:save(freeze_path,digest)
    audit={x['id']:x for x in json.loads((SOURCES['clarify']/'question-audit.json').read_text())}
    reports=[];all_scored=[]
    for repeat in (1,2):
        baseline=json.loads((BASELINE/f'run-{repeat}-scored.json').read_text())
        scored={};summary={};comparisons={};wire={}
        for model in MODELS:
            folder=ROOT/f'{model}-run-{repeat}';verify(folder)
            rows=extract(folder,'candidate');wire[model]=audit_wire(folder)
            scored[model]={r['id']:judge(r,judgments[model,r['id']],audit) for r in rows}
            summary[model]={};comparisons[model]={}
            for cohort,family in sorted({(r['cohort'],r['family']) for r in rows}):
                group=[r for r in scored[model].values() if r['cohort']==cohort and r['family']==family]
                key=cohort+'::'+family
                summary[model][key]=dict(n=len(group),
                    **{metric:sum(r[metric] for r in group) for metric in
                       ('success','factual_correct','calculator','tool_used','truncated')},
                    incomplete=sum(not r['completed'] for r in group))
                comparisons[model][key]=paired([baseline[model][r['id']]['success'] for r in group],
                                              [r['success'] for r in group])
        save(ROOT/f'run-{repeat}-scored.json',scored);all_scored.append(scored)
        reports.append(dict(repeat=repeat,summary=summary,comparisons=comparisons,wire=wire))
    changed={}
    def signature(row):
        return (row['text'],row['completed'],row['truncated'],
                [{k:v for k,v in c.items() if k!='call_id'} for c in row['calls']],
                [{k:v for k,v in c.items() if k!='call_id'} for c in row['tool_results']])
    for model in MODELS:
        changed[model]=[k for k,v in all_scored[0][model].items() if signature(v)!=signature(all_scored[1][model][k])]
    save(ROOT/'analysis.json',dict(reports=reports,changed_repeat_traces=changed,
         review_sha256=digest['sha256'],note='Matched 768-token budget, selected previously examined questions; repeats not independent.'))
    print(json.dumps(reports[0],indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['freeze','run','blind','analyze'])
    parser.add_argument('--model',choices=MODELS);parser.add_argument('--repeat',type=int,choices=[1,2],default=1)
    args=parser.parse_args()
    if args.action=='run':evaluate(args.model,args.repeat)
    else:globals()[args.action]()
