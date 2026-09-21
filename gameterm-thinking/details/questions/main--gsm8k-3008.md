# main::gsm8k-3008

[All questions](../README.md) · [Models and test design](../models-and-tests.md)

Cohort: `main`. Task: `math`.

## Exact question

```text
A snake's head is one-tenth its length. If a snake is 10 feet long, calculate the length of the rest of its body minus the head.
```

## Frozen expected answer / allowed tool names

```text
"9"
```

## Recorded responses

The text below is the harness-delivered response, not a cleaned-up answer. When a response was cut off, the provider may have substituted unfinished reasoning for final text. The cutoff and completion flags remain visible. Empty output is explicitly marked.

### Qwen3.8-27B (Q4_K_M) — thinking off, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The head is one-tenth of the snake, so it's 1 foot. The rest of its body minus the head means everything except that head: (1 - 1/10) × 10 = **9 feet**.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"(1 - 1/10) * 10\"}",
      "call_id": "KkFeOHstU0AlvdhNlEapLZrWKahQNXjZ",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "KkFeOHstU0AlvdhNlEapLZrWKahQNXjZ",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "(1 - 1/10) * 10 = 9",
      "status": "Succeeded"
    }
  ]
}
```

**Frozen review rationale:**

```text
Final stated answer agrees with the frozen answer; explanations and equivalent units accepted.
```

[Scored source](../../results/off/run-1-scored.json) · [Raw requests, SSE and events](../../results/off/qwen27-run-1/candidate.tar.gz)

### Qwen3.8-27B (Q4_K_M) — thinking off, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The head is one-tenth of the snake, so it's 1 foot. The rest of its body minus the head means everything except that head: (1 - 1/10) × 10 = **9 feet**.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"(1 - 1/10) * 10\"}",
      "call_id": "Vc7qBCjIKijuldr5sPtJsVUSFPsEUTUS",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "Vc7qBCjIKijuldr5sPtJsVUSFPsEUTUS",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "(1 - 1/10) * 10 = 9",
      "status": "Succeeded"
    }
  ]
}
```

**Frozen review rationale:**

```text
Final stated answer agrees with the frozen answer; explanations and equivalent units accepted.
```

[Scored source](../../results/off/run-2-scored.json) · [Raw requests, SSE and events](../../results/off/qwen27-run-2/candidate.tar.gz)

### Qwen3.8-27B (Q4_K_M) — thinking on, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The head takes up one-tenth of the snake, so on a 10-foot snake it's 1 foot long (10 ÷ 10). Take that off the full length and you get:

**9 feet.**
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"10 - 10 / 10\"}",
      "call_id": "MFqHSuOWqzq51SJ7XbgkLsynHY5tQpuD",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "MFqHSuOWqzq51SJ7XbgkLsynHY5tQpuD",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "10 - 10 / 10 = 9",
      "status": "Succeeded"
    }
  ]
}
```

**Frozen review rationale:**

```text
Final task answer equals the frozen value; prose and equivalent number words accepted.
```

[Scored source](../../results/on/run-1-scored.json) · [Raw requests, SSE and events](../../results/on/qwen27-run-1/candidate.tar.gz)

### Qwen3.8-27B (Q4_K_M) — thinking on, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The head takes up one-tenth of the snake, so on a 10-foot snake it's 1 foot long (10 ÷ 10). Take that off the full length and you get:

**9 feet.**
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"10 - 10 / 10\"}",
      "call_id": "IjfK9z1JS32Z08T1trP4HSQYRskBalIj",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "IjfK9z1JS32Z08T1trP4HSQYRskBalIj",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "10 - 10 / 10 = 9",
      "status": "Succeeded"
    }
  ]
}
```

**Frozen review rationale:**

```text
Final task answer equals the frozen value; prose and equivalent number words accepted.
```

