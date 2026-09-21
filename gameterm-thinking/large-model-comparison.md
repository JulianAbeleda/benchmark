# Larger-model extension of the GameTerm comparison

The user requested the installed 27B Qwen as another comparator, and a download
of the relevant larger Nemotron. This is evaluation only, following the stopped
[small clarification training pilot](clarification-sft-pilot.md).

## Artifacts and limits

- **Qwen3.8-27B**, installed `Qwen3.8-27B-Q4_K_M.gguf`, explicitly selected by the
  user. Local GGUF identifies `Qwen3.8-27B`, architecture `qwen35`, size `27B`,
  file type 15. The separate Uncensored and Huihui abliterated files are not used.
  The installed artifact is hashed; an upstream download checksum for that
  existing file has not been independently established.
  Local SHA-256: `31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34`.
  [Official model card](https://huggingface.co/Qwen/Qwen3.8-27B).
- **NVIDIA Nemotron 3 Nano 30B-A3B**, post-trained model, downloaded in Q4_K_M
  from ggml-org, revision `f9d9b441a049bf27473c3cdd9cec220f5657b862`.
  Expected 22,421,827,488 bytes, SHA-256
  `0f111a0d49777a2a0178758b1aee14e5365c495987499401ef3ebe87754322a8`.
  The official card specifies 30B total parameters and 3.5B active per token.
  [NVIDIA model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16),
  [GGUF publisher](https://huggingface.co/ggml-org/NVIDIA-Nemotron-3-Nano-30B-A3B-GGUF/tree/f9d9b441a049bf27473c3cdd9cec220f5657b862).

The earlier small Qwen was **Qwen3.5-4B**. The new Qwen comparison changes model
version as well as size. Nemotron 30B is mixture-of-experts; comparing its total
size with dense Qwen 27B is not equalizing active compute. Neither comparison
isolates a causal parameter-count effect or a DayCare training effect.

## Frozen protocol

Runtime artifacts: `/home/ubuntu/storage/daycare-runs/large-model-comparison-001`.
Runner: `scripts/large_model_comparison.py`; semantic review:
`scripts/large_model_review.py`.

The unchanged earlier suites are concatenated with namespaced IDs:

- Original 80: 32 natural math, 20 ordinary questions, 16 tool selection,
  four calculator smoke prompts, eight supplied-expression diagnostics.
- Quality-audited 52: 24 clear math, eight missing-information/ambiguous tasks,
  20 ordinary questions.

Report the two cohorts separately. The original 32-question math set retains
its earlier rubric and known ambiguity limitations; it is not rewritten to
make the new models look better or worse. Both suites are previously examined
questions, not a fresh confirmation holdout.

Both new models run twice with fresh servers, identical requests except model
identity and tokenizer-specific punctuation bans, all 35 native tools, thinking
false, temperature zero, seed 42, max output 768, context 16,384, one slot,
and prompt/RAM caches disabled. Token bans are derived from the actual running
model using the same singleton-probe rule as GameTerm. Existing native driver
asserts first-request parity and records subsequent requests, SSE, tool calls,
actual calculator receipts, and final outcomes. OS actions remain blocked.

Semantic final-answer review hides model labels; equivalent answers, units and
explanatory prose are accepted. Targeted clarification must request the missing
fact without guessing or tool execution. Incomplete/truncated numerical replies
fail. Tool selection assesses proposed allowed names, not successful OS action.
Paired item SD, SE, bootstrap confidence intervals and exact McNemar comparisons
are retained. Deterministic repeats are not independent samples. The reviewer is
the same coding agent, not independent human adjudication.

The Nemotron download completed and matches the publisher's size and SHA-256.
Inference uses the runner at commit `5cb45bd`; copies of the runner, reviewer,
and GameTerm driver are retained in the runtime `frozen-source/` directory.
All 264 first-pass semantic judgments were frozen before revealing the arm map
(review SHA-256 `fbfa98fdd921464d13056ac6cee5914a7f0a6df75555c24f49c33f90b7b81442`).

## Results

These are descriptive results on the existing questions, not a fresh holdout.
Earlier columns come from the retained original runs, not new inference.
The trained 4B column is the earlier calculator adapter, not the rejected
clarification-training pilot.

| Task | Original Nemo 4B | Calculator-trained Nemo 4B | Qwen3.5-4B | Qwen3.8-27B | Nemo 30B-A3B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original math, 32 | 24 | 23 | 26 | 29 | 26 |
| Clear math, 24 | 22 | 22 | 24 | 24 | 22 |
| Requests missing information, 8 | 0 | 0 | 2 | 3 | 5 |
| Tool selection, 16 | 5 | 12 | 15 | 12 | 5 |
| Calculator smoke, 4 | 4 | 4 | 4 | 4 | 0 |
| Supplied-expression diagnostics, 8 | 8 | 8 | 8 | 8 | 4 |
| Ordinary target answers, original 20 | 20 | 20 | 20 | 20 | 19 |
| Ordinary target answers, clarity 20 | 20 | 20 | 20 | 20 | 20 |

The frozen retention criterion additionally requires **no tools** for ordinary
questions. Nemo 30B satisfies that combined criterion on 14/20 in each cohort;
the other models score 20/20. The new reviewer exposes factual correctness and
tool use separately without changing the frozen success criterion or any
semantic judgment. Calling 14/20 its factual accuracy would be misleading.
One missing answer was a Lisbon question routed to web search, which waits for
approval in this fixture. Other unnecessary actions included `update_plan` and
unrelated calculations. Correct target facts can coexist with incorrect extra
prose: the review flags two incidental factual errors. These short questions do
not establish broad general intelligence or its retention.

On original math, Qwen27 used the calculator on 24/32 questions and Nemo30 on
1/32. On clear math the counts were 24/24 and 1/24. Merely increasing model
size did not reliably produce calculator use in this configuration.

## Trace-level failure evidence

- **Correct execution, incorrect reporting:** Nemo30's `main::smoke-1-natural`
  calls `calculate` with `123456789 * 987654321`. The actual successful receipt
  is `121932631112635269`. Its final answer is `1219326311126352689`, with an
  extra digit. This is an observed failure to preserve the tool result, not a
  missing calculator, schema error, or grading rejection of separators.
- **No tool, bad arithmetic and truncation:** Qwen27's `main::gsm8k-3030`
  derives Ekon's 117 videos correctly, but repeatedly claims 117 + 43 = 162
  instead of 160, without calling the calculator, until the token limit.
- **Clarification is present but inconsistent:** both models ask for the
  missing cookie count, duration, and width. Nemo30 also asks for the missing
  tax rate and exchange rate. Neither meets the target on all eight questions.
  Recognition of ambiguity without an actual clarification question does not
  automatically pass.

These traces identify where behavior fails. They do not establish why the
weights produce it. Model family, quantization, native template, penalties,
the 768-token limit and disabled thinking are part of this configuration;
none is isolated by this comparison. A targeted fix should distinguish tool
selection, expression construction, and faithful use of the returned result.

## Uncertainty

The following paired comparisons are Qwen27 minus Nemo30 on the same items.
SD is the sample standard deviation of item differences in {-1, 0, 1}; it is
not variation between repeated runs. Confidence intervals are 100,000-resample
paired percentile bootstrap intervals. Exact McNemar p-values are two-sided.

| Task | Net items | Paired SD | SE | 95% interval, percentage points | Exact p |
| --- | ---: | ---: | ---: | --- | ---: |
| Original math | +3/32 | 0.390 | 0.069 | -3.1 to +21.9 | 0.375 |
| Clear math | +2/24 | 0.282 | 0.058 | 0.0 to +20.8 | 0.500 |
| Missing-information clarification | -2/8 | 0.463 | 0.164 | -62.5 to 0.0 | 0.500 |
| Tool selection | +7/16 | 0.512 | 0.128 | +18.8 to +68.8 | 0.0156 |

Tool selection shows a larger descriptive separation here. These are exploratory
comparisons across multiple tasks and models, with no multiplicity correction;
they are not an adoption test. The math and clarification differences do not
establish reliable superiority. Removing the four already flagged ambiguous
original math items gives 27/28 for Qwen27 and 25/28 for Nemo30; this sensitivity
check does not replace the frozen original score. Prefer the separate 24-item
clear cohort when discussing unambiguous math.

Both models completed two 132-question runs. Each repeat uses the frozen
first-pass judgments only if its answer is identical; any changed answer
requires a fresh review. The final audit also compares tool arguments, receipts,
completion and truncation, ignoring random call IDs.

**Final verification:** all 132 answer/tool traces matched between repeats for
each model. Task scores and paired statistics were identical, so observed
between-repeat score SD is zero; this is deterministic reproducibility, not
zero uncertainty about future questions. All manifest hashes verified.
The wire audit checked 215 requests per Qwen run and 177 per Nemo run: every
request exposed 35 tools with thinking false, and no nonempty reasoning chunks
were emitted. All four native harness runs completed, six relevant scoring tests
passed, repository size and diff checks passed, and temporary servers stopped.

The reproducible analysis entry point is `python3 scripts/large_model_review.py
analyze`, with the recorded runtime artifacts present. `analysis.json` contains
per-task summaries and paired comparisons with all three earlier models;
`run-{1,2}-scored.json` retains per-item decisions, and `wire-audit.json` retains
request counts and repeat differences. Runtime data and model weights are kept
outside Git. The old original math ambiguity audit and the clearer cohort remain
separate; neither the questions nor answers were used for new training here.

The subsequent [thinking-enabled comparison](large-model-thinking.md) changes
only the requested thinking mode at the same output limit and reports paired
within-model changes, including truncation and unnecessary tool use.
