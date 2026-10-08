# Method

## Task

The task is intent ("goal") classification of customer-service messages in Brazilian
Portuguese. It is cast as **single-choice selection among K options described in natural
language**:
- each option is a goal represented only by a one-sentence description;
- the decider sees neither the goals' training examples nor any fine-tuning;
- each question is a System One `choice` question (the `noul` and `score` types are not used).

```json
{
  "state": {"body": "<customer message>"},
  "questions": {
    "goal": {
      "type": "choice",
      "instructions": "Qual é o objetivo do cliente nesta mensagem?",
      "criteria": {"<goal key>": "<goal description>", "...": "... (K = 10)"}
    }
  },
  "model": "multilingual",
  "lang": "pt"
}
```

The output used is the `probabilities` distribution over the K options. The `model` and
`lang` fields are sent to Laya only; the Strands Decider ignores them.

## Two-stage pipeline

1. **Retrieval (shortlist).**
   - Messages and examples are embedded with an instruction prefix applied to every text
     (`Instruct: Identify the customer's goal in this message\nQuery: ` for Qwen3-Embedding)
     and L2-normalised.
   - The similarity of message `m` to goal `g` is `s_g = max_e cos(m, e)` over the examples
     `e` of `g`.
   - The K = 10 goals with the highest `s_g` form the shortlist.
2. **Decision.** The decider receives the `choice` question with the shortlisted goals in
   the **presented order** (see *Option order*) and returns `p_g`.
3. **Combination.**
   `P(g) = softmax_g((a · log max(p_g, 10⁻⁶) + b · s_g) / T)`.
   - The prediction is `argmax_g P(g)`, which does not depend on `T`.
   - `T` only affects calibration.

## Option order

Presenting the shortlist by decreasing similarity, as a production pipeline would, places
the true goal first whenever the embeddings alone are right. A decider with a position prior
then reaches the embeddings' accuracy without using the text. Three orders are therefore
supported:

| Order | Use |
|---|---|
| `random` | **Default for reported results.** Uniform permutation per phrase, seeded. |
| `similarity` | The production order. Measures the gain a deployment would see, including any position effect. |
| `reversed` | Adversarial control: the most similar goal comes last. |

Every report includes two rates: the `first_option` baseline (accuracy of always taking the
first presented option) and how often the decider picks the first option.

## Dataset

`data/goals_ptbr.jsonl` (see [`data/README.md`](../data/README.md)):
- **Goals:** 30 customer-service goals. Each has a key, a name and a one-sentence
  description (median 10.5 words).
- **Training examples:** 10 per goal (300 in total). They are used for similarity and for
  fitting.
- **Test phrases:** 5 per goal (150 in total, median 6 words). They are disjoint from the
  examples; the loader enforces it.

All phrases are synthetic and labelled at generation time. There is no independent human
annotation.

## Conditions

All conditions are evaluated on the 150 test phrases, over the same shortlist:

| Condition | Definition |
|---|---|
| `shortlist_recall` | True goal ∈ shortlist. Upper bound of every other row. |
| `first_option` | Always the first presented option. |
| `embeddings_alone` | `argmax s_g` (that is, `a = 0`). |
| `classifier_alone` | `argmax p_g` (that is, `b = 0`). Ties go to the earlier presented option. |
| `fitted_platform_grid` | `(a, b, T)` fitted by cross-validation on the examples, with `a ∈ {0.5, 1, 2}` (the decider always contributes). |
| `fitted_grid_with_zero` | The same, with `a ∈ {0, 0.5, 1, 2}`. |
| `oracle_on_test` | `(a, b)` chosen on the test phrases themselves. **Optimistic ceiling, not a result.** |

**Fitting:**
- **Folds:** 5-fold cross-validation on the 300 examples. Each goal's examples are shuffled
  with the run seed and dealt round-robin, so there are 2 examples per goal per fold.
- **Similarity during fitting:** an example in fold `f` is scored against the examples of
  the other folds only (of every goal), and its shortlist and decider answer are computed
  under that restriction.
- **Grid:** `b ∈ {0, 1, 2, 4, 8}`, `T ∈ {0.25, 0.5, 0.75, 1, 1.5, 2, 3}`; `(a, b) = (0, 0)`
  is excluded.
- **Objective:** minimum mean negative log-likelihood of the true goal. A true goal outside
  the shortlist costs `log 10⁻⁶`.

## Metrics and statistics

- **Accuracy (top-1):** reported with 95% Wilson score intervals. With n = 150, the
  half-width is between 3 and 8 percentage points.
- **Paired comparisons:** between runs on the same phrases (for example two deciders with
  the same seed and order), using the exact two-sided McNemar test on the discordant pairs.
- **Seeds:** at least three. A seed changes both the fold assignment and, under `random`, the
  option permutation. Report mean and spread across seeds.
- **Latency of the decider:**
  - client-side wall-clock time of one HTTP request with one phrase, covering
    serialisation, transport and inference, but not embedding;
  - 150 sequential requests, with no concurrency and no discarded warm-up;
  - median, p95 (nearest rank, the ⌈0.95·n⌉-th smallest value) and maximum.

## Reproducibility

Each run stores:
- the dataset SHA-256;
- the embedding model and its instruction prefix;
- the decider's `/health` payload (model, checkpoint revision, device);
- the protocol (shortlist size, order, seed, folds);
- one line per phrase with all raw signals.

The analysis (`goalbench report`) is deterministic given these files. Embeddings are cached
per model and text; shipping the cache alongside the results allows the analysis, and new
decider runs, to be repeated without the embedding server.

## Threats to validity

1. **Synthetic, single-author data.**
   - **Source:** phrases and labels come from one language model, with no independent human
     review.
   - **Risks:** the style may be cleaner and more homogeneous than real messages, and label
     ambiguity is not measured (no inter-annotator agreement).
2. **Small scale.**
   - **Size:** 30 goals and 150 test phrases, in one domain (banking, telecom and retail
     customer service).
   - **Consequence:** differences below about 8 percentage points are not distinguishable
     from interval overlap alone; use the paired test.
3. **Off-the-shelf checkpoints.**
   - **No adaptation:** neither decider is fine-tuned to the domain.
   - **Laya calibration:** the Laya checkpoint ships uncalibrated temperatures (1.0).
   - **Scope:** results describe these checkpoints, not the architectures' potential.
4. **Unpinned base model.** `strands-decider` 0.1.0 resolves its base model
   (`Qwen/Qwen3.5-2B-Base`) from the default branch.
5. **Hardware and numerical differences.** Accuracy can change slightly across GPUs.
   Latency depends on hardware and on local HTTP, and is not end-to-end production latency.
