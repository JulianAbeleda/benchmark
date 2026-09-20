# gameterm-calculate

**Question.** Inside a real assistant app, with its long prompt and 35 tools,
does a small local model use a calculator tool when told to, and is the answer
it then gives the person right?

This is the follow-up to [`bc-arithmetic`](../bc-arithmetic/), which showed
that a model that calls a sound calculator is right about 95 percent of the
time, and that most misses came from the calculator (`bc`'s own traps), not
from the model.

## Setup

- The app is GameTerm, a desktop assistant that runs a local model through
  `llama-server` (thinking off, temperature 0.7). Its prompt is about 10,000
  characters plus a permission record, and it offers 35 tools.
- The tool is `calculate(expression, decimals?)`. The engine behind it is
  [`fend-core`](https://github.com/printfn/fend) (MIT), compiled into the app.
  The tool answers exactly what it was asked: nothing is rewritten, so
  `24.50 - 20%` is 24.3, because `20%` is 0.2. Its description says so, and
  says how to write a discount.
- The questions are the sixteen of `bc-arithmetic`, in the same order, all in
  one conversation. In front of each: *"Use the calculate tool for this. Do
  not work it out yourself."*
- The app shows its own line for every call (`expression = result`), so the
  person sees the true number whatever the model then says.
- A reply is read in digits and in words, because the app's character speaks
  numbers ("Seventeen thousand, five hundred thirty-two").

The test is driven by `scripts/smoke-calculate.py` in the app's repository
(`--questions benchmark --say "..."`), which is not public. The recorded
results are here.

## Results, 2026-09-20

| Model | Called the tool | Tool result right | Reply to the person right |
|---|---|---|---|
| Qwen3 8B | 16 of 16 | 16 of 16 | 16 of 16 |
| Qwen3.5 4B | 16 of 16 | 16 of 16 | 14 of 16 |
| Nemotron 3 Nano 4B, easy questions first | 0 of 16 | none | refused all sixteen |
| Nemotron 3 Nano 4B, hardest first (8 questions) | 6 of 8 | 6 of 6 | 7 of 8 |

No approval card appeared in any run: the tool reads nothing and changes
nothing.

## What it shows

1. **When a model called the tool, the tool's result was right every time:
   38 of 38.** That includes the two questions `bc` gets wrong (a remainder
   under `bc -l`, a fractional power) and an 18-digit product.
2. **Every wrong reply came from something the model did in its head, after
   or instead of the tool.** Qwen3.5 4B got the right digits from the tool
   for 2^40 and for 123456789 × 987654321 and then said them wrong in words
   ("One trillion, nine-hundred ninety-five billion ..."). Nemotron skipped
   the tool on the discount-and-tax problem and gave a wrong total.
3. **The first turn sets the tone of a conversation.** Asked "2 plus 2"
   first, Nemotron answered "I don't have a calculator tool" (the tool was in
   the list it was sent: 35 tools, `calculate` eleventh) and then repeated
   that for the fifteen questions after it. The same model, asked the hardest
   questions first, called the tool six times of eight. A small model treats
   its own earlier statement as a fact.
4. **Both Qwen models wrote percent the way the tool's description teaches**,
   for example `3 * (24.50 * (1 - 20%) + 24.50 * (1 - 20%) * 8%)`, and used
   the `decimals` input for rounding without being told to in the question.

## Limits

One pass per question, with sampling on. The totals are small. The easy-first
and hardest-first Nemotron runs differ in length as well as order.
