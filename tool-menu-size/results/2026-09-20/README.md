# Tool menu size, run 2026-09-20

Attempts whose first tool call was right. *Strict*: only the tool that does the job counts. *Fair*: a lookup first (listing apps or windows before acting on them) counts too.

| Model | Tools shown | Prompt tokens | Strict | Fair | Wrong tool | No tool call | Needless call |
|---|---|---|---|---|---|---|---|
| nemotron-3-nano-4b | 6 | 1525 | 31 of 42 | 31 of 42 | 2 | 9 | 0 |
| nemotron-3-nano-4b | 12 | 2572 | 29 of 42 | 37 of 42 | 1 | 4 | 0 |
| nemotron-3-nano-4b | 20 | 4124 | 27 of 42 | 40 of 42 | 0 | 2 | 0 |
| nemotron-3-nano-4b | 35 | 7418 | 26 of 42 | 39 of 42 | 1 | 2 | 0 |
| qwen3-8b | 6 | 1217 | 42 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3-8b | 12 | 2103 | 36 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3-8b | 20 | 3427 | 35 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3-8b | 35 | 6268 | 39 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3.5-4b | 6 | 1343 | 42 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3.5-4b | 12 | 2235 | 30 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3.5-4b | 20 | 3567 | 30 of 42 | 42 of 42 | 0 | 0 | 0 |
| qwen3.5-4b | 35 | 6423 | 29 of 42 | 41 of 42 | 0 | 1 | 0 |
