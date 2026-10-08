# Language effect: Brazilian Portuguese vs English (goalbench 0.2.0)

## Question and design

The question is how much accuracy each component loses in Brazilian Portuguese, and whether
a checkpoint built for the language closes that gap.

- **Datasets:** [`data/goals_en.jsonl`](../data/goals_en.jsonl) is a line-by-line English
  translation of [`data/goals_ptbr.jsonl`](../data/goals_ptbr.jsonl). It has the same 30
  goals in the same order, and the i-th example and test phrase of each goal are
  translations of each other. Goal keys, which deciders see as option labels, are translated
  too.
- **Pairing:** the same decider, embedding model, option order and seed are compared across
  the two datasets with the exact McNemar test, phrase by phrase (`goalbench report
  --cross-dataset`).
- **Deciders:**
  - `laya-multilingual` and `strands-decider-2B-hobson-v21` on both datasets;
  - `laya-english`, the English checkpoint of the same Laya release (same revision
    `7b928d8`), on the English dataset only.
- **Question:** in English, the question is "What is the customer's goal in this message?"
  and Laya receives `lang = en`.
- **Everything else** is identical to [`results.md`](results.md): hardware, servers,
  embedding models, 10-goal shortlist, random order with seeds 0, 1 and 2, plus the
  similarity and reversed controls.
- **Runs:** 30 English runs in [`results/v0.2.0/en/`](../results/v0.2.0/en/), analysed
  together with the 20 Portuguese runs of v0.1.0. See
  [`results/v0.2.0/report.md`](../results/v0.2.0/report.md) and `summary.json`.

## 1. Accuracy by language

Top-1 accuracy on 150 test phrases, random order, mean ± SD over 3 seeds.

| Component | PT-BR, 0.6B | EN, 0.6B | Δ | PT-BR, 4B | EN, 4B | Δ |
|---|---|---|---|---|---|---|
| Shortlist recall | 98.0% | 100% | +2.0 | 100% | 100% | 0 |
| Embeddings alone | 81.3% | 93.3% | **+12.0** | 94.7% | 98.0% | +3.3 |
| Laya multilingual alone | 51.8 ± 2.5% | 57.6 ± 1.7% | +5.8 | 50.9 ± 1.5% | 57.3 ± 1.3% | +6.4 |
| **Laya English alone** | — | **81.6 ± 2.0%** | — | — | **80.9 ± 0.8%** | — |
| Strands Decider alone | 84.9 ± 1.4% | 90.9 ± 0.8% | +6.0 | 85.8 ± 1.4% | 89.6 ± 0.4% | +3.8 |
| Strands Decider + embeddings (CV-fitted) | 85.8 ± 0.4% | 94.2 ± 0.4% | **+8.4** | 89.6 ± 0.8% | 95.3 ± 0.0% | **+5.7** |
| Best configuration (embeddings alone, 4B) | — | — | — | 94.7% | 98.0% | +3.3 |

## 2. Paired tests across languages (exact McNemar, per seed, random order)

"PT only / EN only" counts the phrases correct in one language but not in the other.

| Component | Embeddings | PT only / EN only | p (3 seeds) | Reading |
|---|---|---|---|---|
| Embeddings alone | 0.6B | 6 / 24 | 0.0014 | **significant loss in PT-BR** |
| Embeddings alone | 4B | 2 / 7 | 0.18 | not significant |
| Laya multilingual alone | 0.6B | 10–19 / 21–24 | 0.024–0.87 | inconsistent |
| Laya multilingual alone | 4B | 10–16 / 20–27 | 0.035–0.50 | inconsistent |
| Strands Decider alone | 0.6B | 4–5 / 13–14 | 0.031–0.096 | borderline |
| Strands Decider alone | 4B | 5–7 / 11–12 | 0.14–0.48 | not significant |
| Strands Decider + embeddings | 0.6B | 2 / 14–16 | 0.0013–0.0042 | **significant loss in PT-BR** |
| Strands Decider + embeddings | 4B | 2 / 10–12 | 0.013–0.039 | **significant loss in PT-BR** |

## 3. A checkpoint for the language (English dataset, paired, same phrases)

