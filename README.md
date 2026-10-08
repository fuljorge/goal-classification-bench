# goalbench

A reproducible benchmark for **customer-goal classification in Brazilian Portuguese** with
small "decider" models that answer typed `choice` questions:

- [Laya](https://github.com/NandhaKishorM/laya) (`laya-multilingual`, mmBERT-base encoder);
- [Strands Decider](https://github.com/strands-labs/strands-decider)
  (`strands-decider-2B-hobson-v21`, Qwen3.5-2B base with LoRA and a pointer head).

Both are compared inside the same two-stage pipeline used by goal-oriented conversational
agents:
1. an embedding model shortlists the 10 goals most similar to the message;
2. the decider picks one of them;
3. the two signals are combined and calibrated.

Every call is logged per phrase, so all conditions and statistics are recomputed offline.

- **Method:** [`docs/method.md`](docs/method.md).
- **Dataset card:** [`data/README.md`](data/README.md).
- **Results:** [`docs/results.md`](docs/results.md), with raw logs in
  [`results/v0.1.0/`](results/v0.1.0/).

## Results at a glance (v0.1.0)

Top-1 accuracy on 150 held-out phrases, 10-goal shortlist, random option order, mean ± SD
over 3 seeds. Latency is the p95 of one decider request on an RTX 5080.

| Embeddings | Embeddings alone | Laya alone | Strands Decider alone | Decider + embeddings (CV-fitted) | p95 Laya / Decider |
|---|---|---|---|---|---|
| Qwen3-Embedding-0.6B | 81.3% | 51.8 ± 2.5% | 84.9 ± 1.4% | 85.8 ± 0.4% | 34 / 135 ms |
| Qwen3-Embedding-4B | **94.7%** | 50.9 ± 1.5% | 85.8 ± 1.4% | 89.6 ± 0.8% | 41 / 173 ms |

- **Decider vs Laya:** the Strands Decider beats Laya by 33–35 points (exact McNemar
  p < 10⁻¹⁰), and its accuracy does not depend on option order. Laya prefers the first
  option.
- **4B embeddings:** similarity to 10 examples per goal is the best single signal, and no
  decider improves on it.
- **0.6B embeddings:** the Decider adds about 4.5 points, which is not significant at
  n = 150.

## What is measured

On the held-out test phrases, always over the same 10-goal shortlist:

| Condition | Meaning |
|---|---|
| `shortlist_recall` | The true goal is in the shortlist. This is the upper bound of every other row. |
| `first_option` | Always pick the first presented option. This is the position baseline. |
| `embeddings_alone` | Argmax of the embedding similarity. |
| `classifier_alone` | Argmax of the decider's distribution. |
| `fitted_platform_grid` | `P(g) ∝ exp((a·log p_g + b·s_g)/T)`, with `(a, b, T)` fitted by 5-fold CV on the training examples and `a > 0`. |
| `fitted_grid_with_zero` | The same fit, with `a = 0` allowed, so the decider may be ignored. |
| `oracle_on_test` | `(a, b)` chosen on the test phrases. An optimistic ceiling, not a result. |

Each condition reports accuracy with a 95% Wilson interval. The report also gives:
- how often the decider picks the first option;
- the latency of one decider request (median, p95 and max);
- exact McNemar tests between runs on the same phrases.

**Why option order matters.** A production pipeline presents the shortlist in similarity
order, so the true goal is usually first. In that case, a decider with a position prior
scores as well as the embeddings without understanding anything. Runs therefore default to
`--order random`, and `similarity` and `reversed` are available as controls.

## Quick start

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/). You also need:
- an OpenAI-compatible `/embeddings` endpoint, for example LM Studio, vLLM, Ollama or
  text-embeddings-inference, serving `Qwen3-Embedding-0.6B` or `-4B`;
- the deciders served as described in [`servers/`](servers/README.md).

```sh
uv sync
uv run pytest                      # unit and end-to-end tests with in-process fakes

export GOALBENCH_EMBEDDINGS_KEY=...   # optional, if the endpoint needs a key
export GOALBENCH_CLASSIFIER_TOKEN=... # token of the decider server

# Laya: three seeds, random option order
uv run goalbench run --label laya-multilingual \
  --classifier-url http://127.0.0.1:8300 --classifier-model multilingual --lang pt \
  --embeddings-url http://127.0.0.1:1234/v1/embeddings \
  --embeddings-model text-embedding-qwen3-embedding-0.6b \
  --order random --seed 0 1 2

# Strands Decider: same phrases, same seeds
uv run goalbench run --label strands-decider-2B-hobson-v21 \
  --classifier-url http://127.0.0.1:8301 \
  --embeddings-url http://127.0.0.1:1234/v1/embeddings \
  --embeddings-model text-embedding-qwen3-embedding-0.6b \
  --order random --seed 0 1 2

uv run goalbench report results/*seed0          # Markdown tables and McNemar tests
uv run goalbench report results/* --json > results/summary.json
```

**Secrets:** they are read from environment variables, whose names can be changed with
`--embeddings-key-env` and `--classifier-token-env`. They never reach run files or reports.

**Embedding cache:** embeddings are cached in `.cache/embeddings-<model>.npz`. Later runs,
with other seeds, orders or deciders, reuse exactly the same vectors.

## Run files

```
results/<label>__<embedding model>__<order>__seed<seed>/
  run.json     configuration, dataset SHA-256, versions, decider /health
  items.jsonl  one line per phrase:
               split ("cv" | "test"), goal, text, fold, similarity to every goal,
               shortlist, presented order, decider probabilities, latency_ms
```

## Reproducing the reference environment

| Component | Version |
|---|---|
| Laya | `laya[serve]==0.4.0`, checkpoint `convaiinnovations/laya` / `multilingual` @ `7b928d8` |
| Strands Decider | `strands-decider==0.1.0`, `StrandsAgents/strands-decider-2B-hobson-v21` @ `2b52a62` (base model not pinned by 0.1.0) |
| PyTorch | 2.14.0 (`cu130` for Blackwell GPUs, `cu126` otherwise) |
| GPU | NVIDIA RTX 5080 16 GB, driver 617.14, Windows 11 |

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

- **Code:** Apache-2.0 ([`LICENSE`](LICENSE)).
- **Dataset:** [`data/goals_ptbr.jsonl`](data/goals_ptbr.jsonl), under CC BY 4.0 (see the
  dataset card).
- **Third-party components:** Laya, Strands Decider, Qwen3.5 and Qwen3-Embedding are
  Apache-2.0 and are downloaded, not redistributed.
