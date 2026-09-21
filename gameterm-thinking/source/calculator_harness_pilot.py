"""Natural-wording paired probe through GameTerm's actual shared Rust harness.

See research/calculator-verified-training.md. Artifacts live outside Git.
Answer judgments are explicit, arm-blinded review records, not last-number matches.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import time
import urllib.request

import numpy as np
from calculator_verified_pilot import fetch, gold, save, sha

SEED = 20260921


def verify(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    for path, digest in manifest['hashes'].items():
        if sha(path) != digest:
            raise ValueError(f'frozen input changed: {path}')
    return manifest


def freeze(args):
    root, runs = args.root, args.runs
    root.mkdir(parents=True, exist_ok=False)
    source = fetch(3000, 32)
    save(root / 'source.json', source)
    rows = [{'id': f'gsm8k-{x["row_idx"]}', 'family': 'math',
             'request': x['row']['question'], 'answer': gold(x['row']['answer'])}
            for x in source['rows']]
    known = []
    for pattern in ('*/dataset.json', '*/suite.json', '*/fit-suite.json'):
        for path in runs.glob(pattern):
            data = json.loads(path.read_text())
            items = data.get('rows', []) if isinstance(data, dict) else data
            known.extend(x.get('request', '') for x in items if isinstance(x, dict))
    for row in rows:
        if any(row['request'] in q for q in known):
            raise ValueError(f'previously used question: {row["id"]}')
    old = json.loads((runs / 'calculator-verified-sft-001/suite.json').read_text())
    for row in old:
        if row['family'] == 'plain':
            row['request'] = row['request'].replace('Write only the ', 'What is the ').rstrip('.') + '?'
            rows.append(row)
        elif row['family'] == 'selection':
            rows.append(row)
    envelope = json.loads((runs / 'nemotron-category-001/categorized-envelope.json').read_text())
    envelope.update(temperature=0.0, max_tokens=768)
    assert envelope['chat_template_kwargs']['enable_thinking'] is False
    random.Random(SEED).shuffle(rows)
    save(root / 'suite.json', rows)
    save(root / 'envelope.json', envelope)
    models = {'baseline': runs / 'nemotron-fallback-train-002/candidate-q4_k_m.gguf',
              'candidate': runs / 'calculator-verified-sft-001/candidate-q4_k_m.gguf'}
    server = Path('/home/ubuntu/env/llama.cpp/build-cuda/bin/llama-server')
    paths = [root / n for n in ('suite.json', 'envelope.json', 'source.json')]
    paths += [Path(__file__).resolve(), args.gameterm / 'crates/host/tests/calculator_study.rs',
              server, *models.values()]
    save(root / 'manifest.json', {
        'purpose': 'fresh natural-wording shared-harness paired pilot; no new training',
        'seed': 42, 'temperature': 0, 'max_tokens': 768, 'thinking': False,
        'models': {k: str(v) for k, v in models.items()}, 'server': str(server),
        'gameterm': str(args.gameterm),
        'hashes': {str(p): sha(p) for p in paths},
        'gate': {'math_net_gain_at_least': 4, 'paired_ci_lower_above_zero': True,
                 'exact_mcnemar_p_below': .05, 'plain_losses': 0, 'selection_losses': 0,
                 'new_plain_tool_use': 0, 'candidate_math_unrelated_or_incomplete': 0},
        'grading': 'Blind review of final stated answer, not occurrence of gold among intermediate numbers. '
                   'Clear final answers with explanatory prose accepted; conflicting or absent final answers fail. '
                   'Any length finish, no completed event, or unrelated math tool fails. '
                   'Math exact numeric equality; equivalent fractions accepted. '
                   'Plain answers judged for correctness, not word-only compliance. '
                   'Selection checks first proposed tool(s), not execution. '
                   'Record explicit rationale for every review judgment before unblinding.',
        'limitations': ['single training and inference seed', 'retention concepts previously evaluated',
                       'fresh math relative to located local suites, pretraining overlap unknown',
                       'shared native loop but fake blocked OS, no Air parity claim',
                       'one agent performs blinded grading, not independent human adjudication'],
        'gate_action': 'Pass justifies independent 128-question confirmation, not deployment or more training.'})
    print('Frozen 32 math + 20 natural plain + 16 selection questions.')


def run(args):
    manifest = verify(args.root)
    output = args.root / args.arm
    if output.exists():
        raise ValueError(f'output already exists: {output}')
    command = [manifest['server'], '-m', manifest['models'][args.arm], '--host', '127.0.0.1',
               '--port', '8081', '-ngl', '99', '-c', '16384', '-np', '1', '--jinja', '--seed', '42']
    with (args.root / f'{args.arm}-server.log').open('w') as log:
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(120):
                if server.poll() is not None:
                    raise RuntimeError('server exited; inspect log')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8081/health', timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(1)
            else:
                raise TimeoutError('model server did not become ready')
            env = dict(os.environ, GAMETERM_STUDY_ENVELOPE=str(args.root / 'envelope.json'),
                       GAMETERM_STUDY_SUITE=str(args.root / 'suite.json'),
                       GAMETERM_STUDY_OUTPUT=str(output),
                       GAMETERM_STUDY_ENDPOINT='http://127.0.0.1:8081/v1/chat/completions')
            with (args.root / f'{args.arm}-harness.log').open('w') as log:
                subprocess.run(['cargo', 'test', '-p', 'gameterm-host', '--test', 'calculator_study',
                                'live_headless_calculator_study', '--', '--ignored', '--nocapture'],
                               cwd=manifest['gameterm'], env=env, stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=1800)
        finally:
            server.terminate()
            try:
                server.wait(timeout=20)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
    print(f'{args.arm}: shared-harness run complete; server stopped.')


def extract(root, arm):
    records = []
    for path in sorted((root / arm).glob('turn-*/result.json')):
        data = json.loads(path.read_text())
        events = data['events']
        calls = [e for e in events if e['event'] == 'tool_proposed']
        final = [e['text'] for e in events if e['event'] == 'completed']
        reasons = []
        for sse in sorted(path.parent.glob('*.sse')):
            for line in sse.read_text().splitlines():
                if line.startswith('data: ') and line[6:] != '[DONE]':
                    reasons.extend(c.get('finish_reason') for c in json.loads(line[6:]).get('choices', []))
        row = data['question']
        records.append({**row, 'arm': arm, 'text': final[-1] if final else '',
                        'calls': calls, 'tool_results': [e for e in events if e['event'] == 'tool_resolved'],
                        'completed': bool(final), 'truncated': 'length' in reasons,
                        'outcome': data['outcome']})
    assert len(records) == len(json.loads((root / 'suite.json').read_text()))
    return records


def blind(args):
    verify(args.root)
    rows = extract(args.root, 'baseline') + extract(args.root, 'candidate')
    random.Random(SEED).shuffle(rows)
    mapping, review = {}, []
    for i, row in enumerate(rows):
        key = f'review-{i:03}'
        mapping[key] = row
        if row['family'] != 'selection':
            review.append({'key': key, 'family': row['family'], 'question': row['request'],
                           'expected': row['answer'], 'text': row['text'],
                           'correct': None, 'rationale': ''})
    save(args.root / 'blind-map.json', mapping)
    save(args.root / 'review.json', review)
    print('Review final answers without opening blind-map.json; then analyze.')


def paired(before, after):
    d = np.array(after, dtype=int) - np.array(before, dtype=int)
    gains, losses = int(sum(d == 1)), int(sum(d == -1))
    discordant = gains + losses
    p = min(1., 2 * sum(math.comb(discordant, i) for i in range(min(gains, losses) + 1))
            / 2**discordant) if discordant else 1.
    boot = np.random.default_rng(SEED).choice(d, size=(100000, len(d))).mean(axis=1)
    return {'n': len(d), 'before': sum(before), 'after': sum(after), 'gains': gains, 'losses': losses,
            'net_gain': int(d.sum()), 'paired_sd': float(d.std(ddof=1)),
            'paired_se': float(d.std(ddof=1) / np.sqrt(len(d))),
            'ci95': np.quantile(boot, [.025, .975]).tolist(), 'exact_mcnemar_p': p}


def analyze(args):
    verify(args.root)
    mapping = json.loads((args.root / 'blind-map.json').read_text())
    review = {r['key']: r for r in json.loads((args.root / 'review.json').read_text())}
    by_arm = {'baseline': {}, 'candidate': {}}
    for key, row in mapping.items():
        names = [c['name'] for c in row['calls']]
        unrelated = row['family'] == 'math' and any(n != 'calculate' for n in names)
        if row['family'] == 'selection':
            correct = bool(names) and all(n in row['right'] for n in names)
        else:
            judgment = review[key]
            assert isinstance(judgment['correct'], bool) and judgment['rationale']
            correct = judgment['correct'] and row['completed'] and not unrelated
        row.update(correct=bool(correct and not row['truncated']),
                   calculate='calculate' in names, unrelated=unrelated)
        by_arm[row['arm']][row['id']] = row
    report = {}
    for family in ('math', 'plain', 'selection'):
        a = [r for r in by_arm['baseline'].values() if r['family'] == family]
        b = [by_arm['candidate'][r['id']] for r in a]
        report[family] = paired([r['correct'] for r in a], [r['correct'] for r in b])
        report[family]['calculator_use'] = paired([r['calculate'] for r in a], [r['calculate'] for r in b])
    bad = [r['id'] for r in by_arm['candidate'].values() if r['family'] == 'math'
           and (r['unrelated'] or not r['completed'] or r['truncated'])]
    new_plain = [k for k, r in by_arm['candidate'].items() if r['family'] == 'plain'
                 and r['calls'] and not by_arm['baseline'][k]['calls']]
    m = report['math']
    passed = (m['net_gain'] >= 4 and m['ci95'][0] > 0 and m['exact_mcnemar_p'] < .05
              and report['plain']['losses'] == 0 and report['selection']['losses'] == 0
              and not bad and not new_plain)
    save(args.root / 'scored.json', by_arm)
    result = {'families': report, 'candidate_math_incomplete_or_unrelated': bad,
              'new_plain_tool_use': new_plain, 'passed_confirmation_gate': passed,
              'note': 'SD/CI are paired item variation, not training-seed variance; degenerate CI is not equivalence.'}
    save(args.root / 'analysis.json', result)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'run', 'blind', 'analyze'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--runs', type=Path, default=Path('/home/ubuntu/storage/daycare-runs'))
    parser.add_argument('--gameterm', type=Path, default=Path('/home/ubuntu/gameterm_beta'))
    parser.add_argument('--arm', choices=['baseline', 'candidate'])
    args = parser.parse_args()
    globals()[args.action](args)


if __name__ == '__main__':
    main()
