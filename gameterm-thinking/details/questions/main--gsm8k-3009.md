# main::gsm8k-3009

[All questions](../README.md) · [Models and test design](../models-and-tests.md)

Cohort: `main`. Task: `math`.

## Exact question

```text
The country of Belize had a 5 lane bridge that had 2000 vehicles passing through it every month. They decided to build a new bridge that had twice the capacity of the old one, and the number of vehicles passing through the new one increased by 60% more than the old bridge. If the bridges work concurrently for a year, calculate the total number of vehicles that pass through the two bridges.
```

## Frozen expected answer / allowed tool names

```text
"62400"
```

## Recorded responses

The text below is the harness-delivered response, not a cleaned-up answer. When a response was cut off, the provider may have substituted unfinished reasoning for final text. The cutoff and completion flags remain visible. Empty output is explicitly marked.

### Qwen3.8-27B (Q4_K_M) — thinking off, repeat 1

Frozen score: **pass**. Completed event: **True**. Output cutoff: **False**. Review category: `correct_answer`.

```text
Here's the breakdown:

**Old bridge:** 2,000 vehicles/month × 12 months = **24,000 vehicles/year**

**New bridge:** "60% more than the old" means 2,000 + (60% of 2,000) = 2,000 + 1,200 = 3,200 vehicles/month
So: 3,200 × 12 months = **38,400 vehicles/year**

*(Note: the "twice the capacity" detail is a red herring for this calculation. Capacity tells us how many cars *could* pass; we're told how many actually did.)*

**Total:** 24,000 + 38,400 = **62,400 vehicles over the year.**
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"2000 * 12\"}",
      "call_id": "dMQJte2v6AqKDsbS5m1dTBLDQkgF93BJ",
      "event": "tool_proposed",
      "name": "calculate"
    },
    {
      "arguments_json": "{\"expression\":\"(2000 + 3200) * 12\"}",
      "call_id": "ETnO3cDDcxR3jOGhkMh1Zi3Tiwjcykhs",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "dMQJte2v6AqKDsbS5m1dTBLDQkgF93BJ",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "2000 * 12 = 24000",
      "status": "Succeeded"
    },
    {
      "call_id": "ETnO3cDDcxR3jOGhkMh1Zi3Tiwjcykhs",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "(2000 + 3200) * 12 = 62400",
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
Here's the breakdown:

**Old bridge:** 2,000 vehicles/month × 12 months = **24,000 vehicles/year**

**New bridge:** "60% more than the old" means 2,000 + (60% of 2,000) = 2,000 + 1,200 = 3,200 vehicles/month
So: 3,200 × 12 months = **38,400 vehicles/year**

*(Note: the "twice the capacity" detail is a red herring for this calculation. Capacity tells us how many cars *could* pass; we're told how many actually did.)*

**Total:** 24,000 + 38,400 = **62,400 vehicles over the year.**
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"2000 * 12\"}",
      "call_id": "V2ktHSxKauq1oISLDDWpcrolHOS2NTyk",
      "event": "tool_proposed",
      "name": "calculate"
    },
    {
      "arguments_json": "{\"expression\":\"(2000 + 3200) * 12\"}",
      "call_id": "MO9UaIjzVz5chCe2LcD6Xe1aYimETBil",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "V2ktHSxKauq1oISLDDWpcrolHOS2NTyk",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "2000 * 12 = 24000",
      "status": "Succeeded"
    },
    {
      "call_id": "MO9UaIjzVz5chCe2LcD6Xe1aYimETBil",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "(2000 + 3200) * 12 = 62400",
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
Here's how it breaks down:

- **Old bridge:** 2,000 vehicles/month → ×12 months = 24,000 for the year
- **New bridge:** traffic is 60% more than the old one, so 2,000 + 60% of that = 3,200 vehicles/month → ×12 = 38,400 for the year

(The lane counts are a bit of misdirection. The capacity doubling just explains why it could handle the extra traffic.)

**Total: 24,000 + 38,400 = 62,400 vehicles over the year.**
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"(2000 + 2000 * (1 + 60%)) * 12\"}",
      "call_id": "gJ0u3ietIOahXXwcFqxDYNghvDyQdujL",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "gJ0u3ietIOahXXwcFqxDYNghvDyQdujL",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "(2000 + 2000 * (1 + 60%)) * 12 = 62400",
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
Here's how it breaks down:

- **Old bridge:** 2,000 vehicles/month → ×12 months = 24,000 for the year
- **New bridge:** traffic is 60% more than the old one, so 2,000 + 60% of that = 3,200 vehicles/month → ×12 = 38,400 for the year

(The lane counts are a bit of misdirection. The capacity doubling just explains why it could handle the extra traffic.)

**Total: 24,000 + 38,400 = 62,400 vehicles over the year.**
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"(2000 + 2000 * (1 + 60%)) * 12\"}",
      "call_id": "8bOt77trF1PytDJzxObyVFbtW8W272y9",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "8bOt77trF1PytDJzxObyVFbtW8W272y9",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "(2000 + 2000 * (1 + 60%)) * 12 = 62400",
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
The old bridge carried 2,000 vehicles each month.  
Its capacity was doubled for the new bridge, and traffic on it rose by 60 % over the old‑bridge volume.

- New‑bridge monthly traffic: \(2{,}000 \times 1.6 = 3{,}200\) vehicles.  
- Combined monthly traffic of both bridges: \(2{,}000 + 3{,}200 = 5{,}200\) vehicles.  

Over a year (12 months) the total number of vehicle passages is:

\[
5{,}200 \times 12 = 62{,}400.
\]

So, during one year about **62,400** vehicles would pass through the two bridges together.
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
The old bridge carried 2,000 vehicles each month.  
Its capacity was doubled for the new bridge, and traffic on it rose by 60 % over the old‑bridge volume.

- New‑bridge monthly traffic: \(2{,}000 \times 1.6 = 3{,}200\) vehicles.  
- Combined monthly traffic of both bridges: \(2{,}000 + 3{,}200 = 5{,}200\) vehicles.  

Over a year (12 months) the total number of vehicle passages is:

\[
5{,}200 \times 12 = 62{,}400.
\]

So, during one year about **62,400** vehicles would pass through the two bridges together.
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

Frozen score: **fail**. Completed event: **True**. Output cutoff: **True**. Review category: `partial`.

```text
We need to compute: Old bridge capacity? It had 2000 vehicles per month passing through it (i.e., actual traffic). New bridge has twice the capacity of old one; and the number of vehicles passing through new increased by 60% more than the old bridge. Need total vehicles over a year for both bridges working concurrently.

