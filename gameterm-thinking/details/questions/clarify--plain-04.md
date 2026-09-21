# clarify::plain-04

[All questions](../README.md) · [Models and test design](../models-and-tests.md)

Cohort: `clarify`. Task: `plain`.

## Exact question

```text
What is the capital of South Korea?
```

## Frozen expected answer / allowed tool names

```text
["Seoul"]
```

Question-quality audit (including any missing fact):

```text
{
  "id": "plain-04",
  "quality": "clear",
  "rationale": "Stable ordinary fact or English word form; accepted alternatives declared before inference."
}
```

## Recorded responses

The text below is the harness-delivered response, not a cleaned-up answer. When a response was cut off, the provider may have substituted unfinished reasoning for final text. The cutoff and completion flags remain visible. Empty output is explicitly marked.

### Qwen3.8-27B (Q4_K_M) — thinking off, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Seoul. It's been the capital since 1394 when King Taejo moved it there from Kaesong to found the Joseon dynasty. The city has a long history before that too, as Hanul and later Hanyang under earlier kingdoms like Silla and Goryeo.
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
Correct requested fact or valid synonym; case, punctuation and explanatory prose accepted. Score is for the requested fact, not all incidental claims.
```

[Scored source](../../results/off/run-1-scored.json) · [Raw requests, SSE and events](../../results/off/qwen27-run-1/candidate.tar.gz)

### Qwen3.8-27B (Q4_K_M) — thinking off, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Seoul. It's been the capital since 1394 when King Taejo moved it there from Kaesong to found the Joseon dynasty. The city has a long history before that too, as Hanul and later Hanyang under earlier kingdoms like Silla and Goryeo.
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
Correct requested fact or valid synonym; case, punctuation and explanatory prose accepted. Score is for the requested fact, not all incidental claims.
```

[Scored source](../../results/off/run-2-scored.json) · [Raw requests, SSE and events](../../results/off/qwen27-run-2/candidate.tar.gz)

### Qwen3.8-27B (Q4_K_M) — thinking on, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Seoul! It's been the capital since way back when Korea was a kingdom of kingdoms. The city sits in the northwest part of the country, right along the Han River.
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
Correct final requested answer; prose and equivalent forms accepted.
```

[Scored source](../../results/on/run-1-scored.json) · [Raw requests, SSE and events](../../results/on/qwen27-run-1/candidate.tar.gz)

### Qwen3.8-27B (Q4_K_M) — thinking on, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Seoul! It's been the capital since way back when Korea was a kingdom of kingdoms. The city sits in the northwest part of the country, right along the Han River.
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
Correct final requested answer; prose and equivalent forms accepted.
```

[Scored source](../../results/on/run-2-scored.json) · [Raw requests, SSE and events](../../results/on/qwen27-run-2/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking off, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Seoul. It's been the capital since 1394 and remains so today.
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
Correct requested fact or valid synonym; case, punctuation and explanatory prose accepted. Score is for the requested fact, not all incidental claims.
```

[Scored source](../../results/off/run-1-scored.json) · [Raw requests, SSE and events](../../results/off/nemo30-run-1/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking off, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Seoul. It's been the capital since 1394 and remains so today.
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
Correct requested fact or valid synonym; case, punctuation and explanatory prose accepted. Score is for the requested fact, not all incidental claims.
```

[Scored source](../../results/off/run-2-scored.json) · [Raw requests, SSE and events](../../results/off/nemo30-run-2/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking on, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The capital of South Korea is **Seoul**. It’s a bustling city in the northwest part of the country and serves as its political, economic, and cultural center.
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
States the correct requested fact or accepted equivalent; explanatory prose is allowed.
```

[Scored source](../../results/on/run-1-scored.json) · [Raw requests, SSE and events](../../results/on/nemo30-run-1/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking on, repeat 2

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
The capital of South Korea is **Seoul**. It’s a bustling city in the northwest part of the country and serves as its political, economic, and cultural center.
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
States the correct requested fact or accepted equivalent; explanatory prose is allowed.
```

[Scored source](../../results/on/run-2-scored.json) · [Raw requests, SSE and events](../../results/on/nemo30-run-2/candidate.tar.gz)

## Earlier 4B comparison — thinking off

These are earlier inference runs on the same question, not a thinking-toggle experiment. The trained Nemotron is the calculator adapter, not the rejected clarification pilot.

### Original Nemotron 3 Nano 4B — repeat 1

Original `interaction_success` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
Seoul.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/clarify/run-1-scored.json) · [Raw trace](../../results/earlier-4b/clarify/unmodified-run-1/candidate.tar.gz)

### Original Nemotron 3 Nano 4B — repeat 2

Original `interaction_success` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
Seoul.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/clarify/run-2-scored.json) · [Raw trace](../../results/earlier-4b/clarify/unmodified-run-2/candidate.tar.gz)

### Calculator-trained Nemotron 3 Nano 4B — repeat 1

Original `interaction_success` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
Seoul.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/clarify/run-1-scored.json) · [Raw trace](../../results/earlier-4b/clarify/nemotron-run-1/candidate.tar.gz)

### Calculator-trained Nemotron 3 Nano 4B — repeat 2

Original `interaction_success` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
Seoul.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/clarify/run-2-scored.json) · [Raw trace](../../results/earlier-4b/clarify/nemotron-run-2/candidate.tar.gz)

### Qwen3.5-4B — repeat 1

Original `interaction_success` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
The capital of South Korea is Seoul. It's a bustling city known for its blend of modern skyscrapers and traditional temples, like Gyeongbokgung Palace. Did you want to know more about it? Maybe where Jalen Brunson would play if he were there instead of the Knicks!
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/clarify/run-1-scored.json) · [Raw trace](../../results/earlier-4b/clarify/qwen-run-1/candidate.tar.gz)

### Qwen3.5-4B — repeat 2

Original `interaction_success` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
The capital of South Korea is Seoul. It's a bustling city known for its blend of modern skyscrapers and traditional temples, like Gyeongbokgung Palace. Did you want to know more about it? Maybe where Jalen Brunson would play if he were there instead of the Knicks!
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/clarify/run-2-scored.json) · [Raw trace](../../results/earlier-4b/clarify/qwen-run-2/candidate.tar.gz)
