# Model identities and test design

[Research report](../PAPER.md) · [Every question and response](README.md) · [Training method](../training/README.md)

## Which Qwen?

**The larger-model experiment used the installed Qwen3.8-27B, quantized as Q4_K_M.**
The earlier small-model comparison used **Qwen3.5-4B, also Q4_K_M**. They are
different model versions, so their difference cannot be attributed to size alone.
Neither Qwen artifact was trained by DayCare in this study.

| Record label | Model | Local training status | Thinking settings in this archive |
|---|---|---|---|
| `qwen27` | Installed Qwen3.8-27B Q4_K_M | No DayCare training | Off and on |
| `nemo30` | NVIDIA Nemotron 3 Nano 30B-A3B Q4_K_M | No DayCare training | Off and on |
| Earlier `qwen` | Qwen3.5-4B Q4_K_M | No DayCare training | Off |
| Earlier `unmodified` | Original Nemotron 3 Nano 4B, Q4_K_M export | No DayCare adapter | Off |
| Earlier `nemotron` | Nemotron 3 Nano 4B, calculator-trained Q4_K_M export | DayCare calculator LoRA, continued from an earlier adapter | Off |

“No DayCare training” does not mean a pretrained base without publisher
post-training. These are the installed/downloaded inference artifacts. The
trained 4B arm is not the later rejected clarification pilot.

## Exact artifact identities

SHA-256 identifies the local files actually evaluated:

| Artifact filename / role | SHA-256 |
|---|---|
| `Qwen3.8-27B-Q4_K_M.gguf` | `31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34` |
| `NVIDIA-Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf` | `0f111a0d49777a2a0178758b1aee14e5365c495987499401ef3ebe87754322a8` |
| `Qwen_Qwen3.5-4B-Q4_K_M.gguf` | `13c16f426047e2de38cd075bdade4a7bcbc8c774384876f677740cda65f8a983` |
| Original 4B `unmodified-Q4_K_M.gguf` | `0148c1d5d6e3af1bebf8d284cc2b44fd0c616ac87d0ca5624bdbda116ed7c6c5` |
| Trained 4B `candidate-q4_k_m.gguf` | `1698c08aad72891a18595a1da2fa0acdd5abcb29559bb2c658460bb5bfdf2091` |

The installed Qwen27 file identifies itself as Qwen3.8-27B in GGUF metadata;
its upstream checksum has not been independently established. Nemo30 was
verified against the ggml-org publisher revision listed in the
[original report](../large-model-comparison.md#artifacts-and-limits).
Nemo30 has about 3.5B active parameters per token; it is not compute-matched to
a dense 27B model. Original per-run manifests preserve the file paths and hashes.

## What each test measures

| Cohort / task | Questions | Measurement |
|---|---:|---|
| Original / natural math | 32 | Final mathematical answer to an unmodified word problem |
| Original / ordinary answers | 20 | Simple target facts or words; correctness and unnecessary tools are separate |
| Original / tool selection | 16 | Proposed tool names against the allowed names; OS execution is blocked |
| Original / calculator smoke | 4 | Arithmetic stress cases through the actual calculator loop |
| Original / supplied expression | 8 | Answer when an explicit calculator expression is supplied |
| Audited / clear math | 24 | Final answer on questions audited as sufficiently specified |
| Audited / clarification | 8 | Ask for the required missing fact rather than assume it |
| Audited / ordinary answers | 20 | Plain-answer control alongside the audited questions |

[Read all 132 exact questions and every recorded response](README.md).
Each question page shows the answer key or allowed tools, completion/cutoff flags,
original score, actual tool arguments, tool receipts, and links to raw traces.
For the larger runs it also includes the frozen review rationale.

All models saw the complete 35-tool menu and native model template. The larger
thinking toggle retained temperature 0, seed 42, a 16,384-token context and
768 output tokens per inference response; reasoning shares that output limit.
Each condition ran twice on a fresh server with prompt/RAM caches disabled.
The eight larger-model runs contain 1,056 turns. The earlier 4B runs add 792
turns on the same questions, giving **1,848 recorded responses** in the appendix.
These are 132 distinct test prompts, not 1,848 independent questions.