Interpretation: Old bridge had 2000 vehicles per month. New bridge capacity is double that (i.e., can handle up to 4000 vehicles per month). But actual traffic on new bridge increased by 60% more than the old bridge's traffic? "the number of vehicles passing through the new one increased by 60% more than the old bridge." Could mean: The new bridge sees a volume that is 60% higher than the old bridge's volume. So if old =2000 per month, then new = 2000 * (1 + 0.6) = 3200 vehicles per month? But also capacity double; maybe they meant actual traffic increased by 60% relative to old: i.e., new traffic is 60% more than the old's volume => 2000*1.6=3200.

But could be ambiguous: "the number of vehicles passing through the new one increased by 60% more than the old bridge." Might mean increase relative to capacity? Actually they say built a new bridge that had twice the capacity, and the number of vehicles passing through the new one increased by 60% more than the old bridge. So maybe traffic on new is 60% higher than what passed through old (i.e., 2000 *1.6 =3200). That seems plausible.

Now they work concurrently for a year: total vehicles passing both bridges over that period = sum of monthly volumes times 12 months.

Old per month = 2000, new per month = maybe 2000*1.6=3200? Or could be capacity double => max capacity is 4000; but actual traffic increased by 60% more than old bridge's *capacity?* That would be ambiguous.

Probably they want: Old volume = 2000 per month. New volume = (old + 60% of old) = 1.6*2000=3200 per month. So total monthly combined = 5200, yearly = 5200 *12 = 62400.

