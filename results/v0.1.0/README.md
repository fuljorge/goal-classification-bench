# Results v0.1.0 (2026-10-08)

This folder holds the 20 runs analysed in [`docs/results.md`](../../docs/results.md):

- 2 deciders × 2 embedding models;
- `random` order with seeds 0, 1 and 2;
- the `similarity` and `reversed` controls with seed 0.

| Path | Content |
|---|---|
| `<label>__<embedding model>__<order>__seed<seed>/run.json` | Configuration, dataset SHA-256, decider `/health` (checkpoint revision, device) |
| `<label>__<embedding model>__<order>__seed<seed>/items.jsonl` | One line per phrase (450 per run): similarity to every goal, shortlist, presented order, decider probabilities, latency |
| `embeddings/` | The exact L2-normalised vectors used, keyed by model, instruction and text |
| `report.md` | Per-run tables, paired tests between deciders, within-run tests |
| `summary.json` | The same as `report.md`, plus aggregates across seeds, in JSON |

## Recompute the analysis (no servers needed)

```sh
uv run goalbench report results/v0.1.0/*__* \
  --within fitted_grid_with_zero:embeddings_alone fitted_platform_grid:embeddings_alone \
           classifier_alone:embeddings_alone
```

## How the runs were collected

```sh
# For each EMB in text-embedding-qwen3-embedding-0.6b, text-embedding-qwen3-embedding-4b:

# Laya (servers/laya, port 8300)
goalbench run --label laya-multilingual --classifier-url http://127.0.0.1:8300 \
  --classifier-model multilingual --lang pt \
  --embeddings-url <LM Studio /v1/embeddings> --embeddings-model $EMB \
  --order random --seed 0 1 2 --out results/v0.1.0
#   ...and again with --order similarity --seed 0 and with --order reversed --seed 0

# Strands Decider (servers/strands-decider, port 8301)
goalbench run --label strands-decider-2B-hobson-v21 --classifier-url http://127.0.0.1:8301 \
  --embeddings-url <LM Studio /v1/embeddings> --embeddings-model $EMB \
  --order random --seed 0 1 2 --out results/v0.1.0
#   ...and the same two controls
```

To repeat the decider calls without an embedding server, copy `embeddings/*.npz` to `.cache/`
(or pass `--embeddings-cache`). The client then finds every vector in the cache and never
calls `--embeddings-url`, although the flag is still required.
