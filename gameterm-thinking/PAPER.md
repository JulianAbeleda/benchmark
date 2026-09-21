# Calculator access, LoRA adaptation, and thinking in a native assistant harness

**Exploratory research report · September 2026 · GameTerm / DayCare**
Status: reproducible local experiment record, not a peer-reviewed paper.

[Model identities and test design](details/models-and-tests.md) ·
[Every question and response](details/README.md) ·
[Training method and artifact formats](training/README.md) ·
[Reproduction instructions](README.md#inspect-and-verify-without-a-gpu)

## Abstract

We examine whether calculator use corresponds to better completed answers in
GameTerm's native assistant harness. An earlier comparison evaluated original
and calculator-adapted Nemotron 3 Nano 4B alongside Qwen3.5-4B. A subsequent
experiment evaluated the installed Qwen3.8-27B and NVIDIA Nemotron 3 Nano
30B-A3B with thinking disabled and enabled. All artifacts used Q4_K_M for
these inference comparisons. The shared evaluation contains 132 questions in
two cohorts, with separate math, clarification, tool-selection, and ordinary
answer outcomes. Two deterministic repeats are retained per condition.

On 24 clear math questions, original and trained Nemo4B both scored 22/24,
while calculator use rose from 4/24 to 24/24. For Nemo30, enabling thinking
increased calculator use from 1/24 to 16/24 but retained 22/24 accuracy: two
answers improved and two previously correct answers were truncated. Qwen27
scored 24/24 in both thinking modes. Reasoning shared a 768-token response
budget. These selected, previously examined questions support descriptive
behavioral findings, not a general accuracy improvement, regression, or
adoption claim. The appendix exposes all 132 prompts and 1,848 recorded
responses, including tool arguments, receipts and failures.

## 1. Research questions

1. Does supervised calculator adaptation change tool use and final-answer success?
2. Does enabling thinking change those outcomes under a matched output budget?
3. Where do failures occur: choosing a tool, constructing an expression,
   executing it, requesting missing information, or reporting its result?

The experiments have different interventions. The earlier original-versus-trained
4B comparison includes accumulated adapter changes. The larger-model experiment
has no DayCare training intervention and isolates the thinking request flag
within each model under fixed settings. Comparing model families or Qwen
versions does not isolate a size effect.

## 2. Related work

LoRA freezes base weights and learns low-rank updates, the adaptation mechanism
used here. Our narrow final-block placement is an implementation choice, not a
claim that this placement is optimal. [Hu et al., 2021](https://arxiv.org/abs/2106.09685).

Toolformer studies learning when to call APIs and how to incorporate returned
results. It motivates evaluating useful downstream behavior rather than call
syntax alone. Our externally verified supervised labels do not reproduce its
self-supervised data-generation procedure. [Schick et al., 2023](https://arxiv.org/abs/2302.04761).

ToRA studies mathematical problem solving with tool-integrated trajectories.
Our paired call/receipt/answer examples share the goal of teaching result use,
but differ in tool language, model, training scale, and disabled-thinking
format. Its results are not expected-effect estimates for this study.
[Gou et al., 2023](https://arxiv.org/abs/2309.17452).

We report paired tests because model conditions answer the same questions.
Statistical test selection must reflect the experimental design; repeating a
deterministic answer does not create another independent item.
[Dror et al., 2018](https://aclanthology.org/P18-1128/).

## 3. Models and training

The larger Qwen was **Qwen3.8-27B Q4_K_M**, identified by its installed filename
and GGUF metadata. The smaller Qwen was **Qwen3.5-4B Q4_K_M**. The larger
Nemotron was **NVIDIA Nemotron 3 Nano 30B-A3B Q4_K_M**. The earlier Nemotron
variants were original and calculator-trained **Nemotron 3 Nano 4B** exports.
Full filenames, hashes, provenance qualifications and condition labels are in
[Table: model identities](details/models-and-tests.md).

The 4B calculator continuation used DayCare/tinygrad LoRA: rank 4, alpha 8,
learning rate 5e-5, three epochs, 112 examples and 336 updates. Only the final
block's feed-forward up/down projections were adapted. Thirty-two independent
GSM8K training questions each contributed a call target and an answer target
conditioned on a real calculator receipt. Thirty-two ordinary and sixteen
other-tool replay examples were mixed throughout training. The ordinary quota
is a local policy, not a threshold established by the cited papers.

The [training appendix](training/README.md) publishes the actual dataset,
configuration, per-update losses, verification records and historical trainer
source. It also distinguishes the historical NPZ/JSON artifacts from DayCare's
XML format and documents the later lossless XML integration. A storage-format
fix is not a new training result.

The original training spending gate failed under its earlier restrictive
wording and 160-token configuration. Later natural-wording evaluation changed
the measurement conditions; it did not retroactively pass that gate. The 4B
comparison here is against the original model after accumulated adaptation,
not a controlled estimate of the last continuation's effect alone.

## 4. Evaluation methods

### 4.1 Questions

The original cohort contains 32 natural math, 20 ordinary, 16 tool-selection,
four smoke, and eight supplied-expression questions. The audited cohort
contains 24 clear math, eight clarification, and 20 ordinary questions.
[Every exact prompt, key and response is linked individually](details/README.md).
Known ambiguity in four original math items is retained in the primary record;
a separate sensitivity analysis is described in the original report. No item
was silently rewritten to improve a score. These are previously examined
questions, not a new confirmation holdout. Pretraining contamination is unknown.

### 4.2 Runtime

Inference ran through GameTerm's shared coordinator, harness, provider,
normalizer and real `fend` calculator, with all 35 tool schemas. OS actions and
unavailable external providers were blocked fixtures. Exact first-request JSON
parity was asserted. This reproduces the shared backend loop, not the entire
Mac UI or all external tool effects.

The larger-model toggle retained temperature 0, seed 42, context 16,384, one
server slot, disabled prompt/RAM caches, native templates, model-specific
punctuation bans, and 768 output tokens per inference response. Only
`enable_thinking` changed within a model. This is not a comparison of separately
optimized publisher settings. Both models ran sequentially on an RTX 5090
32 GB, twice per setting. The larger runs repeated their answers and tool
traces exactly after excluding random call IDs.

### 4.3 Scoring and uncertainty

Final semantic answers accept equivalent numeric forms, units and prose.
Merely mentioning the right number in unfinished reasoning does not pass.
Clarification must request the missing fact without guessing or using tools.
Tool-selection success concerns allowed proposed names, not execution of
blocked actions. Ordinary target correctness and unnecessary tool use are
separate fields. A correct target can coexist with an erroneous extra sentence;
review notes preserve these cases.

One coding agent reviewed responses with model labels hidden and froze
judgments before unblinding. Style may reveal identity; this is not independent
human adjudication. Published rationales permit independent reassessment.

For paired binary outcomes, we report gains/losses, sample SD of item differences
in {-1,0,1}, SE, 100,000-resample percentile bootstrap intervals, and exact
two-sided McNemar p-values. Repeats do not increase n. These exploratory
comparisons have no multiplicity correction. Degenerate intervals on unchanged
items do not establish population equivalence.

## 5. Results

### 5.1 Earlier 4B comparison, thinking disabled

| Outcome | Original Nemo4B | Trained Nemo4B | Qwen3.5-4B |
|---|---:|---:|---:|
| Original math correct, /32 | 24 | 23 | 26 |
| Clear math correct, /24 | 22 | 22 | 24 |
| Calculator used on clear math, /24 | 4 | 24 | 18 |
| Appropriate clarification, /8 | 0 | 0 | 2 |
| Tool selection, /16 | 5 | 12 | 15 |

The increased call frequency does not establish improved end-to-end accuracy.
These rows describe earlier runs, not additional thinking-toggle conditions.
Their scored records and raw traces are in [the earlier-run archive](results/earlier-4b/).

### 5.2 Larger models, matched thinking toggle

| Outcome | Qwen27 off | Qwen27 on | Nemo30 off | Nemo30 on |
|---|---:|---:|---:|---:|
| Original math correct, /32 | 29 | 29 | 26 | 24 |
| Clear math correct, /24 | 24 | 24 | 22 | 22 |
| Calculator used on clear math, /24 | 24 | 24 | 1 | 16 |
| Appropriate clarification, /8 | 3 | 3 | 5 | 3 |
| Tool selection, /16 | 12 | 9 | 5 | 9 |
| Ordinary answers without tools, /20 in each cohort | 20 | 20 | 14 | 20 |
| Any output cutoff, /132 | 2 | 9 | 0 | 20 |

For Nemo30 clear math, thinking produced two gains and two losses: paired
SD 0.417, SE 0.085, 95% bootstrap interval −16.7 to +16.7 percentage points,
exact p=1.0. Its original-math change was −2/32, SD 0.435, SE 0.077, interval
−21.9 to +9.4 points, exact p=0.6875. These do not establish a reliable accuracy
change. Full per-task statistics are in the [thinking report](large-model-thinking.md)
and [machine-readable analysis](results/on/analysis.json).

### 5.3 Failure evidence

The [large-product trace](details/questions/main--smoke-1-natural.md) shows
Nemo30 with thinking off receiving the correct calculator product and then
copying it incorrectly. The tool executed correctly; final reporting failed.

In the clear cohort, thinking corrected Nemo30's duration and percentage-decrease
answers but introduced cutoffs on compound growth and discounted/taxed price.
See [duration](details/questions/clarify--clear-04.md),
[percentage decrease](details/questions/clarify--clear-12.md),
[compound growth](details/questions/clarify--clear-16.md), and
[discount/tax](details/questions/clarify--clear-09.md).
Every failed original/clear math turn in the larger thinking runs involved a
length finish. Some contained a correct intermediate value but no completed
answer. The provider's reasoning-as-final fallback makes cutoff inspection
necessary even when a harness completion event exists.

## 6. Limitations

This is a small, exploratory, one-training-seed sequence of experiments on
selected prompts. It cannot estimate training-seed variance or broad capability
retention. Model families, active compute, quantization, native templates and
Qwen versions differ. The installed Qwen27 artifact lacks an independently
verified upstream checksum. The shared 768-token limit constrains thinking;
more room is plausible to test, not a demonstrated remedy. The historical
server binary has an exact hash but no fully reconstructed clean build recipe.
Human-independent semantic review and fresh confirmation data remain absent.

## 7. Conclusion and next experiment

Calculator access, calculator activation, and a correct final answer are
separate outcomes. These observations show changes in activation without a
reliable demonstrated clear-math gain. The next bounded test should freeze a
larger or explicitly divided reasoning/final-answer budget, retain the same
harness and scoring, and report expression correctness, execution success and
faithful final reporting separately. Such a test has not been run in this report.

## Data and code availability

The [question appendix](details/README.md) presents every recorded response;
compressed archives retain the original requests, streams and events. The
[replay command](README.md#inspect-and-verify-without-a-gpu) verifies the original
larger-model scores without a GPU. Earlier 4B records are checked against their
raw traces by `verify_additional.py`. `build_details.py --check` verifies that
rendered question pages exactly match the evidence. Training metadata is
published separately from model weights. XML conversion evidence is explicitly
identified as post-training, preserving the historical source hashes.
