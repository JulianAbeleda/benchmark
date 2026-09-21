"""Run a fresh full 132-question arm through the archived native GameTerm driver."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'source'))
from calculator_harness_pilot import run
from calculator_verified_pilot import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=['qwen27', 'nemo30'], required=True)
    parser.add_argument('--thinking', choices=['off', 'on'], required=True)
    parser.add_argument('--model-file', type=Path, required=True)
    parser.add_argument('--server', type=Path, required=True)
    parser.add_argument('--gameterm', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    game, model, server = (p.resolve() for p in (args.gameterm, args.model_file, args.server))
    reference = ROOT / 'results' / args.thinking / f'{args.model}-run-1'
    original = json.loads((reference / 'manifest.json').read_text())
    assert sha(model) == original['hashes'][original['models']['candidate']], 'Model artifact differs'
    assert sha(server) == original['hashes'][original['server']], 'Server binary differs; declare a new protocol for a new build'
    assert subprocess.check_output(['git', '-C', str(game), 'rev-parse', 'HEAD'], text=True).strip() == 'e61521b3731f2c4ed387d9dbaac8fb0a6105c6e5'
    driver = game / 'crates/host/tests/calculator_study.rs'
    archived = ROOT / 'results/on/frozen-source/calculator_study.rs'
    assert driver.exists() and sha(driver) == sha(archived), 'Install the archived envelope-driven driver first'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    for name in ('suite.json', 'envelope.json'):
        shutil.copy2(reference / name, output / name)
    paths = [model, server, driver, output / 'suite.json', output / 'envelope.json', Path(__file__).resolve(), ROOT / 'source/calculator_harness_pilot.py']
    manifest = dict(models={'candidate': str(model)}, server=str(server), gameterm=str(game),
                    hashes={str(p): sha(p) for p in paths}, reference=str(reference))
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    os.environ['LLAMA_ARG_CACHE_RAM'] = '0'
    os.environ['LLAMA_ARG_CACHE_PROMPT'] = '0'
    run(SimpleNamespace(root=output, arm='candidate'))


if __name__ == '__main__':
    main()
