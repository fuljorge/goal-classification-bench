# Results v0.2.0 (2026-10-08): language comparison

This folder holds 30 English runs, in `en/`, analysed together with the 20 Brazilian
Portuguese runs of [`../v0.1.0/`](../v0.1.0/). The results are in
[`docs/results-language.md`](../../docs/results-language.md).

| Path | Content |
|---|---|
| `en/<label>__<embedding model>__<order>__seed<seed>/` | 3 deciders (Laya multilingual, Laya English, Strands Decider) × 2 embedding models × (random seeds 0–2 + similarity + reversed), on `data/goals_en.jsonl` |
| `embeddings/` | Embedding cache covering both datasets (PT-BR and EN texts) |
| `report.md`, `summary.json` | Joint analysis of the 50 runs, including the cross-language paired tests |

## Recompute

```sh
uv run goalbench report results/v0.1.0/*__* results/v0.2.0/en/*__* --cross-dataset \
  --compare classifier_alone fitted_grid_with_zero embeddings_alone \
  --within fitted_grid_with_zero:embeddings_alone fitted_platform_grid:embeddings_alone \
           classifier_alone:embeddings_alone
```

## How the English runs were collected

```sh
Q="What is the customer's goal in this message?"
# For each EMB in text-embedding-qwen3-embedding-0.6b, text-embedding-qwen3-embedding-4b
# and each order spec in "random 0 1 2", "similarity 0", "reversed 0":
goalbench run --data data/goals_en.jsonl --instructions "$Q" \
  --label laya-multilingual --classifier-url http://127.0.0.1:8300 \
  --classifier-model multilingual --lang en \
  --embeddings-url <LM Studio /v1/embeddings> --embeddings-model $EMB \
  --order <order> --seed <seeds> --out results/v0.2.0/en
#   ...the same with --label laya-english --classifier-model english
#   ...and with --label strands-decider-2B-hobson-v21 --classifier-url http://127.0.0.1:8301
#      (without --classifier-model and --lang)
```

The Laya server was started with both checkpoints: `LAYA_MODELS=english,multilingual` and
`LAYA_MAX_LOADED=2`. Its routing confirmed that the `model` field selected each checkpoint
explicitly.