Thus answer: 62,400 vehicles in a year.

We need to compute using calculate tool? It's simple arithmetic; we can do mental but must use calculate function for any number work. The instruction says "Use it for every number you would have to work out". So we should call calculate with expression that yields result and maybe decimals 0 as integer.

Expression: (2000 *12) + ((2000*1.6)*12). Or simpler: total = 12*(2000+3200)=12*5200=62400.

Let's use calculate with expression "12 * (2000 + (2000 * 1.6))". That yields maybe decimal? It will be integer but we can specify decimals 0.

Thus call calculate with expression and decimals perhaps 0.

We need to output only tool usage, not any text before or after; must do one operation per turn: either a tool call or final answer. Since
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
Unfinished reasoning/planning, with no completed final response.
```

[Scored source](../../results/on/run-1-scored.json) · [Raw requests, SSE and events](../../results/on/nemo30-run-1/candidate.tar.gz)

### NVIDIA Nemotron 3 Nano 30B-A3B (Q4_K_M) — thinking on, repeat 2

Frozen score: **fail**. Completed event: **True**. Output cutoff: **True**. Review category: `partial`.

```text
We need to compute: Old bridge capacity? It had 2000 vehicles per month passing through it (i.e., actual traffic). New bridge has twice the capacity of old one; and the number of vehicles passing through new increased by 60% more than the old bridge. Need total vehicles over a year for both bridges working concurrently.

Interpretation: Old bridge had 2000 vehicles per month. New bridge capacity is double that (i.e., can handle up to 4000 vehicles per month). But actual traffic on new bridge increased by 60% more than the old bridge's traffic? "the number of vehicles passing through the new one increased by 60% more than the old bridge." Could mean: The new bridge sees a volume that is 60% higher than the old bridge's volume. So if old =2000 per month, then new = 2000 * (1 + 0.6) = 3200 vehicles per month? But also capacity double; maybe they meant actual traffic increased by 60% relative to old: i.e., new traffic is 60% more than the old's volume => 2000*1.6=3200.

But could be ambiguous: "the number of vehicles passing through the new one increased by 60% more than the old bridge." Might mean increase relative to capacity? Actually they say built a new bridge that had twice the capacity, and the number of vehicles passing through the new one increased by 60% more than the old bridge. So maybe traffic on new is 60% higher than what passed through old (i.e., 2000 *1.6 =3200). That seems plausible.

Now they work concurrently for a year: total vehicles passing both bridges over that period = sum of monthly volumes times 12 months.

Old per month = 2000, new per month = maybe 2000*1.6=3200? Or could be capacity double => max capacity is 4000; but actual traffic increased by 60% more than old bridge's *capacity?* That would be ambiguous.

Probably they want: Old volume = 2000 per month. New volume = (old + 60% of old) = 1.6*2000=3200 per month. So total monthly combined = 5200, yearly = 5200 *12 = 62400.

Thus answer: 62,400 vehicles in a year.

We need to compute using calculate tool? It's simple arithmetic; we can do mental but must use calculate function for any number work. The instruction says "Use it for every number you would have to work out". So we should call calculate with expression that yields result and maybe decimals 0 as integer.

Expression: (2000 *12) + ((2000*1.6)*12). Or simpler: total = 12*(2000+3200)=12*5200=62400.

Let's use calculate with expression "12 * (2000 + (2000 * 1.6))". That yields maybe decimal? It will be integer but we can specify decimals 0.

Thus call calculate with expression and decimals perhaps 0.

