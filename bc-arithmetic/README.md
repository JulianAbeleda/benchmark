# bc-arithmetic

**Question.** Small local models get sums wrong in their head. If a model may
call `bc`, how many more answers are right, how well does it write the `bc`
command, and what does the extra step cost in time?

## What the test does

For each model it starts `llama-server` the way GameTerm does (thinking off,
GameTerm's sampling settings, q8_0 cache) and asks 16 questions in 8 levels of
rising difficulty, twice:

1. **In its head.** No tool.
2. **With bc.** A `bash` tool is offered, with a hint to use `bc` for every
   calculation. The model may call it up to five times per question.

Every question has one exact answer. The model is asked to end with
`ANSWER: <number>`; that number is compared with the answer key.

| Level | What it tests | Example |
|---|---|---|
| 1 | one small operation | 2 plus 2 |
| 2 | several digits | 487 times 36 |
| 3 | decimals and percent | 15 percent of 80 |
| 4 | brackets, averages, rounding | (1499 times 12) divided by 7 |
| 5 | very large whole numbers | 123456789 times 987654321 |
| 6 | word problems with several steps | discount, then tax, times three |
| 7 | square roots | hypotenuse of 5 and 12 |
| 8 | traps in `bc` itself | remainder under `bc -l`, a fractional power |

Level 8 is there on purpose. `bc -l` answers `17 % 5` with `0`, because `-l`
sets twenty decimals and the remainder is taken after that division. And `bc`
refuses `2 ^ 0.5`; the way round is `sqrt(2)` or `e(l(2) * 0.5)`.

## Safety

The model writes shell commands, so the test never hands them to a shell. It
accepts only three shapes (`echo "<expr>" | bc [-l]`, `echo <expr> | bc [-l]`,
`bc [-l] <<< "<expr>"`), checks that the expression holds only digits,
operators and lower-case letters, and gives it to `/usr/bin/bc` on standard
input. Anything else is answered with "refused", and the model sees that.

## Run it

```
python3.12 bc-arithmetic/run.py                      # every model under the Arkey root
python3.12 bc-arithmetic/run.py qwen3.5-4b qwen3-8b  # chosen models
python3.12 bc-arithmetic/run.py --run 2026-10-01-after-prompt-change
python3.12 bc-arithmetic/report.py results/<run name>
```

About six minutes per model on a 16 GB M-series Air.

## Reading the results

One question is asked once per condition, with sampling on, so a single cell
can flip between runs. Read the totals and the pattern by level, not one cell.
A refused command counts against the model: GameTerm would refuse it too.

## Runs

See [`results/`](results/). Each run folder has a `README.md` summary.
