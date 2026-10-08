---
title: "Your intent classifier is 12 points worse in Portuguese: benchmarking Laya, Strands Decider and Qwen3 embeddings"
published: false
description: "A reproducible benchmark of small choice deciders and embeddings for customer-goal classification in Brazilian Portuguese, plus what a parallel English translation reveals about the cost of language."
tags: ai, machinelearning, nlp, python
series: Goal classification in Brazilian Portuguese
---

A conversational agent first has to decide what the customer wants. I measured that step for customer-service messages in Brazilian Portuguese (PT-BR), using two small "decider" models and two embedding models. Then I translated the whole dataset into English and ran everything again.

## TL;DR

- **Decider vs Laya.** Off the shelf, the **Strands Decider (2B)** gets **84.9–85.8%** top-1 accuracy, against **50.9–51.8%** for **Laya multilingual**. Its accuracy does not depend on how the options are ordered.
- **Embeddings alone win.** **Qwen3-Embedding-4B** similarity, with no decider at all, reaches **94.7%**, and no decider improves on it.
- **The Portuguese tax.** Every component is less accurate in PT-BR than on the same phrases in English. The 0.6B embeddings lose **12 points** (p = 0.0014), and the full Decider pipeline loses **8.4 points**.
- **The checkpoint's language is the biggest lever.** Laya's **English** checkpoint beats its **multilingual** sibling by **24 points** on English text. Laya has no Portuguese checkpoint, which makes a case for PT-BR fine-tuning.

