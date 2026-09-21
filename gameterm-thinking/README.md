# GameTerm calculator use: larger models, thinking off and on

Does thinking change calculator use and completed answers inside GameTerm's
actual harness? This experiment evaluates the installed Qwen3.8-27B Q4_K_M and
NVIDIA Nemotron 3 Nano 30B-A3B Q4_K_M on the same 132 questions, with thinking
off and on, twice per setting. **No weights were trained in this experiment.**

The calculator executes through GameTerm's real coordinator, harness, provider,
argument normalizer and `fend` implementation. The 35-tool menu is preserved;
OS actions and unavailable external providers are fixtures. This is a server
headless test, not a claim of complete parity with the app on a MacBook Air.

## Research report and appendices

- [Research report](PAPER.md): questions, related work, methods, results, uncertainty and limitations.
- [Exact models and test design](details/models-and-tests.md): Qwen3.8-27B versus the earlier Qwen3.5-4B, Nemotron variants, filenames and hashes.
- [Every question and model response](details/README.md): 132 prompts, 1,848 recorded responses, tool arguments and receipts, including both repeats.
- [Training method and XML artifacts](training/README.md): actual 4B LoRA examples, settings, source records, the original NPZ/XML gap, and verified correction.
- [Original thinking report](large-model-thinking.md) and [original baseline report](large-model-comparison.md): unchanged historical research snapshots.

The main matched experiment contains 1,056 larger-model turns. The appendix
also includes 792 earlier 4B responses on the same questions. These are
descriptive experiments on previously examined prompts, not 1,848 independent
questions or a fresh confirmation.

## Inspect and verify without a GPU

```sh
python3 -m venv .venv
.venv/bin/pip install -r gameterm-thinking/requirements.txt
.venv/bin/python gameterm-thinking/verify.py
.venv/bin/python gameterm-thinking/verify_additional.py
.venv/bin/python gameterm-thinking/build_details.py --check
```

The verifier checks the export hashes, extracts the compressed wire evidence in
a temporary directory, applies the original scorer to the frozen review,
compares every recorded score, checks thinking/tool-count/token-limit settings,
and recomputes the thinking-toggle paired statistics. It does not call a model
or network service. Run normally, without Python's `-O` assertion-disabling flag.

- `results/{off,on}/`: protocols, suites, frozen review and arm maps, scored
  answers, analysis and original provenance manifests.
- `results/{off,on}/{model}-run-{1,2}/candidate.tar.gz`: lossless request JSON,
  streamed SSE responses, events, calculator receipts, and final outcomes for
  all 132 turns. Archives contain no weights or build/server logs.
- `source/`: unchanged DayCare runner/scorer dependencies. The original study
  entry points contain historical server paths; use the wrapper below for new
  inference rather than editing archived source.
- `results/{off,on}/frozen-source/`: the study's original source snapshots,
  including the Rust harness driver.
- `evidence-sha256.json`: relocation-independent hashes of exported evidence.
  Original absolute-path manifests are preserved, not rewritten to imply the
  original freeze happened here.

## Run fresh inference

This requires access to the matching GameTerm source, Rust dependencies, the
matching model artifact and server binary, and adequate GPU memory. The
original GPU was an RTX 5090 with 32 GB. Run one model at a time; port 8081 must
be free. The wrapper starts and stops its own server, refuses existing output
folders, and leaves archived results untouched.

Use a **dedicated clean GameTerm checkout** at
`e61521b3731f2c4ed387d9dbaac8fb0a6105c6e5`. Install
`results/on/frozen-source/calculator_study.rs` as
`crates/host/tests/calculator_study.rs` there. This driver reads the explicit
thinking flag from the envelope and asserts exact first-request parity.
It works for either setting; the original off driver hard-coded false.

```sh
.venv/bin/python gameterm-thinking/run.py \
  --model nemo30 --thinking on \
  --model-file /path/to/NVIDIA-Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf \
  --server /path/to/llama-server \
  --gameterm /path/to/dedicated-gameterm-checkout \
  --output /path/to/new-run
```

Use `--model qwen27` for Qwen, `--thinking off` for the baseline, and a new
output directory for each repeat. The wrapper retains temperature 0, seed 42,
context 16,384, one slot, disabled prompt/RAM caches, all 35 tools and the exact
saved envelope (including model-specific token bans). New answers require new
semantic review if they differ; never reuse old judgments on changed answers.

Model SHA-256:

- Qwen: `31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34`.
  The installed file's GGUF metadata labels it Qwen3.8-27B. An upstream checksum
  for that file was not independently established.
- Nemo: `0f111a0d49777a2a0178758b1aee14e5365c495987499401ef3ebe87754322a8`.
  Publisher/revision is recorded in the off report.
- Server binary: `3199983082f507fb694d10a43e208d4eca5e444daa2f5569ec8f56ee9ea52fe0`.

The local llama.cpp checkout currently reports revision
`ac4cddeb0dbd778f650bf568f6f08344a06abe3a` **with local modifications**.
That revision is not a sufficient build recipe for the historical binary.
Neither server binaries nor weights are redistributed here. The wrapper
requires the recorded binary hash; another build needs a separately declared
protocol. Thus archived-score replay is portable, while exact fresh-inference
reproduction still depends on access to the original artifacts and GameTerm.
The new wrapper's argument/guard checks have been tested; no new model run was
performed just to publish this archive.

GameTerm's historical strict checks had existing Clippy and formatting failures;
those are documented in the thinking report. The four thinking live runs and
relevant provider contract test passed. Publication does not claim those
unrelated repository failures were repaired.

## Provenance and scope

DayCare experiment commits: off setup `5cb45bd`, off report `c88c34a`, thinking
setup `cc08ae8`, thinking report `e9f664e`. Those commit identifiers describe the
local experiment history; they are not a promise that each is publicly reachable.
DayCare owns training and the original research record; this repository owns
the published benchmark evidence. This archive does not publish weights,
change training, deploy an adapter, or claim a fresh statistical confirmation.

Exported requests preserve the app's character/system prompt, public creator
name, tool schemas, and historical `/home/ubuntu` paths for fidelity. The
publication scan found no credential patterns, email addresses, or
non-loopback IP addresses. Keep future real-user traces out of these synthetic
benchmark records.