| Comparison | Embeddings | A only / B only | p (3 seeds) |
|---|---|---|---|
| Laya English vs Laya multilingual | 0.6B | 42–47 / 8–9 | 8·10⁻⁸ to 3·10⁻⁶ |
| Laya English vs Laya multilingual | 4B | 41–44 / 5–8 | 4·10⁻⁸ to 6·10⁻⁷ |
| Strands Decider vs Laya English | 0.6B | 17–22 / 4–8 | 0.0005–0.036 |
| Strands Decider vs Laya English | 4B | 18–20 / 6 | 0.009–0.023 |

- **Same architecture, different checkpoint:** within the same Laya release, the
  English-specific checkpoint is **24 points** more accurate than the multilingual one on
  English (81.6% against 57.6%, and 80.9% against 57.3%). This is the largest single effect
  measured in this study.
- **Gap that remains:** the Strands Decider is still ahead of the English checkpoint, by
  about 9 points.

## 4. Option order in English (seed 0, decider alone)

| Decider | similarity / random / reversed (0.6B) | Picks first: similarity / reversed |
|---|---|---|
| Laya English | 82.7% / 82.0% / 78.7% | 81% / 1% |
| Laya multilingual | 66.7% / 56.0% / 60.0% | 67% / 2% |
| Strands Decider | 91.3% / 90.0% / 89.3% | 87% / 0% |

The pattern seen in Portuguese holds in English:
- **Strands Decider and Laya English:** both follow the content. Their picks of the first
  option track where the true goal is.
- **Laya multilingual:** it gains from the similarity order.

## Findings

1. **Every component pays a Portuguese penalty.**
   - **Same models, same phrases:** accuracy is lower in Brazilian Portuguese than in
     English, and the gap is significant for the 0.6B embeddings (−12 points) and for the
     full Decider pipeline (−8.4 points with 0.6B, −5.7 with 4B).
   - **Larger models:** they reduce but do not remove the gap. The 4B embeddings lose 3.3
     points, not significant at n = 150.
2. **Language-specific checkpoints matter most.**
   - **Laya:** the English checkpoint of Laya beats its multilingual sibling by 24 points
     on English text (p < 10⁻⁵ in every seed). The multilingual checkpoint, the only option
     Laya offers for Portuguese, reaches only 51–52% on PT-BR.
   - **What this suggests:** a checkpoint fine-tuned for Brazilian Portuguese on the
     goal-classification task could recover a gain of the same order.
3. **Fine-tuning in PT-BR is the logical next step.**
   - **Laya:** fine-tuning on Brazilian Portuguese goal-classification data targets the
     component with the largest measured gap. The training recipe is published with Laya
     (`laya-train`).
   - **Strands Decider:** already strong off the shelf, it loses 4–6 points in Portuguese,
     a smaller but consistent gap that domain and language fine-tuning could address.
   - **Embeddings:** the 0.6B model is the most language-sensitive component (−12 points);
     a PT-BR-adapted embedding model, or the 4B, is advisable.
4. **Cross-validated fitting on examples transfers poorly in both languages.** In English,
   CV again selects the decider (a > 0) where the oracle selects a = 0:
   - Decider with 4B: 95.3% against 98.0% for the embeddings alone;
   - Laya English with 0.6B: 89.3% against 93.3%.

## Threats specific to this comparison

- **Translation effects.**
  - **Language model as translator:** the English dataset is a translation produced by a
    language model, not text written by English-speaking customers. Translations tend to be
    more explicit and regular ("translationese"), which can make English easier.
  - **Length:** English phrases are longer (median 8 against 6 words), so they carry more
    explicit wording.
  - **Consequence:** part of the PT-BR gap may come from the data, not the language.
  - **Mitigation:** a native English set and a native PT-BR set written by people.
- **Localisation.** Brazil-specific terms were translated by meaning (Pix → instant
  transfer, boleto → payment slip, Procon → consumer protection agency, CNPJ → company tax
  ID, DANFE → electronic invoice document, consignado → payroll-deducted loan). Some of
  these concepts are less familiar to a model in their Brazilian form, which is part of the
  effect being measured but is not "language" in the narrow sense.
- **Same author.** Both datasets descend from the same synthetic source, so their
  difficulty is matched by construction but not independently validated.
- **Laya English on PT-BR.** It was not measured, by design: it is not a candidate for
  Portuguese.