![Top-1 accuracy by component, PT-BR (blue) vs English (grey)](https://raw.githubusercontent.com/fuljorge/goal-classification-bench/d18b7d4fb7852d59588f3abcfbdceaa11f32d57d/docs/figures/figure1-accuracy-by-language.png)

*Figure 1. Top-1 accuracy in PT-BR (blue) and in a line-by-line English translation (grey). Bold differences are significant in every seed (exact McNemar test).*

## The problem: picking the customer's goal

Goal-oriented agents route each message to one of many **goals** ("pay a bill", "block a card", "talk to a human"). Each goal is defined by a one-line description and a few example phrases. The decision gates everything after it:

- **High confidence:** the agent acts.
- **Middle band:** it asks for confirmation.
- **Low confidence:** it asks a clarifying question.

So you want two things from the classifier: accuracy, and probabilities you can trust.

A new class of small models is built exactly for this. **[Laya](https://github.com/NandhaKishorM/laya)** and the **[Strands Decider](https://github.com/strands-labs/strands-decider)** answer typed questions ("pick one of these N options") and return a probability per option from a dedicated head, instead of generating text. Most of their published evaluations are in English. I wanted to know how they behave in Portuguese.

## How the benchmark works

The setup mirrors a production pipeline:

1. **Shortlist.** An embedding model (Qwen3-Embedding 0.6B or 4B) scores the message against each goal's examples. The 10 most similar goals become the options.
2. **Decide.** The decider gets a `choice` question with those 10 goal descriptions and returns a probability for each.
3. **Combine.** The two signals are mixed and calibrated:

{% katex %}
P(g) = \operatorname{softmax}_g\left(\frac{a \log p_g + b\, s_g}{T}\right)
{% endkatex %}

With `a = 0` you trust only the embeddings; with `b = 0`, only the decider. The weights `(a, b, T)` are fitted by 5-fold cross-validation on the goals' training examples, never on the test phrases.

**The dataset:**

- 30 goals from banking, telecom and retail;
- 10 training examples per goal;
- 150 held-out test phrases;
- a line-by-line English translation (same goals, same order, same phrase positions), so every comparison across languages is paired phrase by phrase.

### The trap: option order

In production, you naturally present the shortlist **sorted by similarity**. That means the right answer is usually the *first* option. A decider that simply prefers the first option would then look exactly as good as your embeddings, without reading the message at all.

So every configuration runs three ways:

- **random order**, with 3 seeds (the main results);
- **similarity order** (what production does);
- **reversed order** (the right answer tends to be last).

That control mattered. Laya multilingual picks the first option in **62%** of similarity-ordered questions and loses **11 points** when the order is reversed (p = 0.0015). The Strands Decider barely notices: only **4 of 150** phrases change outcome.

## Results in Brazilian Portuguese

Random option order, mean ± SD over 3 seeds:

| | 0.6B embeddings | 4B embeddings |
|---|---|---|
| Embeddings alone | 81.3% | **94.7%** |
| Laya multilingual alone | 51.8 ± 2.5% | 50.9 ± 1.5% |
| Strands Decider alone | **84.9 ± 1.4%** | 85.8 ± 1.4% |
| Strands Decider + embeddings (fitted) | 85.8 ± 0.4% | 89.6 ± 0.8% |
| Decider p95 latency (RTX 5080) | 135 ms | 173 ms |
| Laya p95 latency | 34 ms | 41 ms |

What stands out:

- **Laya is below the embeddings it is supposed to complement.** Forcing it into the combination costs 23–31 points; the fit only works if it can set `a = 0` and ignore Laya.
- **The Decider helps a weak retriever, not a strong one.** With 0.6B embeddings it adds about 4.5 points (consistent across seeds, not significant at n = 150). With 4B embeddings, the embeddings alone are significantly *better* than the Decider alone.
- **Cross-validated fitting can fool you.** With 4B embeddings, fitting on the examples always chose to use the Decider, and lost about 5 points against ignoring it. Inside cross-validation each example is compared against 8 examples per goal instead of 10. That weakens the similarity signal and makes the decider look more useful than it is.

## The cost of language

Same models, same phrases, translated into English (paired McNemar tests):

| Component | PT-BR | English | Δ |
|---|---|---|---|
| Embeddings alone, 0.6B | 81.3% | 93.3% | **+12.0** (p = 0.0014) |
| Embeddings alone, 4B | 94.7% | 98.0% | +3.3 (n.s.) |
| Strands Decider + 0.6B embeddings | 85.8% | 94.2% | **+8.4** (p ≤ 0.004) |
| Strands Decider + 4B embeddings | 89.6% | 95.3% | **+5.7** (p ≤ 0.039) |
| Laya multilingual alone | 51.8% | 57.6% | +5.8 |
| **Laya English checkpoint alone** | — | **81.6%** | **+24 over multilingual** |

The last row is the one I keep coming back to. Laya's English and multilingual checkpoints come from the same release and share an architecture. On English text, training for one language instead of many is worth **24 points**, the largest effect in the whole study. For Portuguese, the only option is the multilingual checkpoint, at about 51%.

## What this means for your agent

1. **Spend on the embedding model first.** With 10 examples per goal, a good embedding model was the single best component in both languages.
2. **Test deciders with shuffled options.** Production order silently rewards models that just like the first option.
3. **Tune the combination on held-out phrases**, not on your goals' examples.
4. **Evaluate in your users' language.** An English evaluation overstated PT-BR accuracy for every component.
5. **If you use a decider in PT-BR, plan to fine-tune it.** The 24-point gap between Laya's checkpoints shows how much a language-specific model can recover. That is my next experiment.

## Reproduce it

Everything is open: the code, both datasets, the server images for both deciders, and the raw per-phrase logs of all 50 runs. You can recompute every number above **without a GPU or any model server**:

```bash
git clone https://github.com/fuljorge/goal-classification-bench
cd goal-classification-bench
uv sync
uv run goalbench report results/v0.1.0/*__* results/v0.2.0/en/*__* --cross-dataset
```

To run new deciders or models, the `servers/` folder has Docker images and plain-venv instructions for both deciders, and `goalbench run` takes any OpenAI-compatible embeddings endpoint.

{% github fuljorge/goal-classification-bench %}

## Caveats

- **Synthetic data.** The dataset was written by a language model, so absolute numbers are likely optimistic. The paired comparisons are more robust, because every system sees the same phrases.
- **Translated English.** The English set is a translation, so part of the Portuguese gap may come from translation regularity rather than the language itself.
- **Small n.** 150 test phrases resolve differences of roughly 8 points or more. Smaller gaps here are consistent but not significant.

The full write-up, with the methodology, all paired tests and threats to validity, is archived with the code on Zenodo: [doi:10.5281/zenodo.23233352](https://doi.org/10.5281/zenodo.23233352).

*Next in this series: fine-tuning a decider for Brazilian Portuguese, and whether it closes the gap.*
