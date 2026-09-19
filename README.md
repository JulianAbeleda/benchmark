# benchmark

Small, repeatable tests of the local models that GameTerm runs. Each test has
its own folder with the script, the questions, and every recorded run.

This repo is tooling. It is not part of any product, and nothing here ships.

## Tests

| Folder | Question it answers |
|---|---|
| [`bc-arithmetic`](bc-arithmetic/) | How much better is a small model at arithmetic when it can call `bc`, and how well does it write `bc` commands? |

## Requirements

- macOS with the Arkey root installed (`~/Library/Application Support/Arkey`):
  the test uses its `llama-server` and the models under `models/<name>/model.gguf`.
- `python3.12`. No packages.
- Nothing else may be using port 8097. GameTerm can stay closed; the test
  starts its own engine and stops it.

## How a run is recorded

`results/<run name>/<model>.json` holds every question, the model's reply, the
commands it wrote and what they printed. `report.py` writes one Markdown page
per model and a `README.md` summary beside them. Results are committed, so a
later run can be compared with an earlier one.
