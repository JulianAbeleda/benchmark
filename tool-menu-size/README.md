# tool-menu-size

**Question.** How many tools can a small local model see before it starts
picking the wrong one? Is there a number to cap the menu at?

## What the literature offers

There is no universal number. There is a fair way to compare menu sizes:
*Bits-over-Random*, `BoR = log2(P_observed / P_random)`, where for one right
tool in a menu of K out of N, `P_random = K / N`
([arXiv 2605.24660](https://arxiv.org/abs/2605.24660)). It corrects for a
larger menu containing the right tool more often by luck, and it is a measure
for the step that *chooses* the menu. For the model's own choosing, the
honest answer is to measure the curve on the models and tools in question.

## What the test does

Twenty-one requests (three for each of six "gold" tools, three that need no
tool), each asked twice, with 6, 12, 20 and 35 tools on the menu. The gold
tools are always there; each larger menu adds the most similar tools first.
Within a menu size the tool list is identical for every request, in a fixed
shuffled order, so the engine's prompt cache holds it. Short system prompt,
thinking off, temperature 0.7.

The tool definitions are a real desktop assistant's. They are read from a
local file that is not in this repository; the results name the tools only.

## Result, 2026-09-20 (fair scoring, of 42 attempts)

| Tools shown | Qwen3 8B | Qwen3.5 4B | Nemotron 3 Nano 4B | Prompt tokens |
|---|---|---|---|---|
| 6 | 42 | 42 | 31 | ~1,300 |
| 12 | 42 | 42 | 37 | ~2,300 |
| 20 | 42 | 42 | 40 | ~3,700 |
| 35 | 42 | 41 | 39 | ~6,300 to 7,400 |

## What it shows

1. **The count was not the problem.** With 35 tools on the menu neither Qwen
   model once picked a tool from the wrong area. There is no accuracy knee in
   this range to cap the menu at.
2. **Strict scoring misleads.** Scored strictly the Qwen models "drop" from
   42 to about 30 of 42 the moment lookup tools appear, because they then
   list apps or windows before acting, which is what the tools' own
   descriptions ask for. That is a first step, not a wrong pick.
3. **The weak model did better with more tools.** Nemotron's misses at six
   tools were mostly *no tool call at all* (9 of 11). Given lookup tools it
   had a first step it was willing to take, and it rose to 40 of 42.
4. **The cost of a long menu is tokens.** The 35 definitions are about 6,300
   tokens, five times the six-tool menu. That is paid in the first read after
   a start, in context room, and in whatever a long prompt does to a small
   model's attention, which this short-prompt test does not measure.

## Limits

Single requests under a short system prompt. Inside the real application the
same tools sit on top of several thousand more tokens of instructions and a
growing conversation, and that is where the errors that prompted this test
were seen. This test says the models *can* choose among 35 tools; it does not
say 35 tools are free.

## Run it

```
python3.12 tool-menu-size/run.py [models...] [--tools FILE] [--sizes 6 12 20 35] [--repeats 2]
python3.12 tool-menu-size/report.py results/<run name>
```