[Scored source](../../results/on/run-2-scored.json) · [Raw requests, SSE and events](../../results/on/qwen27-run-2/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking off, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The whole snake measures ten feet.

Its head makes up exactly one‑tenth of that total:

\[
\text{head length}= \frac{1}{10}\times 10\ \text{ft}=1\ \text{ft}
\]

To find the length of everything else, subtract the head from the whole body:

\[
\text{tail+rest}=10\ \text{ft}-1\ \text{ft}=9\ \text{ft}
\]

So the part of the snake that isn’t its head is **nine feet long**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

**Frozen review rationale:**

```text
Final stated answer agrees with the frozen answer; explanations and equivalent units accepted.
```

[Scored source](../../results/off/run-1-scored.json) · [Raw requests, SSE and events](../../results/off/nemo30-run-1/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking off, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The whole snake measures ten feet.

Its head makes up exactly one‑tenth of that total:

\[
\text{head length}= \frac{1}{10}\times 10\ \text{ft}=1\ \text{ft}
\]

To find the length of everything else, subtract the head from the whole body:

\[
\text{tail+rest}=10\ \text{ft}-1\ \text{ft}=9\ \text{ft}
\]

So the part of the snake that isn’t its head is **nine feet long**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

**Frozen review rationale:**

```text
Final stated answer agrees with the frozen answer; explanations and equivalent units accepted.
```

[Scored source](../../results/off/run-2-scored.json) · [Raw requests, SSE and events](../../results/off/nemo30-run-2/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking on, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The head takes up one tenth of the total length.

If the whole snake measures ten feet that makes the head about one foot long.

Subtracting that from the total leaves nine feet for the rest of the body.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"10 - (10 / 10)\"}",
      "call_id": "xEtI7EGRF7NHkXbzPJvsvhItHG3DZz23",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "xEtI7EGRF7NHkXbzPJvsvhItHG3DZz23",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "10 - (10 / 10) = 9",
      "status": "Succeeded"
    }
  ]
}
```

**Frozen review rationale:**

```text
Final task answer matches the frozen numerical value, including equivalent word forms.
```

[Scored source](../../results/on/run-1-scored.json) · [Raw requests, SSE and events](../../results/on/nemo30-run-1/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking on, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The head takes up one tenth of the total length.

If the whole snake measures ten feet that makes the head about one foot long.

Subtracting that from the total leaves nine feet for the rest of the body.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"10 - (10 / 10)\"}",
      "call_id": "gzI1j1DWdA9TZUzQvy3IxtlKovoJUvaa",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "gzI1j1DWdA9TZUzQvy3IxtlKovoJUvaa",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "10 - (10 / 10) = 9",
      "status": "Succeeded"
    }
  ]
}
```

**Frozen review rationale:**

```text
Final task answer matches the frozen numerical value, including equivalent word forms.
```

[Scored source](../../results/on/run-2-scored.json) · [Raw requests, SSE and events](../../results/on/nemo30-run-2/candidate.tar.gz)

## Earlier 4B comparison — thinking off

These are earlier inference runs on the same question, not a thinking-toggle experiment. The trained Nemotron is the calculator adapter, not the rejected clarification pilot.

### Original Nemotron 3 Nano 4B — repeat 1

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
The whole snake is ten feet long and the head takes up one‑tenth of that, which is one foot.  

Ten feet − one foot = nine feet.

So the part of the body after the head measures **nine feet**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/main/run-1-scored.json) · [Raw trace](../../results/earlier-4b/main/unmodified-run-1/candidate.tar.gz)

### Original Nemotron 3 Nano 4B — repeat 2

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
The whole snake is ten feet long and the head takes up one‑tenth of that, which is one foot.  

Ten feet − one foot = nine feet.

So the part of the body after the head measures **nine feet**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/main/run-2-scored.json) · [Raw trace](../../results/earlier-4b/main/unmodified-run-2/candidate.tar.gz)

### Calculator-trained Nemotron 3 Nano 4B — repeat 1

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
The snake's head is one‑tenth of its total length.  
- Total length: 10 feet → Head length: 1/10 × 10 ft = **1 foot**.  
- Rest of the body (body minus head): 10 ft − 1 ft = **9 feet**.

So, excluding the head, the snake’s remaining body is **9 feet long**.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"9*12\"}",
      "call_id": "6zFzsEQSVifcvZDMseMkH12hI7DZXlOc",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "6zFzsEQSVifcvZDMseMkH12hI7DZXlOc",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "9*12 = 108",
      "status": "Succeeded"
    }
  ]
}
```

[Scored source](../../results/earlier-4b/main/run-1-scored.json) · [Raw trace](../../results/earlier-4b/main/nemotron-run-1/candidate.tar.gz)

### Calculator-trained Nemotron 3 Nano 4B — repeat 2

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
The snake's head is one‑tenth of its total length.  
- Total length: 10 feet → Head length: 1/10 × 10 ft = **1 foot**.  
- Rest of the body (body minus head): 10 ft − 1 ft = **9 feet**.

So, excluding the head, the snake’s remaining body is **9 feet long**.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"9*12\"}",
      "call_id": "hb5JmmdJQolOS36gCdh4xxXw5Gq8dISU",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "hb5JmmdJQolOS36gCdh4xxXw5Gq8dISU",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "9*12 = 108",
      "status": "Succeeded"
    }
  ]
}
```

[Scored source](../../results/earlier-4b/main/run-2-scored.json) · [Raw trace](../../results/earlier-4b/main/nemotron-run-2/candidate.tar.gz)

### Qwen3.5-4B — repeat 1

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
If the head is one-tenth of the total length, then:

Head = 1/10 × 10 feet = **1 foot**  
Rest of the body (excluding head) = Total - Head = 10 - 1 = **9 feet**

So, the rest of the snake’s body minus the head is **9 feet long**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/main/run-1-scored.json) · [Raw trace](../../results/earlier-4b/main/qwen-run-1/candidate.tar.gz)

### Qwen3.5-4B — repeat 2

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
If the head is one-tenth of the total length, then:

Head = 1/10 × 10 feet = **1 foot**  
Rest of the body (excluding head) = Total - Head = 10 - 1 = **9 feet**

So, the rest of the snake’s body minus the head is **9 feet long**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/main/run-2-scored.json) · [Raw trace](../../results/earlier-4b/main/qwen-run-2/candidate.tar.gz)