We need to output only tool usage, not any text before or after; must do one operation per turn: either a tool call or final answer. Since
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
Unfinished reasoning/planning, with no completed final response.
```

[Scored source](../../results/on/run-2-scored.json) · [Raw requests, SSE and events](../../results/on/nemo30-run-2/candidate.tar.gz)

## Earlier 4B comparison — thinking off

These are earlier inference runs on the same question, not a thinking-toggle experiment. The trained Nemotron is the calculator adapter, not the rejected clarification pilot.

### Original Nemotron 3 Nano 4B — repeat 1

Original `correct` score: **fail**. Completed event: **True**. Output cutoff: **False**.

```text
The old bridge handles 2000 vehicles per month.

A new bridge with twice the capacity would handle 4000 vehicles per month if it were used alone.

But the problem says: "the number of vehicles passing through the new one increased by 60% more than the old bridge."

So, increase = 60% of 2000 = 1.2 × 2000 = 2400

Thus, total at new bridge = original + increase = 2000 + 2400 = 4400 vehicles per month.

Now both bridges work concurrently for a year (12 months).

Total monthly flow: old bridge 2000 + new bridge 4400 = 6400 vehicles

Over 12 months: 6400 × 12 = ?

Let's calculate:

(6400 × 12) = 76800

So total number of vehicles passing through both bridges in a year is **76,800**.

Answer: 76800
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

Original `correct` score: **fail**. Completed event: **True**. Output cutoff: **False**.

```text
The old bridge handles 2000 vehicles per month.

A new bridge with twice the capacity would handle 4000 vehicles per month if it were used alone.

But the problem says: "the number of vehicles passing through the new one increased by 60% more than the old bridge."

So, increase = 60% of 2000 = 1.2 × 2000 = 2400

Thus, total at new bridge = original + increase = 2000 + 2400 = 4400 vehicles per month.

Now both bridges work concurrently for a year (12 months).

Total monthly flow: old bridge 2000 + new bridge 4400 = 6400 vehicles

Over 12 months: 6400 × 12 = ?

Let's calculate:

(6400 × 12) = 76800

So total number of vehicles passing through both bridges in a year is **76,800**.

Answer: 76800
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

Original `correct` score: **fail**. Completed event: **True**. Output cutoff: **False**.

```text
The old bridge handles 2,000 vehicles per month.  
- New bridge capacity: twice the old → \(2 \times 2{,}000 = 4{,}000\) vehicles/month.  
- Increase over the old bridge: a further 60% of the original traffic → additional \(0.6 \times 2{,}000 = 1{,}200\) vehicles/month.  

So the new bridge carries \(4{,}000 + 1{,}200 = 5{,}200\) vehicles per month.

Both bridges operate concurrently for one year (12 months). Total monthly traffic:  
\(2{,}000\ (\text{old}) + 5{,}200\ (\text{new}) = 7{,}200\) vehicles.  

Total yearly traffic: \(7{,}200 \times 12 = 86{,}400\).

**Answer:** \(\boxed{86\,400}\) vehicles pass through the two bridges in a year.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"2400*12+3840*12\"}",
      "call_id": "r0K8vE4N0raSjBKQq3gLvkHh4CO5qFlo",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "r0K8vE4N0raSjBKQq3gLvkHh4CO5qFlo",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "2400*12+3840*12 = 74880",
      "status": "Succeeded"
    }
  ]
}
```

[Scored source](../../results/earlier-4b/main/run-1-scored.json) · [Raw trace](../../results/earlier-4b/main/nemotron-run-1/candidate.tar.gz)

### Calculator-trained Nemotron 3 Nano 4B — repeat 2

Original `correct` score: **fail**. Completed event: **True**. Output cutoff: **False**.

```text
The old bridge handles 2,000 vehicles per month.  
- New bridge capacity: twice the old → \(2 \times 2{,}000 = 4{,}000\) vehicles/month.  
- Increase over the old bridge: a further 60% of the original traffic → additional \(0.6 \times 2{,}000 = 1{,}200\) vehicles/month.  

So the new bridge carries \(4{,}000 + 1{,}200 = 5{,}200\) vehicles per month.

