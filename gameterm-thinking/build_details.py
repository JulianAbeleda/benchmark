"""Render every frozen question and all eight recorded responses as linked Markdown."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = {'qwen27': 'Qwen3.8-27B (Q4_K_M)', 'nemo30': 'NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M)'}


def read(path):
    return json.loads(path.read_text())


def block(text):
    fence = '`' * max(3, max((len(part) for part in re.findall(r'`+', text)), default=0) + 1)
    return f'{fence}text\n{text}\n{fence}\n'


def render():
    suite = read(ROOT / 'results/on/suite.json')
    records = {(mode, rep): read(ROOT / f'results/{mode}/run-{rep}-scored.json')
               for mode in ('off', 'on') for rep in (1, 2)}
    reviews = {}
    for mode in ('off', 'on'):
        mapping = read(ROOT / f'results/{mode}/review-map.json')
        for review in read(ROOT / f'results/{mode}/review.json'):
            reviews[mode, mapping[review['key']]['model'], review['id']] = review
    audit = {r['id']: r for r in read(ROOT / 'question-audit.json')}
    index = ['# Every question and recorded response\n',
             '[Model identities and test design](models-and-tests.md) · [Study summary](../README.md)\n',
             'All 132 questions are listed below. Each linked page contains the exact prompt, expected answer or allowed tools, '
             'and all fourteen recorded responses: the two larger models × thinking off/on × two repeats, plus three earlier 4B variants × two repeats (thinking off). '
             'Responses are reproduced verbatim, including empty answers and cutoffs. '
             'The two deterministic repeats are not independent test questions.\n']
    output = {}
    groups = sorted({(q['cohort'], q['family']) for q in suite})
    for cohort, family in groups:
        questions = [q for q in suite if (q['cohort'], q['family']) == (cohort, family)]
        index.append(f'## {cohort} / {family} — {len(questions)} questions\n')
        for q in questions:
            filename = q['id'].replace('::', '--') + '.md'
            label = q['request'].replace('\n', ' ').replace('[', '\\[').replace(']', '\\]')
            index.append(f'- [{q["id"]}](questions/{filename}) — {label}')
            lines = [f'# {q["id"]}\n', '[All questions](../README.md) · [Models and test design](../models-and-tests.md)\n',
                     f'Cohort: `{cohort}`. Task: `{family}`.\n', '## Exact question\n', block(q['request']),
                     '## Frozen expected answer / allowed tool names\n', block(json.dumps(q.get('answer', q.get('right')), ensure_ascii=False))]
            if cohort == 'clarify':
                lines += ['Question-quality audit (including any missing fact):\n', block(json.dumps(audit[q['source_id']], ensure_ascii=False, indent=2))]
            lines += ['## Recorded responses\n',
                      'The text below is the harness-delivered response, not a cleaned-up answer. '
                      'When a response was cut off, the provider may have substituted unfinished reasoning for final text. '
                      'The cutoff and completion flags remain visible. Empty output is explicitly marked.\n']
            for model, name in MODELS.items():
                for mode in ('off', 'on'):
                    for rep in (1, 2):
                        r = records[mode, rep][model][q['id']]
                        assert r['request'] == q['request']
                        review = reviews[mode, model, q['id']]
                        assert review['text'] == r['text']
                        lines += [f'### {name} — thinking {mode}, repeat {rep}\n',
                                  f'Frozen score: **{"pass" if r["success"] else "fail"}**. '
                                  f'Completed event: **{r["completed"]}**. Output cutoff: **{r["truncated"]}**. '
                                  f'Review category: `{r["response"]}`.\n',
                                  block(r['text']) if r['text'] else '*No final response text was emitted.*\n',
                                  '**Tool calls and returned results:**\n',
                                  block(json.dumps({'calls': r['calls'], 'tool_results': r['tool_results']}, ensure_ascii=False, indent=2)),
                                  '**Frozen review rationale:**\n', block(review['rationale']),
                                  f'[Scored source](../../results/{mode}/run-{rep}-scored.json) · '
                                  f'[Raw requests, SSE and events](../../results/{mode}/{model}-run-{rep}/candidate.tar.gz)\n']
            lines += ['## Earlier 4B comparison — thinking off\n',
                      'These are earlier inference runs on the same question, not a thinking-toggle experiment. '
                      'The trained Nemotron is the calculator adapter, not the rejected clarification pilot.\n']
            for model, name in [('unmodified', 'Original Nemotron 3 Nano 4B'),
                                ('nemotron', 'Calculator-trained Nemotron 3 Nano 4B'),
                                ('qwen', 'Qwen3.5-4B')]:
                for rep in (1, 2):
                    source = f'results/earlier-4b/{cohort}/run-{rep}-scored.json'
                    r = read(ROOT / source)[model][q['source_id']]
                    assert r['request'] == q['request']
                    metric = 'correct' if cohort == 'main' else 'interaction_success'
                    lines += [f'### {name} — repeat {rep}\n',
                              f'Original `{metric}` score: **{"pass" if r[metric] else "fail"}**. '
                              f'Completed event: **{r["completed"]}**. Output cutoff: **{r["truncated"]}**.\n',
                              block(r['text']) if r['text'] else '*No final response text was emitted.*\n',
                              '**Tool calls and returned results:**\n',
                              block(json.dumps({'calls': r['calls'], 'tool_results': r['tool_results']}, ensure_ascii=False, indent=2)),
                              f'[Scored source](../../{source}) · '
                              f'[Raw trace](../../results/earlier-4b/{cohort}/{model}-run-{rep}/candidate.tar.gz)\n']
            output[Path('details/questions') / filename] = '\n'.join(lines)
        index.append('')
    output[Path('details/README.md')] = '\n'.join(index).rstrip() + '\n'
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    pages = render()
    assert len(pages) == 133
    for relative, content in pages.items():
        path = ROOT / relative
        if args.check:
            assert path.read_text() == content, f'Stale generated page: {relative}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(f'{"Verified" if args.check else "Wrote"} 132 question pages, 1,848 responses, and the question index.')


if __name__ == '__main__':
    main()
