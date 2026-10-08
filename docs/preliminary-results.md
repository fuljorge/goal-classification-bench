# Preliminary results (2026-10-08)

> **Superseded by [`results.md`](results.md).**
>
> - **How these were measured:** a single pass per configuration, made before this
>   repository existed, with options presented in **similarity order** (no position
>   control) and without per-phrase predictions (no paired tests).
> - **Status:** they motivated the protocol in [`method.md`](method.md) and are kept only
>   as history.
> - **What the final results changed:** the position-bias concern raised here is resolved
>   there. The Strands Decider's accuracy does not depend on option order.

## Setup

| Item | Value |
|---|---|
| Hardware | NVIDIA RTX 5080 16 GB (one Laya row on an RTX 3090 over the LAN) |
| Software | PyTorch 2.14.0+cu130 |
| Deciders | Measured one at a time |
| Embeddings | Served remotely by LM Studio (context 8192) |
| Fitting grid | `a ∈ {0.5, 1, 2}`; the platform grid, without `a = 0` |
| Latency percentile | p95 taken as the ⌊0.95·n⌋-th smallest value |

Accuracy is top-1 over the 150 test phrases, with the 95% Wilson interval in brackets.

## Qwen3-Embedding-0.6B

- **Shortlist recall:** 98.0% [94.3, 99.3].
- **Embeddings alone:** 81.3% [74.3, 86.8]. Because options were in similarity order, this
  is also the `first_option` baseline.

| Decider | Alone | Fitted (a; b; T) | Oracle (a; b) | Latency median / p95 |
|---|---|---|---|---|
| laya-multilingual (RTX 3090, LAN) | 56.7% [48.7, 64.3] | 62.0% (0.5; 8; 1.5) | 81.3% (0; 1) | 36 / 48 ms |
| laya-multilingual (RTX 5080) | 56.0% [48.0, 63.7] | 61.3% [53.3, 68.8] (0.5; 8; 1.5) | 81.3% (0; 1) | 36 / 47 ms |
| strands-decider-2B-hobson-v21 (RTX 5080) | 84.7% [78.0, 89.6] | 87.3% [81.1, 91.7] (0.5; 8; 0.5) | 87.3% (0.5; 8) | 137 / 164 ms |

## Qwen3-Embedding-4B

- **Shortlist recall:** 100%.
- **Embeddings alone (= first option):** 94.7% [89.8, 97.3].

| Decider | Alone | Fitted (a; b; T) | Oracle (a; b) | Latency median / p95 |
|---|---|---|---|---|
| laya-multilingual (RTX 5080) | 54.0% [46.0, 61.8] | 68.0% [60.2, 74.9] (0.5; 8; 1.5) | 94.7% (0; 1) | 36 / 49 ms |
| strands-decider-2B-hobson-v21 (RTX 5080) | 86.7% [80.3, 91.2] | 91.3% [85.7, 94.9] (0.5; 8; 0.5) | 94.7% (0; 1) | 135 / 166 ms |

## Observations to verify

- **Strands Decider × Laya.** Off the shelf, the Strands Decider is about 30 points more
  accurate than Laya alone.
  - Its 84.7% is close to the 81.3% first-option baseline, so part of the gap may be
    position preference.
  - Laya, by contrast, does not exploit the order.
- **0.6B embeddings.** Only the Decider improves on the embeddings alone (87.3% vs 81.3%).
  The intervals overlap, so this needs the paired test.
- **4B embeddings.** No decider improves on the embeddings alone (94.7%). The fitted platform
  grid cannot select `a = 0`, so it loses accuracy.
- **Latency.** The Decider is about 3.5× slower than Laya per request.
