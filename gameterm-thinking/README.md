# GameTerm calculator use: larger models, thinking off and on

Does thinking change calculator use and completed answers inside GameTerm's
actual harness? This experiment evaluates the installed Qwen3.8-27B Q4_K_M and
NVIDIA Nemotron 3 Nano 30B-A3B Q4_K_M on the same 132 questions, with thinking
off and on, twice per setting. **No weights were trained in this experiment.**

The calculator executes through GameTerm's real coordinator, harness, provider,
argument normalizer and `fend` implementation. The 35-tool menu is preserved;
OS actions and unavailable external providers are fixtures. This is a server
headless test, not a claim of complete parity with the app on a MacBook Air.

## What happened

Each cell is the score in either repeat; repeating deterministic responses does
not double the number of independent questions.

| Outcome | Qwen off | Qwen on | Nemo off | Nemo on |
|---|---:|---:|---:|---:|
| Clear math correct, /24 | 24 | 24 | 22 | 22 |
| Calculator used on clear math, /24 | 24 | 24 | 1 | 16 |
| Original math correct, /32 | 29 | 29 | 26 | 24 |
| Appropriate clarification, /8 | 3 | 3 | 5 | 3 |
| Tool selection, /16 | 12 | 9 | 5 | 9 |
| Calculator smoke answers, /4 | 4 | 4 | 0 | 2 |
| Supplied-expression answers, /8 | 8 | 8 | 4 | 7 |
| Ordinary answers without tools, /20 in each cohort | 20 | 20 | 14 | 20 |
| Turns with any output cutoff, /132 | 2 | 9 | 0 | 20 |

Thinking increased Nemo's calculator use, but did not improve its clear-math
score. Two answers improved and two previously correct answers were cut off.
All failed original/clear math responses in the thinking runs involved output
cutoffs. Reasoning and the final response share the **768-token limit per
inference response**. This is a controlled toggle at that limit, not a benchmark
of either mode's best possible settings. A larger budget is a hypothesis to
test, not an established fix.

A successful calculator call is not sufficient for a correct final answer:
one recorded Nemo response received the correct large product and copied it
with an extra digit. Tool choice, expression correctness, execution, and final
reporting are separate failure points.

Read the full [thinking report](large-model-thinking.md) and
[thinking-off report](large-model-comparison.md) for failure examples and
per-task SD, SE, bootstrap intervals and exact McNemar tests. The reports are
unaltered DayCare research snapshots; their absolute paths are historical.
The earlier 4B training columns in the off report are context from earlier
studies, **not additional runs packaged in this directory**.

## Questions and scoring

The [frozen suite](results/on/suite.json) contains two separately reported cohorts:

- Original 80: 32 natural math, 20 ordinary questions, 16 tool-selection tasks,
  four calculator smoke tasks, and eight supplied-expression diagnostics.
- Audited 52: 24 clear math, eight ambiguous/missing-information questions,
  and 20 ordinary controls. The [question audit](question-audit.json) specifies
  which fact a clarification must request.

The GSM8K-derived items retain their row identifiers; the source dataset is
[OpenAI GSM8K](https://github.com/openai/grade-school-math), distributed under
its [MIT license](https://github.com/openai/grade-school-math/blob/master/LICENSE).
Other controls and prompts were assembled for this study. These questions have
already been examined; they are not a fresh holdout, and pretraining overlap is
unknown. Four original math questions have known ambiguity limitations. We
retain their original primary score and report sensitivity separately.

Final-answer judgments accept equivalent numbers, units, and explanatory prose.
A clarification must actually ask for the missing information without guessing
or calling tools. Truncated/incomplete math responses fail even when an
intermediate number is right. Selection checks allowed proposed tool names,
not execution of blocked OS tools. Ordinary factual correctness is recorded
separately from the criterion that also requires no tool use.

Semantic judgments were made by one coding agent with model labels hidden,
then frozen before unblinding; response style can still reveal a model. They
are not independent human review. Replaying a judgment proves consistency with
that judgment, not its objective correctness. Review rationales are published
so readers can disagree and perform a separate sensitivity analysis.

Statistics use paired questions, not repeated deterministic runs. Small,
previously examined samples and multiple exploratory comparisons do not support
an adoption decision or a broad general-intelligence claim. A zero difference
on this sample does not establish equivalence on future questions.

## Inspect and verify without a GPU

```sh
python3 -m venv .venv
.venv/bin/pip install -r gameterm-thinking/requirements.txt
.venv/bin/python gameterm-thinking/verify.py
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
