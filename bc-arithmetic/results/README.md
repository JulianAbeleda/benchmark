# Recorded runs

| Run | Models | Answer format | Notes |
|---|---|---|---|
| [`2026-09-19-first-pass`](2026-09-19-first-pass/) | all three | "digits only" | The wording was a flaw: Qwen3 8B computed 59.97 and 2569.71 with bc and then wrote `ANSWER: 5997` and `ANSWER: 256971`. Three of its four misses with bc are that. |
| [`2026-09-19`](2026-09-19/) | Nemotron 3 Nano 4B, Qwen3 8B | "a plain number such as 1234.56" | Stopped before Qwen3.5 4B ran. This is the wording `run.py` has now. |

Both are one pass per question with sampling on (temperature 0.7).

## What the two passes say together

| Model | In its head | With bc | Seconds per question (head → bc) |
|---|---|---|---|
| Nemotron 3 Nano 4B | 8 of 16, then 13 of 16 | 15 of 16, then 12 of 16 | 3.8 → 2.7, then 3.7 → 4.5 |
| Qwen3 8B | 13 of 16, then 15 of 16 | 12 of 16 (format flaw), then 15 of 16 | 12.0 → 6.6, then 11.7 → 5.3 |
| Qwen3.5 4B | 10 of 16 | 14 of 16 | 14.1 → 4.3 |

**Not settled: whether bc makes the answers more right.** The same model and
condition moved by three to five answers between the passes. That is as large
as the effect being measured. One pass per question cannot rank anything.

**Settled across both passes:**

- The models use the tool when it is offered: Nemotron on 14 of 16 questions
  both times, Qwen3 8B on 16 of 16.
- They write valid `bc` commands for plain arithmetic. No command was refused
  by the safety filter.
- For the two Qwen models, with bc is two to three times faster: one short
  command replaces a long written-out working.
- The easy levels (1 to 3) and very large whole numbers (5) are mostly right
  either way.
- Misses with bc cluster in two places. Level 6, word problems: the setup is
  wrong, or the model writes the command as text and never calls the tool
  (Qwen3.5 4B, both word problems, first pass). Level 8, the traps in `bc`
  itself: `echo "1000003 % 97" | bc -l` prints `.00000000000000000056`, and
  the models believed it. There the calculator misled the model.

**What follows for a calculator tool:** raw `bc` behind a shell tool is not a
clear win for small models, because the tool's own quirks cause errors. A
calculator that takes an expression, handles `mod` correctly whatever the
precision, and returns a tidy number would remove the level 8 misses. Nothing
fixes a word problem that was set up wrong.

## When the model used the tool, was it right?

Pooled over every recorded attempt in both passes (80 attempts with the tool
offered; the model called bc in 73 of them):

| | Right | Share |
|---|---|---|
| The model called bc | 63 of 73 | 86% |
| The same questions in its head | 59 of 80 | 74% |

The ten misses after calling bc:

- 3 were the first pass's "digits only" wording (bc gave the right number and
  the model dropped the decimal point);
- 4 were bc misleading the model (level 8: the remainder under `-l`, the
  fractional power);
- 3 were the model's own, all Nemotron: functions bc does not have
  (`round(...)`, `printf`), the tax added as `+ 0.08` instead of times 1.08,
  and `1.05^10` computed without multiplying by 1000.

Without the wording flaw and without the trap level: 58 of 61, 95%. By model,
when it called bc: Qwen3.5 4B 13 of 13, Qwen3 8B 27 of 32 (every miss the
flaw or a trap), Nemotron 3 Nano 4B 23 of 28.

So: when a model uses a tool and the tool's output is sound, it is right about
95% of the time. What is left is the tool misleading it (fixable in the tool),
the model handing the tool the wrong input (not fixable by the tool), and the
model not calling the tool at all (7 of 80 here; the tool's description is
the lever).

## Not done yet

1. **Repeats.** Ask every question at least three times per condition and
   report the share that is right. Without this the accuracy numbers above
   are noise. `report.py` already reads a `repeats` field and an `attempt`
   per row; `run.py` does not write them yet.
2. **Qwen3.5 4B with the corrected wording**, and the two 9B models once
   they are downloaded.
3. **The same questions inside GameTerm's real prompt** (about 10,000
   characters of system text and 34 tools). With the short prompt used here
   Qwen3 8B gets 15 of 16 in its head; inside GameTerm it answers "3." to
   "2 plus 2". The prompt, not the arithmetic, is the larger variable.
4. **A third condition: a purpose-built calculator tool** in place of `bash`
   plus a hint, to measure what the tidy layer is worth.
5. **`osascript` as the engine**, against `bc`. Measured by hand on
   2026-09-19: `osascript` is cleaner on small results (`0.3`, `2.5`, does
   `2 ^ 0.5` and `17 mod 5` correctly) and loses digits on large whole
   numbers (`1.21932631112635E+17`), where `bc` is exact. It is also a whole
   scripting language, so an expression must be checked before it is run.
