---
title: "Seu classificador de intenções é 12 pontos pior em português: um benchmark de Laya, Strands Decider e embeddings Qwen3"
published: false
description: "Um benchmark reprodutível de pequenos modelos de decisão e de embeddings para classificar o objetivo do cliente em português do Brasil, e o que uma tradução paralela para o inglês revela sobre o custo do idioma."
tags: ai, machinelearning, nlp, braziliandevs
series: Classificação de objetivos em português do Brasil
---

A primeira coisa que um agente conversacional precisa fazer é entender o que o cliente quer. Medi essa etapa em mensagens de atendimento em português do Brasil, com dois pequenos modelos de "decisão" e dois modelos de embeddings. Depois traduzi o conjunto inteiro para o inglês e rodei tudo de novo.

## Resumo

- **Decider × Laya.** Sem nenhum ajuste, o **Strands Decider (2B)** acerta **84,9–85,8%** das frases (top-1), contra **50,9–51,8%** do **Laya multilíngue**. O acerto do Decider não depende da ordem em que as opções são apresentadas.
- **Os embeddings sozinhos vencem.** A semelhança do **Qwen3-Embedding-4B**, sem nenhum modelo de decisão, chega a **94,7%**, e nenhum modelo de decisão melhora esse número.
- **O imposto do português.** Todos os componentes acertam menos em português do que nas mesmas frases em inglês. Os embeddings 0.6B perdem **12 pontos** (p = 0,0014), e o pipeline completo com o Decider perde **8,4 pontos**.
- **O idioma do checkpoint é a maior alavanca.** O checkpoint **inglês** do Laya supera o **multilíngue** em **24 pontos** em texto em inglês. O Laya não tem checkpoint para português, o que reforça o caso para um fine-tuning em PT-BR.

