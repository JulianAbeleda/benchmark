"""Frozen small calculator SFT experiment; see research/calculator-verified-training.md."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import random
import re
import subprocess
import urllib.request
from fractions import Fraction
from pathlib import Path

import numpy as np

SEED = 20260920
PREFIX = 'Solve this problem. Reply with only the final number, without units or explanation.\n\n'
# Manually reviewed against GSM8K train 0:32; no derived answer-only operands.
EXPRESSIONS = [
    '48+48/2', '12*50/60', '100-100/2-15-15*2', '(120-12-12*2)/2',
    '3*2*2*52', '(10+10*(1+80/100))*(1+25/100)', '2*16+2*8', '(2*3+2)*2',
    '200-16-30-46-38-11-18', '(8*18+(10-8)*18*(1+1/2))*5',
    '847/(1+2+2*2)', '(95+15-3*5-4*15)/7', '60+60/2-5', '10+10/2+10*2',
    '120/8*20/60', '(6*2.5-6)*500*5*20-2000', '2500/5*2-200',
    '26+15+24-4-6-6*2', '2*2*3+1*2*2', '(20*2*5+200)/25',
    '11+(11+9)+(11+9-13)', '6*5*3*12', '4*2+2-3', '(75-5*7-2*10)/4',
    '100-15-23', '175-100*2/5-75*1/3', '2*20/100*1000',
    '800*(1-70/100)+400*(1-3/5)', '20-4*3', '600*(25/100)/(40/100-25/100)',
    '2*4*(1-50/100)+2*4*(1-75/100)', '(60*8+30*4)*2',
]
PLAIN = [
    ('Write only the opposite of ancient.', ['modern']),
    ('Write only the plural of tooth.', ['teeth']),
    ('Write only the past tense of swim.', ['swam']),
    ('Write only the chemical symbol for gold.', ['Au']),
    ('Write only the capital of Portugal.', ['Lisbon']),
    ('Write only the opposite of shallow.', ['deep']),
    ('Write only the plural of goose.', ['geese']),
    ('Write only the past tense of buy.', ['bought']),
    ('Write only the chemical symbol for iron.', ['Fe']),
    ('Write only the capital of Italy.', ['Rome']),
    ('Write only the opposite of narrow.', ['wide','broad']),
    ('Write only the plural of mouse.', ['mice']),
    ('Write only the past tense of speak.', ['spoke']),
    ('Write only the chemical symbol for helium.', ['He']),
    ('Write only the capital of Japan.', ['Tokyo']),
    ('Write only the opposite of victory.', ['defeat','loss']),
    ('Write only the plural of woman.', ['women']),
    ('Write only the past tense of fly.', ['flew']),
    ('Write only the chemical symbol for nitrogen.', ['N']),
    ('Write only the capital of Germany.', ['Berlin']),
]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def common_module(path):
    spec = importlib.util.spec_from_file_location('calculator_common', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fetch(offset, count):
    url = ('https://datasets-server.huggingface.co/rows?dataset=openai%2Fgsm8k'
           f'&config=main&split=train&offset={offset}&length={count}')
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def gold(answer):
    return re.search(r'####\s*([^\n]+)', answer).group(1).strip().replace(',', '')


def freeze(args):
    root, runs = args.root, args.runs
    root.mkdir(parents=True, exist_ok=True)
    if (root / 'manifest.json').exists():
        raise ValueError('already frozen')
    envelope_path = runs / 'nemotron-category-001/categorized-envelope.json'
    accepted = runs / 'nemotron-fallback-train-002'
    envelope = json.loads(envelope_path.read_text())
    common_path = runs / 'nemotron-math-tool-001/evaluate.py'
    common = common_module(common_path)
    source_path = root / 'source-train.json'
    source = json.loads(source_path.read_text()) if source_path.exists() else fetch(0, 32)
    holdout = fetch(2200, 64)
    save(source_path, source)
    save(root / 'source-holdout.json', holdout)
    prior = json.loads((accepted / 'dataset.json').read_text())['rows']
    names = [t['function']['name'] for t in envelope['tools']]
    rows, fit, checks = [], [], []
    calculator = subprocess.Popen([str(common.CALCULATOR)], text=True,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for source_row, expression in zip(source['rows'], EXPRESSIONS, strict=True):
            idx, item = source_row['row_idx'], source_row['row']
            answer, request = gold(item['answer']), PREFIX + item['question']
            result = common.execute(calculator, {'expression': expression})
            assert result['ok'] and common.number(result['outcome']) == Fraction(answer), (idx, result)
            checks.append({'index': idx, 'expression': expression, 'answer': answer, 'result': result})
            row = {'id': f'verified-call-{idx:04}', 'group': 'calculate_story',
                   'request': request, 'tool_names': names,
                   'target': {'kind': 'tool', 'name': 'calculate', 'arguments': {'expression': expression}}}
            rows.append(row)
            rows.append({'id': f'verified-result-{idx:04}', 'group': 'calculate_result',
                         'request': request, 'tool_names': names,
                         'history': [
                             {'role': 'assistant', 'content': '', 'tool_calls': [{
                                 'id': 'call_calculate', 'type': 'function',
                                 'function': {'name': 'calculate', 'arguments': {'expression': expression}}}]},
                             {'role': 'tool', 'tool_call_id': 'call_calculate', 'content': result['outcome']}],
                         'target': {'kind': 'words', 'content': answer}})
            fit.append({'id': row['id'], 'family': 'math', 'request': request, 'answer': answer})
    finally:
        calculator.terminate()
        calculator.wait()
    rng = random.Random(SEED)
    ordinary = [r for r in prior if r['target']['kind'] == 'words' and not r.get('history')]
    other = [r for r in prior if r['target']['kind'] == 'tool' and r['target']['name'] != 'calculate']
    for old in rng.sample(ordinary, 32) + rng.sample(other, 16):
        row = copy.deepcopy(old)
        row['id'] = 'replay-' + row['id']
        row['tool_names'] = names
        rows.append(row)
    suite = [{'id': f'gsm8k-{x["row_idx"]}', 'family': 'math',
              'request': PREFIX + x['row']['question'], 'answer': gold(x['row']['answer'])}
             for x in holdout['rows']]
    known = []
    for pattern in ('*/dataset.json', '*/suite.json'):
        for path in runs.glob(pattern):
            data = json.loads(path.read_text())
            items = data.get('rows', []) if isinstance(data, dict) else data
            known.extend(x.get('request', '') for x in items if isinstance(x, dict))
    for x in holdout['rows']:
        assert not any(x['row']['question'] in q for q in known), x['row_idx']
    suite.extend({'id': f'ordinary-{i}', 'family': 'plain', 'request': q,
                  'answer': answers[0], 'accepted_answers': answers} for i, (q, answers) in enumerate(PLAIN))
    available = [x for x in json.loads((accepted / 'suite.json').read_text())
                 if x.get('right') and 'calculate' not in x['right']]
    for x in rng.sample(available, 16):
        suite.append({**x, 'family': 'selection'})
    assert not {r['request'] for r in rows} & {r['request'] for r in suite}
    rng.shuffle(suite)
    dataset = {'schema': 'daycare.native_tool_sft.v1', 'seed': SEED,
               'envelope': str(envelope_path), 'envelope_sha256': sha(envelope_path), 'rows': rows}
    save(root / 'dataset.json', dataset)
    save(root / 'suite.json', suite)
    save(root / 'fit-suite.json', fit)
    save(root / 'label-verification.json', checks)
    paths = [root / n for n in ('dataset.json', 'suite.json', 'fit-suite.json', 'source-train.json',
                               'source-holdout.json', 'label-verification.json')]
    paths += [Path(__file__), envelope_path, common_path, common.CALCULATOR,
              accepted / 'train/adapter.npz', accepted / 'candidate-q4_k_m.gguf']
    save(root / 'manifest.json', {'frozen_before_training': True, 'seed': SEED,
         'training': {'rank': 4, 'alpha': 8, 'last_k': 1, 'lr': 5e-5, 'epochs': 3},
         'gate': {'net_math_gain': 8, 'bootstrap_lower_above_zero': True, 'exact_mcnemar_p_below': .05,
                  'ordinary_item_losses': 0, 'selection_item_losses': 0,
                  'new_ordinary_tool_calls': 0, 'math_loop_or_unrelated_failures': 0},
         'common': str(common_path), 'envelope': str(envelope_path),
         'hashes': {str(p): sha(p) for p in paths},
         'limitations': ['one seed', 'combined repairs', 'base-pretraining overlap unknown',
                         'selection probes previously evaluated; math deciding items fresh']})
    print('Frozen 112 training rows, 64 deciding math, 20 ordinary, 16 selection probes.')


def normalize(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


def evaluate(args):
    manifest = json.loads((args.root / 'manifest.json').read_text())
    for path, expected in manifest['hashes'].items():
        if sha(path) != expected:
            raise ValueError(f'frozen input changed: {path}')
    common = common_module(Path(manifest['common']))
    envelope = json.loads(Path(manifest['envelope']).read_text())
    suite = json.loads((args.root / ('fit-suite.json' if args.fit else 'suite.json')).read_text())
    calculator = subprocess.Popen([str(common.CALCULATOR)], text=True,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    responses = []
    def post(url, body):
        request = urllib.request.Request(url + '/v1/chat/completions', data=json.dumps(body).encode(),
                                         headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=300) as r:
            full = json.load(r)
        responses.append(full)
        return full['choices'][0]['message']
    common.post = post
    output = args.root / (args.arm + ('-fit' if args.fit else '') + '.json')
    if output.exists():
        raise ValueError(f'refusing to overwrite {output}')
    results = []
    try:
        for row in suite:
            responses.clear()
            if row['family'] == 'selection':
                message = post(args.url, common.base_body(envelope, row, envelope['tools']))
                calls = message.get('tool_calls') or []
                names = [c.get('function', {}).get('name') for c in calls]
                content, trace, error = message.get('content') or '', calls, None
                correct = bool(names) and all(n in row['right'] for n in names)
            else:
                content, trace, error = common.run_tools(args.url, envelope, row, calculator)
                correct = (common.number(content) == common.number(row['answer']) if row['family'] == 'math'
                           else normalize(content) in {normalize(x) for x in row['accepted_answers']})
            truncated = any(x['choices'][0].get('finish_reason') == 'length' for x in responses)
            if truncated:
                error = 'output truncated'
            results.append({'id': row['id'], 'family': row['family'], 'correct': bool(correct and not error),
                            'strict_number_only': bool(row['family'] == 'math' and correct and not error
                                and re.fullmatch(r'\s*[-+]?\d[\d,]*(?:\.\d+)?(?:/\d+)?\s*', content)),
                            'content': content, 'trace': trace, 'error': error,
                            'raw_responses': copy.deepcopy(responses)})
            save(output, {'complete': False, 'arm': args.arm, 'results': results})
            if len(results) % 16 == 0:
                print(f'{args.arm}: {len(results)}/{len(suite)}', flush=True)
    finally:
        calculator.terminate()
        calculator.wait()
    save(output, {'complete': True, 'arm': args.arm, 'results': results})


def analyze(args):
    arms = [json.loads((args.root / f'{a}.json').read_text()) for a in ('baseline', 'candidate')]
    assert all(a['complete'] for a in arms)
    before, after = [{r['id']: r for r in a['results']} for a in arms]
    assert before.keys() == after.keys()
    report = {}
    for family in ('math', 'plain', 'selection'):
        keys = [k for k in before if before[k]['family'] == family]
        d = np.array([int(after[k]['correct']) - int(before[k]['correct']) for k in keys])
        gains, losses = int(sum(d == 1)), int(sum(d == -1))
        n = gains + losses
        p = min(1., 2 * sum(math.comb(n, i) for i in range(min(gains, losses) + 1)) / 2**n) if n else 1.
        boot = np.random.default_rng(SEED).choice(d, size=(100000, len(d))).mean(axis=1)
        report[family] = {'n': len(keys), 'before': sum(before[k]['correct'] for k in keys),
                          'after': sum(after[k]['correct'] for k in keys), 'gains': gains, 'losses': losses,
                          'net_gain': int(d.sum()), 'sd': float(d.std(ddof=1)),
                          'se': float(d.std(ddof=1)/np.sqrt(len(d))),
                          'ci95': np.quantile(boot, [.025, .975]).tolist(), 'exact_mcnemar_p': p,
                          'before_tool_use': sum(bool(before[k]['trace']) for k in keys),
                          'after_tool_use': sum(bool(after[k]['trace']) for k in keys)}
    bad = [r['id'] for r in after.values() if r['family'] == 'math' and r['error'] and
           ('loop' in r['error'] or 'unexpected tool' in r['error'])]
    new_plain = [k for k in before if before[k]['family'] == 'plain' and
                 after[k]['trace'] and not before[k]['trace']]
    m = report['math']
    passed = (m['net_gain'] >= 8 and m['ci95'][0] > 0 and m['exact_mcnemar_p'] < .05
              and report['plain']['losses'] == 0 and report['selection']['losses'] == 0
              and not bad and not new_plain)
    save(args.root / 'analysis.json', {'families': report, 'passed_investment_gate': passed,
         'math_loop_or_unrelated': bad, 'new_plain_tool_use': new_plain})
    print(json.dumps({'families': report, 'passed_investment_gate': passed}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['freeze', 'evaluate', 'analyze'])
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--runs', type=Path)
    p.add_argument('--url', default='http://127.0.0.1:8081')
    p.add_argument('--arm', choices=['baseline', 'candidate'])
    p.add_argument('--fit', action='store_true')
    args = p.parse_args()
    globals()[args.action](args)


if __name__ == '__main__':
    main()
