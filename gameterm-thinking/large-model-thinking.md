# Thinking enabled in the native GameTerm comparison

The user requested the same two larger models with thinking enabled, following
the [thinking-disabled comparison](large-model-comparison.md). This is inference
evaluation, without training or adoption.

## Frozen comparison

Both existing GGUF artifacts, all 132 questions, all 35 tool definitions, the
system and ledger messages, native calculator execution, sampling settings,
seed, context and 768-token output limit per inference response are retained.
The only request change
is `chat_template_kwargs.enable_thinking: false` to `true`. Each model runs
twice, sequentially, with fresh servers and prompt/RAM caches disabled.

Reasoning uses the same output budget as the final answer. This experiment
therefore measures the thinking toggle under the existing budget, not each
mode's best achievable accuracy with separately tuned settings. Report final
answers, truncation, incomplete turns, tool use and emitted reasoning separately.
No automatic increase in budget is part of this protocol.

The publishers describe broader operating settings than this controlled toggle.
NVIDIA recommends a high output limit (example: 10,000 tokens) when reasoning
is enabled, and documents a separate reasoning budget that reserves space for
the final response. Qwen recommends different sampling settings for thinking
and non-thinking modes. We retain the baseline settings here to isolate the
toggle, so these results must not be presented as optimized thinking-mode
benchmarks. [NVIDIA model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16),
[Qwen model card](https://huggingface.co/Qwen/Qwen3.8-27B).

GameTerm's study driver had hard-coded thinking off. An isolated checkout of
the same `e61521b3` revision, carrying the existing untracked study driver, now
reads the explicit boolean from the captured envelope. The exact first-request
assertion remains enabled. Shipping code and the original checkout are unchanged.
The isolated checkout is `/home/ubuntu/storage/worktrees/gameterm-thinking-study`.

The existing semantic scorer remains authoritative: equivalent answers and prose
are accepted; ordinary factual correctness is separate from unnecessary tool use;
clarification must request the missing fact; selection measures proposed tool
names, not blocked OS execution. Review hides model labels and grades final
answers, not internal reasoning. Freeze judgments before revealing labels.
The reviewer is the same coding agent, not an independent human adjudicator;
response style can also reveal a model despite hidden labels.
Paired SD, SE, bootstrap intervals and exact McNemar comparisons use questions,
never deterministic repetitions, as the sampling units. These are previously
examined questions and exploratory comparisons, not a fresh confirmation set.

## Evidence

Runner: `scripts/thinking_model_comparison.py`.
Runtime root: `/home/ubuntu/storage/daycare-runs/large-model-thinking-001`.
Protocol, suites, baseline scores, envelopes, runner, scorer and driver hashes
are frozen before inference. Each run also hashes model and server binaries.
The original comparison's artifacts and source remain available for verification.

Both models completed two 132-question runs. The review SHA-256 is
`4966cbd6cfde370bea994b0babb10a1e32e0c737aaf7ae8777d2c906103b47d0`.
Reviews began on completed responses while the first pass was still running,
using the same deterministic arm-hidden ordering. Before scoring, every copied
judgment was checked against the final extracted ID, question, expected answer,
text and calls. All judgments were frozen before opening the arm map.

Verification: the dedicated headless target builds and its four live runs
exercise exact request parity; the provider's existing thinking-toggle contract
test passes, as do seven relevant DayCare tests. Size checks pass. GameTerm's
strict Clippy check fails on eight existing unused-import/dead-code warnings in
shipping Linux host code; full checks fail on existing host-test formatting.
These failures are recorded in runtime logs and are not bypassed or claimed fixed.

## Interpreting unfinished responses

The shared provider's existing TH-010 fallback substitutes `reasoning_content`
when the model emitted no final text. Consequently, a harness `completed` event
can contain unfinished reasoning after a length finish. The scorer already
rejects truncated turns; a correct intermediate number in that fallback does
not establish a completed answer. The fallback's diagnostic text still says
`enable_thinking=false` regardless of the requested state. Recorded request JSON
and SSE, not that stale diagnostic string, establish whether thinking was on.
This study does not change the fallback or the shipping provider.

## Results

| Metric | Qwen27 off | Qwen27 on | Nemo30 off | Nemo30 on |
| --- | ---: | ---: | ---: | ---: |
| Original math, 32 | 29 | 29 | 26 | 24 |
| Clear math, 24 | 24 | 24 | 22 | 22 |
| Calculator used on clear math, 24 | 24 | 24 | 1 | 16 |
| Appropriate clarification, 8 | 3 | 3 | 5 | 3 |
| Tool selection under frozen rubric, 16 | 12 | 9 | 5 | 9 |
| Calculator smoke answers, 4 | 4 | 4 | 0 | 2 |
| Supplied-expression answers, 8 | 8 | 8 | 4 | 7 |
| Ordinary target answers, original 20 | 20 | 20 | 19 | 20 |
| Ordinary target answers, clarity 20 | 20 | 20 | 20 | 20 |
| Ordinary answers without tools, each cohort of 20 | 20 | 20 | 14 | 20 |
| Any length finish, all 132 | 2 | 9 | 0 | 20 |

Calculator use on original math increases from 24/32 to 31/32 for Qwen and
1/32 to 8/32 for Nemo. Actual final answers remain the outcome, not activation.
Both enabled models emit reasoning on every question in their first pass.

Every failed original/clear math turn with thinking enabled has a length finish:
three for Qwen and ten for Nemo. This identifies the observed failure condition;
it does not prove that every response would become correct with more tokens.

Nemo fixes its previous duration conversion (`clear-04`, 213 → 203 minutes)
and percentage decrease (`clear-12`, 30% → 25%) errors. The duration correction
uses no tool; the percentage correction uses a real calculator receipt of 25.
But its compound-growth
and discounted-price responses (`clear-16`, `clear-09`) now truncate. Both
contain the right value in unfinished reasoning; neither produces a completed
final answer under the frozen rubric. These two gains and two losses leave
the score at 22/24. More calculator use has not yet increased completed clear
math answers at this budget.

Nemo's large-integer product answer is now correct, but it makes no calculator
call on that item. This fixes the observed final-answer error without proving
better copying of a calculator receipt. Its supplied-expression diagnostic is
more directly encouraging: all eight prompts trigger calculator calls and
seven finish correctly; the remaining expression is cut off mid-JSON and
rejected by the normalizer.

Qwen fixes the 117 + 43 videos case. Its three original-math cutoffs are all
among the previously flagged ambiguous items: walking, stickers and flavors.
Its unchanged 29/32 comprises one gain and one loss, not identical item behavior.
The separate 24 clear questions remain 24/24, already at the ceiling when off.

Tool selection also needs care: the frozen rubric rejects any length finish,
even if some proposed names are appropriate. With thinking on, all seven Nemo
selection failures have a length finish; five of Qwen's seven failures do.
Ignoring truncation and checking only proposed names gives 13/16 for Nemo and
11/16 for Qwen. Those are supplementary name-only counts, not valid-call or
successful-execution scores, and do not replace the primary 9/16 figures.

Some replies recognize missing information without asking for it. Nemo's train
response explicitly says duration is missing but does not request it; Qwen's
language-overlap reasoning recognizes insufficiency but truncates before asking.
Those receive partial labels, not a claim that the ambiguity went unnoticed.
Qwen's cookie response assumes twelve per box before inviting correction, so
it fails the existing no-guessing criterion. Conditional illustrative examples
alongside a real request for the missing fact remain accepted.

Ordinary scores refer to the requested target fact. Review notes flag incorrect
extra explanations (for example, the right helium symbol followed by the wrong
proton count). A 20/20 target score does not mean every sentence is correct and
does not establish broad general intelligence.

## Paired uncertainty, thinking on minus off

| Model / task | Net items | Paired item SD | SE | Bootstrap 95% interval, percentage points | Exact McNemar p |
| --- | ---: | ---: | ---: | --- | ---: |
| Qwen original math | 0/32 | 0.254 | 0.045 | -9.4 to +9.4 | 1.000 |
| Qwen tool selection | -3/16 | 0.403 | 0.101 | -37.5 to 0.0 | 0.250 |
| Qwen clarification | 0/8 | 0.535 | 0.189 | -37.5 to +37.5 | 1.000 |
| Nemo original math | -2/32 | 0.435 | 0.077 | -21.9 to +9.4 | 0.688 |
| Nemo clear math | 0/24 | 0.417 | 0.085 | -16.7 to +16.7 | 1.000 |
| Nemo tool selection | +4/16 | 0.447 | 0.112 | +6.3 to +50.0 | 0.125 |
| Nemo clarification | -2/8 | 0.463 | 0.164 | -62.5 to 0.0 | 0.500 |

Intervals use 100,000 paired bootstrap resamples. Qwen's clear-math indicators
are identical, producing zero empirical paired SD and a degenerate bootstrap
interval; that is not proof of equivalence on future questions. None of the
listed exact tests establishes an improvement or regression.
With few discordant items, the percentile bootstrap can exclude zero while the
exact test does not; we do not select whichever method gives a stronger claim.
The six-item gain
in each Nemo no-tools ordinary cohort has unadjusted p=0.03125; this primarily
measures tool discipline and is exploratory, without multiplicity correction.

Output-token totals, including reasoning and all tool follow-ups, are 14,183 →
46,605 for Qwen and 14,308 → 68,056 for Nemo in pass one. These are measured
token counts, not wall-time or financial cost estimates.

## Reproducibility and conclusion

Final analysis verified all frozen inputs and all four run manifests. Each model
reproduced all 132 final-answer/tool traces exactly, ignoring random call IDs.
Task scores, paired statistics, request counts and output-token totals match
between repetitions. Observed repeat-score SD is zero; the repeats are not extra
independent questions. Every recorded request has thinking enabled and all 35
tools, and every question emits reasoning. Both temporary servers are stopped.

The artifact/model identity and envelope-only toggle checks are retained in
`matched-config-audit.json`. `analysis.json` holds both runs' paired results;
`run-{1,2}-scored.json` and the frozen `review.json` retain decisions and evidence.
Runner/protocol source is committed at `cc08ae8`; frozen source copies and the
isolated GameTerm driver diff are retained with the runtime artifacts.

Thinking changes tool behavior and fixes some individual errors, but does not
increase completed clear-math answers at this budget. The data do not establish
a general improvement or regression. The next bounded experiment should test
an explicitly allocated reasoning/final-answer budget, or a larger output limit
with matched controls. That would be a separate experiment; it has not been run
here and is not assumed to rescue every cutoff. No training, adoption or Air
deployment resulted from this evaluation.