![Acerto top-1 por componente, PT-BR (azul) × inglês (cinza)](https://raw.githubusercontent.com/fuljorge/goal-classification-bench/d18b7d4fb7852d59588f3abcfbdceaa11f32d57d/docs/figures/figure1-accuracy-by-language.png)

*Figura 1. Acerto top-1 em PT-BR (azul) e numa tradução frase a frase para o inglês (cinza). As diferenças em negrito são significativas em todas as sementes (teste exato de McNemar). Figura em inglês, como no artigo.*

## O problema: descobrir o objetivo do cliente

Agentes orientados a objetivos encaminham cada mensagem para um entre muitos **objetivos** ("pagar uma conta", "bloquear o cartão", "falar com um atendente"). Cada objetivo é definido por uma descrição de uma linha e algumas frases de exemplo. Essa decisão condiciona todo o resto:

- **Confiança alta:** o agente executa.
- **Faixa intermediária:** ele pede confirmação.
- **Confiança baixa:** ele faz uma pergunta para esclarecer.

Por isso, você quer duas coisas do classificador: acerto e probabilidades em que dá para confiar.

Uma nova classe de modelos pequenos foi feita exatamente para isso. O **[Laya](https://github.com/NandhaKishorM/laya)** e o **[Strands Decider](https://github.com/strands-labs/strands-decider)** respondem perguntas tipadas ("escolha uma destas N opções") e devolvem uma probabilidade por opção, a partir de uma camada dedicada, em vez de gerar texto. A maior parte das avaliações publicadas desses modelos é em inglês. Eu queria saber como eles se saem em português.

## Como o benchmark funciona

A montagem reproduz um pipeline de produção:

1. **Pré-seleção.** Um modelo de embeddings (Qwen3-Embedding 0.6B ou 4B) compara a mensagem com os exemplos de cada objetivo. Os 10 objetivos mais parecidos viram as opções.
2. **Decisão.** O modelo de decisão recebe uma pergunta `choice` com as descrições desses 10 objetivos e devolve uma probabilidade para cada um.
3. **Combinação.** Os dois sinais são combinados e calibrados:

{% katex %}
P(g) = \operatorname{softmax}_g\left(\frac{a \log p_g + b\, s_g}{T}\right)
{% endkatex %}

Com `a = 0`, você confia só nos embeddings; com `b = 0`, só no modelo de decisão. Os pesos `(a, b, T)` são ajustados por validação cruzada em 5 partes, usando os exemplos de treino dos objetivos e nunca as frases de teste.

**O conjunto de dados:**

- 30 objetivos de atendimento de banco, telecom e varejo;
- 10 exemplos de treino por objetivo;
- 150 frases de teste separadas;
- uma tradução frase a frase para o inglês (mesmos objetivos, mesma ordem, mesma posição de cada frase), para que toda comparação entre idiomas seja pareada, frase a frase.

### A armadilha: a ordem das opções

Em produção, o natural é apresentar a pré-seleção **ordenada por semelhança**. Isso significa que a resposta certa costuma ser a *primeira* opção. Um modelo de decisão que simplesmente prefira a primeira opção pareceria tão bom quanto os seus embeddings, sem ler a mensagem.

Por isso, cada configuração roda de três formas:

- **ordem aleatória**, com 3 sementes (os resultados principais);
- **ordem por semelhança** (o que a produção faz);
- **ordem inversa** (a resposta certa tende a ficar por último).

Esse controle fez diferença. O Laya multilíngue escolhe a primeira opção em **62%** das perguntas ordenadas por semelhança e perde **11 pontos** quando a ordem é invertida (p = 0,0015). O Strands Decider quase não percebe: só **4 das 150** frases mudam de resultado.

## Resultados em português

Ordem aleatória, média ± desvio-padrão em 3 sementes:

| | Embeddings 0.6B | Embeddings 4B |
|---|---|---|
| Embeddings sozinhos | 81,3% | **94,7%** |
| Laya multilíngue sozinho | 51,8 ± 2,5% | 50,9 ± 1,5% |
| Strands Decider sozinho | **84,9 ± 1,4%** | 85,8 ± 1,4% |
| Strands Decider + embeddings (ajustado) | 85,8 ± 0,4% | 89,6 ± 0,8% |
| Latência p95 do Decider (RTX 5080) | 135 ms | 173 ms |
| Latência p95 do Laya | 34 ms | 41 ms |

O que chama atenção:

- **O Laya fica abaixo dos embeddings que deveria complementar.** Forçá-lo na combinação custa de 23 a 31 pontos. O ajuste só funciona se puder usar `a = 0` e ignorar o Laya.
- **O Decider ajuda um recuperador fraco, não um forte.** Com os embeddings 0.6B, ele soma cerca de 4,5 pontos (de forma consistente nas sementes, mas sem significância com n = 150). Com os embeddings 4B, os embeddings sozinhos são significativamente *melhores* que o Decider sozinho.
- **A validação cruzada pode enganar.** Com os embeddings 4B, o ajuste feito nos exemplos sempre escolheu usar o Decider e perdeu cerca de 5 pontos em relação a ignorá-lo. Dentro da validação cruzada, cada exemplo é comparado com 8 exemplos por objetivo, e não 10. Isso enfraquece o sinal de semelhança e faz o modelo de decisão parecer mais útil do que é.

## O custo do idioma

Mesmos modelos, mesmas frases, traduzidas para o inglês (testes de McNemar pareados):

| Componente | PT-BR | Inglês | Δ |
|---|---|---|---|
| Embeddings sozinhos, 0.6B | 81,3% | 93,3% | **+12,0** (p = 0,0014) |
| Embeddings sozinhos, 4B | 94,7% | 98,0% | +3,3 (não significativo) |
| Strands Decider + embeddings 0.6B | 85,8% | 94,2% | **+8,4** (p ≤ 0,004) |
| Strands Decider + embeddings 4B | 89,6% | 95,3% | **+5,7** (p ≤ 0,039) |
| Laya multilíngue sozinho | 51,8% | 57,6% | +5,8 |
| **Checkpoint inglês do Laya sozinho** | — | **81,6%** | **+24 sobre o multilíngue** |

A última linha é a que mais me chama atenção. Os checkpoints inglês e multilíngue do Laya vêm da mesma versão e têm a mesma arquitetura. Em texto em inglês, treinar para um idioma em vez de muitos vale **24 pontos**, o maior efeito de todo o estudo. Para o português, a única opção é o checkpoint multilíngue, com cerca de 51%.

## O que isso significa para o seu agente

1. **Invista primeiro no modelo de embeddings.** Com 10 exemplos por objetivo, um bom modelo de embeddings foi o melhor componente isolado nos dois idiomas.
2. **Teste modelos de decisão com as opções embaralhadas.** A ordem de produção premia, sem ninguém perceber, modelos que simplesmente gostam da primeira opção.
3. **Ajuste a combinação com frases separadas para teste**, e não com os exemplos dos seus objetivos.
4. **Avalie no idioma dos seus usuários.** Uma avaliação em inglês superestimou o acerto em português para todos os componentes.
5. **Se for usar um modelo de decisão em português, planeje um fine-tuning.** A diferença de 24 pontos entre os checkpoints do Laya mostra quanto um modelo específico para o idioma pode recuperar. Esse é o meu próximo experimento.

## Reproduza você mesmo

Está tudo aberto: o código, os dois conjuntos de dados, as imagens dos servidores dos dois modelos de decisão e os registros brutos, frase a frase, das 50 execuções. Dá para recalcular todos os números acima **sem GPU e sem nenhum servidor de modelo**:

```bash
git clone https://github.com/fuljorge/goal-classification-bench
cd goal-classification-bench
uv sync
uv run goalbench report results/v0.1.0/*__* results/v0.2.0/en/*__* --cross-dataset
```

Para testar outros modelos, a pasta `servers/` tem imagens Docker e instruções com ambientes Python para os dois modelos de decisão, e o `goalbench run` aceita qualquer endpoint de embeddings compatível com a API da OpenAI.

{% github fuljorge/goal-classification-bench %}

## Ressalvas

- **Dados sintéticos.** O conjunto foi escrito por um modelo de linguagem, então os números absolutos provavelmente são otimistas. As comparações pareadas são mais robustas, porque todos os sistemas veem as mesmas frases.
- **Inglês traduzido.** O conjunto em inglês é uma tradução, então parte da diferença do português pode vir da regularidade da tradução, e não do idioma em si.
- **Amostra pequena.** 150 frases de teste distinguem diferenças a partir de uns 8 pontos. As diferenças menores daqui são consistentes, mas não significativas.

O artigo completo, com a metodologia, todos os testes pareados e as ameaças à validade, está arquivado junto com o código no Zenodo: [doi:10.5281/zenodo.23233352](https://doi.org/10.5281/zenodo.23233352).

*No próximo post da série: um fine-tuning de modelo de decisão para o português do Brasil, e se ele fecha essa diferença.*