Both bridges operate concurrently for one year (12 months). Total monthly traffic:  
\(2{,}000\ (\text{old}) + 5{,}200\ (\text{new}) = 7{,}200\) vehicles.  

Total yearly traffic: \(7{,}200 \times 12 = 86{,}400\).

**Answer:** \(\boxed{86\,400}\) vehicles pass through the two bridges in a year.
```

**Tool calls and returned results:**

```text
{
  "calls": [
    {
      "arguments_json": "{\"expression\":\"2400*12+3840*12\"}",
      "call_id": "2ERajMBcp9Rp9LBjp3WzIOgJNvYzqPzj",
      "event": "tool_proposed",
      "name": "calculate"
    }
  ],
  "tool_results": [
    {
      "call_id": "2ERajMBcp9Rp9LBjp3WzIOgJNvYzqPzj",
      "capability": "NotReported",
      "event": "tool_resolved",
      "output": "2400*12+3840*12 = 74880",
      "status": "Succeeded"
    }
  ]
}
```

[Scored source](../../results/earlier-4b/main/run-2-scored.json) · [Raw trace](../../results/earlier-4b/main/nemotron-run-2/candidate.tar.gz)

### Qwen3.5-4B — repeat 1

Original `correct` score: **pass**. Completed event: **True**. Output cutoff: **False**.

```text
Let's break this down step-by-step:

1. **Old Bridge Capacity**:  
   The old bridge had 2000 vehicles per month.  

2. **New Bridge Capacity**:  
   The new bridge has twice the capacity of the old one, so it can handle $2 \times 2000 = 4000$ vehicles per month.

3. **Increase in Traffic on New Bridge**:  
   The number of vehicles passing through the new bridge increased by 60% more than the old bridge. This means:  
   $$
   \text{New traffic} = 2000 + (0.60 \times 2000) = 2000 + 1200 = 3200 \, \text{vehicles/month}.
   $$

4. **Total Vehicles per Month**:  
   The total number of vehicles passing through both bridges each month is:  
   $$
   2000 (\text{old bridge}) + 3200 (\text{new bridge}) = 5200 \, \text{vehicles/month}.
   $$

5. **Total Vehicles Over a Year**:  
   Since the bridges work concurrently for a year (12 months), we multiply the monthly total by 12:  
   $$
   5200 \times 12 = 62400 \, \text{vehicles/year}.
   $$

**Final Answer**: The total number of vehicles that pass through both bridges in a year is **62,400**.
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
Let's break this down step-by-step:

1. **Old Bridge Capacity**:  
   The old bridge had 2000 vehicles per month.  

2. **New Bridge Capacity**:  
   The new bridge has twice the capacity of the old one, so it can handle $2 \times 2000 = 4000$ vehicles per month.

3. **Increase in Traffic on New Bridge**:  
   The number of vehicles passing through the new bridge increased by 60% more than the old bridge. This means:  
   $$
   \text{New traffic} = 2000 + (0.60 \times 2000) = 2000 + 1200 = 3200 \, \text{vehicles/month}.
   $$

4. **Total Vehicles per Month**:  
   The total number of vehicles passing through both bridges each month is:  
   $$
   2000 (\text{old bridge}) + 3200 (\text{new bridge}) = 5200 \, \text{vehicles/month}.
   $$

5. **Total Vehicles Over a Year**:  
   Since the bridges work concurrently for a year (12 months), we multiply the monthly total by 12:  
   $$
   5200 \times 12 = 62400 \, \text{vehicles/year}.
   $$

**Final Answer**: The total number of vehicles that pass through both bridges in a year is **62,400**.
```

**Tool calls and returned results:**

```text
{
  "calls": [],
  "tool_results": []
}
```

[Scored source](../../results/earlier-4b/main/run-2-scored.json) · [Raw trace](../../results/earlier-4b/main/qwen-run-2/candidate.tar.gz)
