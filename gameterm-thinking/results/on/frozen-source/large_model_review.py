"""Arm-hidden semantic review for the larger-model extension."""
import argparse
import json
import random

from large_model_comparison import ROOT, MODELS, SOURCES
from calculator_harness_pilot import extract, paired, verify
from calculator_verified_pilot import save, sha
from calculator_quality_review import score


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
            question=row['request'],expected=row.get('answer',row.get('right')),text=row['text'],
            calls=row['calls'],response='selection' if row['family']=='selection' else None,
            rationale='Scored using the predeclared allowed tool names.' if row['family']=='selection' else ''))
    save(ROOT/'review-map.json',mapping);save(ROOT/'review.json',review)


def judge(row,review,audit):
    assert review['text']==row['text'], 'Changed repeated answer requires a fresh review.'
    names=[c['name'] for c in row['calls']]
    if row['family']=='selection':
        success=bool(names) and all(n in row['right'] for n in names) and not row['truncated']
    elif row['cohort']=='clarify':
        violation=any(n!='calculate' for n in names) or (row['family'] in ('plain','clarification') and bool(names))
        result=score(audit[row['source_id']],dict(review,completed=row['completed'],
                     truncated=row['truncated'],policy_violation=violation))
        success=result['interaction_success']
    else:
        assert review['response'] in ('correct_answer','targeted_clarification','partial','wrong') and review['rationale']
        unrelated=any(n!='calculate' for n in names) if row['family'] in ('math','smoke','oracle') else bool(names)
        success=review['response']=='correct_answer' and row['completed'] and not row['truncated'] and not unrelated
    factual=review['response']=='correct_answer' and row['completed'] and not row['truncated']
    return dict(row,success=bool(success),factual_correct=bool(factual),
                tool_used=bool(names),calculator='calculate' in names,response=review['response'])


def wire_audit():
    reports={}
    for model in MODELS:
        runs=[]
        for rep in (1,2):
            folder=ROOT/f'{model}-run-{rep}'/'candidate'
            requests=list(folder.glob('turn-*/request-*.json'))
            reasoning=0
            for path in requests:
                request=json.loads(path.read_text())
                assert request['chat_template_kwargs']['enable_thinking'] is False, path
                assert len(request['tools'])==35 and request['temperature']==0 and request['max_tokens']==768, path
            for path in folder.glob('turn-*/*.sse'):
                for line in path.read_text().splitlines():
                    if line.startswith('data: ') and line[6:]!='[DONE]':
                        for choice in json.loads(line[6:]).get('choices',[]):
                            delta=choice.get('delta',{})
                            reasoning+=bool(delta.get('reasoning_content') or delta.get('reasoning'))
            runs.append(dict(repeat=rep,requests=len(requests),reasoning_chunks=reasoning))
        first=extract(ROOT/f'{model}-run-1','candidate')
        second=extract(ROOT/f'{model}-run-2','candidate')
        def signature(row):
            return (row['id'],row['text'],row['completed'],row['truncated'],
                    [{k:v for k,v in c.items() if k!='call_id'} for c in row['calls']],
                    [{k:v for k,v in c.items() if k!='call_id'} for c in row['tool_results']])
        changed=[a['id'] for a,b in zip(first,second) if signature(a)!=signature(b)]
        reports[model]=dict(runs=runs,changed_repeat_traces=changed)
    save(ROOT/'wire-audit.json',reports)


def analyze():
    mapping=json.loads((ROOT/'review-map.json').read_text());reviews=json.loads((ROOT/'review.json').read_text())
    assert len(reviews)==len(mapping) and {x['key'] for x in reviews}==set(mapping)
    judgments={(mapping[x['key']]['model'],x['id']):x for x in reviews}
    audit={x['id']:x for x in json.loads((SOURCES['clarify']/'question-audit.json').read_text())}
    review_hash={'sha256':sha(ROOT/'review.json')}
    frozen=ROOT/'review-freeze.json'
    if frozen.exists():
        assert json.loads(frozen.read_text())==review_hash, 'Frozen judgments changed.'
    else:
        save(frozen,review_hash)
    reports=[]
    for rep in (1,2):
        scored={};summary={}
        for model in MODELS:
            folder=ROOT/f'{model}-run-{rep}';verify(folder)
            scored[model]={r['id']:judge(r,judgments[model,r['id']],audit) for r in extract(folder,'candidate')}
            summary[model]={}
            for cohort in SOURCES:
                summary[model][cohort]={}
                for family in sorted({r['family'] for r in scored[model].values() if r['cohort']==cohort}):
                    group=[r for r in scored[model].values() if r['cohort']==cohort and r['family']==family]
                    summary[model][cohort][family]=dict(n=len(group),correct=sum(r['success'] for r in group),
                       factual_correct=sum(r['factual_correct'] for r in group),
                       tool_used=sum(r['tool_used'] for r in group),
                       calculator=sum(r['calculator'] for r in group),incomplete=sum(not r['completed'] for r in group),
                       truncated=sum(r['truncated'] for r in group),
                       targeted_clarification=sum(r['response']=='targeted_clarification' for r in group))
        comparisons={}
        for cohort,source in SOURCES.items():
            filename=f'unmodified-extended-run-{rep}-scored.json' if cohort=='main' else f'run-{rep}-scored.json'
            old=json.loads((source/filename).read_text())
            for family in summary['qwen27'][cohort]:
                ids=[k for k,r in scored['qwen27'].items() if r['cohort']==cohort and r['family']==family]
                pools={m:[scored[m][k]['success'] for k in ids] for m in MODELS}
                for m,data in old.items():
                    metric='correct' if cohort=='main' else 'interaction_success'
                    pools[m]=[data[k.split('::',1)[1]][metric] for k in ids]
                comparisons[cohort+'::'+family]={}
                for newer in MODELS:
                    for reference in ('unmodified','nemotron','qwen'):
                        comparisons[cohort+'::'+family][newer+' vs '+reference]=paired(pools[reference],pools[newer])
                comparisons[cohort+'::'+family]['qwen27 vs nemo30']=paired(pools['nemo30'],pools['qwen27'])
        save(ROOT/f'run-{rep}-scored.json',scored)
        reports.append(dict(repeat=rep,summary=summary,comparisons=comparisons))
    save(ROOT/'analysis.json',dict(reports=reports,review_sha256=sha(ROOT/'review.json'),
        note='Same deterministic repetitions are not independent samples; paired statistics describe these selected questions. No causal size or training claim.'))
    wire_audit()
    print(json.dumps(reports[0]['summary'],indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['blind','analyze']);args=parser.parse_args()
    globals()[args.action]()
