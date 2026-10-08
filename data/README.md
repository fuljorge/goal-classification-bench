# Dataset card: `goals_ptbr.jsonl` and `goals_en.jsonl`

## Summary

`goals_ptbr.jsonl` is a small, synthetic intent-classification set in Brazilian Portuguese
for customer service.

| Item | Value |
|---|---|
| Goals | 30, covering banking, telecom and retail service: bills and invoices, cards, Pix, plans, deliveries, support, registration, complaints and others |
| Description | One sentence per goal |
| Training examples | 10 per goal, 300 in total |
| Test phrases | 5 per goal, 150 in total, disjoint from the examples |
| License | CC BY 4.0 |

## Format

One JSON object per line:

```json
{"key": "segunda_via_boleto",
 "name": "Segunda via de boleto",
 "description": "Cliente pede a segunda via de um boleto ou fatura para pagar.",
 "examples": ["quero a segunda via do boleto", "..."],
 "tests": ["o boleto não chegou, consegue reenviar?", "..."]}
```

## Provenance

- **How it was made:** written on 2026-10-07 by a large language model (an AI coding agent)
  while building a goal-classification feature, as an evaluation set for that feature.
- **What it contains:** every message is fictitious. No real customer data, names,
  documents or personal data are included.
- **Labels:** assigned at generation time. There was no independent human annotation and no
  inter-annotator agreement measurement.

## Intended use and limitations

- **Intended use:** benchmarking choice-style deciders and embedding shortlists for
  goal-oriented conversational agents. It is suited to comparative measurements with paired
  tests.
- **Not representative of real traffic:**
  - phrases are short (median 6 words), mostly single-intent and cleaner than real messages;
  - regional variation, typos and code-switching are under-represented.
- **Small:** 150 test phrases give 95% intervals of ±3 to ±8 percentage points.
- **Single generator:** a model trained on similar data may find it easier than real
  messages.

## `goals_en.jsonl`: parallel English translation

`goals_en.jsonl` is a line-by-line English translation of `goals_ptbr.jsonl`, made on
2026-10-08 by the same kind of AI agent for the language comparison in
[`docs/results-language.md`](../docs/results-language.md).

- **Structure:** same goals, same order, same number of phrases. Phrase i of goal g
  translates phrase i of goal g, and `ptbr_key` keeps the Portuguese key.
- **Localisation:** Brazil-specific terms are translated by meaning (Pix → instant transfer,
  boleto → payment slip, Procon → consumer protection agency, CNPJ → company tax ID, DANFE →
  electronic invoice document, consignado → payroll-deducted loan), keeping the
  informal, lower-case style.
- **Limitations:** it is translated text, not native customer English. It may be more
  explicit and regular than real messages ("translationese"), and its test phrases are
  longer (median 8 words, against 6).
- **License:** CC BY 4.0.
