"""Verify the published evidence and replay frozen judgments without a model."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'source'))
from calculator_harness_pilot import extract, paired
from large_model_review import judge


def read(path):
    return json.loads(path.read_text())


def unpack(archive, destination):
    with tarfile.open(archive) as tar:
        for member in tar:
            path = Path(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts:
                raise ValueError(f'Unsafe archive member: {member.name}')
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)


def main():
    hashes = read(ROOT / 'evidence-sha256.json')
    for name, expected in hashes.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    audit = {row['id']: row for row in read(ROOT / 'question-audit.json')}
    scored = {}
    for mode in ('off', 'on'):
        folder = ROOT / 'results' / mode
        reviews = read(folder / 'review.json')
        mapping = read(folder / 'review-map.json')
        assert hashlib.sha256((folder / 'review.json').read_bytes()).hexdigest() == read(folder / 'review-freeze.json')['sha256']
        judgments = {(mapping[r['key']]['model'], r['id']): r for r in reviews}
        scored[mode] = {}
        for repeat in (1, 2):
            expected = read(folder / f'run-{repeat}-scored.json')
            scored[mode][repeat] = {}
            for model in ('qwen27', 'nemo30'):
                run = folder / f'{model}-run-{repeat}'
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    shutil.copy2(run / 'suite.json', target / 'suite.json')
                    unpack(run / 'candidate.tar.gz', target)
                    rows = extract(target, 'candidate')
                    actual = {r['id']: judge(r, judgments[model, r['id']], audit) for r in rows}
                    assert actual == expected[model], (mode, repeat, model)
                    for request in (target / 'candidate').glob('turn-*/request-*.json'):
                        body = read(request)
                        assert body['chat_template_kwargs']['enable_thinking'] is (mode == 'on')
                        assert len(body['tools']) == 35 and body['max_tokens'] == 768 and body['temperature'] == 0
                scored[mode][repeat][model] = actual
                print(f'{mode} {model} repeat {repeat}: all {len(actual)} judgments and wire settings verified')
    reports = read(ROOT / 'results/on/analysis.json')['reports']
    for repeat in (1, 2):
        for model in ('qwen27', 'nemo30'):
            rows = scored['on'][repeat][model]
            for cohort, family in sorted({(r['cohort'], r['family']) for r in rows.values()}):
                group = [r for r in rows.values() if r['cohort'] == cohort and r['family'] == family]
                stats = paired([scored['off'][repeat][model][r['id']]['success'] for r in group],
                               [r['success'] for r in group])
                assert stats == reports[repeat - 1]['comparisons'][model][cohort + '::' + family]
    print('PASS: 1,056 recorded turns, frozen semantic judgments, and all thinking-toggle paired statistics verified.')


if __name__ == '__main__':
    main()
