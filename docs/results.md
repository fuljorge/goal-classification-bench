# Results (goalbench 0.1.0, 2026-10-08)

## Setup

The protocol is described in [`method.md`](method.md).

| Item | Value |
|---|---|
| Runs | 20, raw logs in [`results/v0.1.0/`](../results/v0.1.0/) |
| Deciders | 2: `laya-multilingual` and `strands-decider-2B-hobson-v21` |
| Embedding models | 2: Qwen3-Embedding-0.6B and -4B |
| Option orders | `random` with seeds 0, 1 and 2, plus the `similarity` and `reversed` controls with seed 0 |
| Test phrases | 150 per run, 30 goals, 10-goal shortlist |
| Hardware | NVIDIA RTX 5080 16 GB, driver 617.14, Windows 11 |
| Software | PyTorch 2.14.0+cu130; Python 3.14.6 for the client and 3.12 for the servers |
| Embeddings | Served by LM Studio over HTTPS, context 8192 |

Both deciders were loaded on the same GPU and queried one at a time.

The full per-run tables are in [`results/v0.1.0/report.md`](../results/v0.1.0/report.md),
and the machine-readable version, including every McNemar test, is in
[`results/v0.1.0/summary.json`](../results/v0.1.0/summary.json).

## 1. Main results (random option order, mean ± sample SD over 3 seeds)

Top-1 accuracy on the 150 test phrases. A single run has a 95% Wilson interval of about
±6 points around 80% and about ±4 points around 95%.

### Qwen3-Embedding-0.6B

- **Shortlist recall:** 98.0%.
- **Embeddings alone:** 81.3%.
- **First-option baseline:** 9.6 ± 2.5%.

| Decider | Decider alone | Fitted, platform grid (a > 0) | Fitted, grid with a = 0 | Oracle on test | Latency median / p95 |
|---|---|---|---|---|---|
| laya-multilingual | 51.8 ± 2.5% | 58.4 ± 1.7% | 81.3 ± 0.0% (a = 0 in every seed) | 81.3% | 31 / 34 ms |
| strands-decider-2B-hobson-v21 | **84.9 ± 1.4%** | 85.8 ± 0.4% (a = 0.5, b = 4) | 85.8 ± 0.4% (a = 0.5, b = 4) | 86.9 ± 0.4% | 122 / 135 ms |

### Qwen3-Embedding-4B

- **Shortlist recall:** 100%.
- **Embeddings alone:** **94.7%**.
- **First-option baseline:** 10.4 ± 3.3%.

| Decider | Decider alone | Fitted, platform grid (a > 0) | Fitted, grid with a = 0 | Oracle on test | Latency median / p95 |
|---|---|---|---|---|---|
| laya-multilingual | 50.9 ± 1.5% | 63.8 ± 1.7% | 94.7 ± 0.0% (a = 0 in every seed) | 94.7% | 32 / 41 ms |
| strands-decider-2B-hobson-v21 | 85.8 ± 1.4% | 89.6 ± 0.8% (a = 0.5, b = 8) | 89.6 ± 0.8% (a = 0.5, b = 8) | 94.7% (a = 0) | 127 / 173 ms |

**Latency:** client-side time of one HTTP request with one phrase. The embedding call is not
included.

## 2. Paired tests (exact McNemar, two-sided, per seed, random order)

| Comparison | Discordant pairs (A only / B only) | p-value range over seeds | Reading |
|---|---|---|---|
| Decider alone vs Laya alone, 0.6B | 46–59 / 3–6 | 7·10⁻¹¹ to 2·10⁻¹² | Decider far better |
| Decider alone vs Laya alone, 4B | 52–59 / 3–4 | 10⁻¹¹ to 2·10⁻¹⁴ | Decider far better |
| Decider fitted vs embeddings alone, 0.6B | 16–17 / 9–10 | 0.23–0.33 | +4.5 points, **not significant** |
| Decider alone vs embeddings alone, 0.6B | 16–17 / 10–14 | 0.25–0.72 | not significant |
| Decider fitted vs embeddings alone, 4B | 6 / 13–15 | 0.078–0.17 | embeddings better, not significant per seed |
| Decider alone vs embeddings alone, 4B | 6 / 17–21 | 0.006–0.035 | **embeddings significantly better** |
| Laya fitted (platform grid) vs embeddings alone, both models | 0–5 / 37–49 | < 5·10⁻⁷ | forcing Laya in hurts |

No correction for multiple comparisons is applied. Each line reports the range over the
three random-order seeds.

## 3. Option-order sensitivity (seed 0, decider alone)

| Decider | Embeddings | similarity | random | reversed | Similarity vs reversed (McNemar) | Picks first option: similarity / random / reversed |
|---|---|---|---|---|---|---|
| Laya | 0.6B | 56.0% | 54.7% | 44.7% | 22 / 5, **p = 0.0015** | 62% / 16% / 10% |
| Laya | 4B | 54.0% | 50.0% | 48.0% | 17 / 8, p = 0.11 | 57% / 14% / 8% |
| Strands Decider | 0.6B | 84.7% | 83.3% | 84.7% | 2 / 2, p = 1.0 | 77% / 9% / 1% |
| Strands Decider | 4B | 86.7% | 85.3% | 85.3% | 4 / 2, p = 0.69 | 83% / 11% / 0% |

In similarity order, the true goal is first in 81.3% (0.6B) and 94.7% (4B) of the phrases.

- **Strands Decider:** it follows the content. It picks the first option less often than the
  truth is first, and only 4–6 of 150 phrases change outcome when the order is reversed.
- **Laya:** it prefers the first slot. It picks it in 57–62% of the similarity-ordered
  questions, against a uniform 10%, and loses 11 points when the order is reversed with the
  0.6B shortlist.

## Findings

1. **Strands Decider is much stronger than Laya off the shelf, and not because of position.**
   - **Accuracy:** 84.9–85.8% against 50.9–51.8% on the same 10-goal questions (p < 10⁻¹⁰
     in every paired setting).
   - **Order:** its accuracy is invariant to option order.
   - **Laya:** without domain fine-tuning or calibration (its checkpoint ships temperatures
     of 1.0), it is below the embedding similarity it is meant to complement. It is also
     measurably order-sensitive.
2. **A good embedding model is the strongest single component here.**
   - **4B:** similarity to 10 examples per goal reaches 94.7%. No decider improves on it,
     and the 4B embeddings are significantly better than the Decider alone.
   - **0.6B:** the Decider adds about 4.5 points (81.3% → 85.8%). The gain is consistent
     across seeds but not significant at n = 150.
3. **Cross-validated fitting on the examples does not transfer to the test phrases.**
   - **What happens:** with the 4B embeddings, CV on the 300 examples always selects
     `a = 0.5` (the decider is used) and loses about 5 points against `a = 0`, which the
     oracle shows to be best.
   - **Likely cause:** within CV, each example is scored against 8 examples per goal instead
     of 10. That weakens the similarity signal and makes the decider look more useful than
     it is at test time.
   - **Recommendation:** for deployment, choose `a` on held-out phrases rather than on
     examples alone.
4. **Latency.** Per request, the Decider is about 4× slower than Laya (p95 135–173 ms against
   34–41 ms on an RTX 5080). Add the embedding call when budgeting for an end-to-end limit.

## Limitations

See [`method.md`](method.md#threats-to-validity). In short:
- one small, synthetic, single-author dataset;
- no fine-tuning of either decider;
- one GPU;
- per-seed p-values without a multiple-comparison correction.

The [preliminary results](preliminary-results.md) used similarity order only and are
superseded by this document.
