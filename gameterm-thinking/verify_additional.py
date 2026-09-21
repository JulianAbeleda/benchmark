"""Verify earlier 4B raw responses and frozen training evidence without inference."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from verify import ROOT, extract, read, unpack


def main():
    for name, expected in read(ROOT / 'additional-evidence-sha256.json').items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    total = 0
    for cohort, count in [('main', 80), ('clarify', 52)]:
        folder = ROOT / 'results/earlier-4b' / cohort
        for rep in (1, 2):
            scored = read(folder / f'run-{rep}-scored.json')
            for model in ('qwen', 'nemotron', 'unmodified'):
                run = folder / f'{model}-run-{rep}'
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    shutil.copy2(run / 'suite.json', target / 'suite.json')
                    unpack(run / 'candidate.tar.gz', target)
                    rows = extract(target, 'candidate')
                    assert len(rows) == count
                    for row in rows:
                        saved = scored[model][row['id']]
                        for key, value in row.items():
                            assert saved[key] == value, (cohort, model, rep, row['id'], key)
                    total += len(rows)
    print(f'PASS: {total} earlier 4B responses match raw traces; additional evidence hashes verified.')
    print('Historical score judgments are preserved, not independently re-adjudicated by this check.')


if __name__ == '__main__':
    main()
