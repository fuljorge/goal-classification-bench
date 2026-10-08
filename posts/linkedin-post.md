# LinkedIn post

Plain text (LinkedIn does not render Markdown). Attach `linkedin-carousel.pt-BR.pdf` as a document, or
`docs/figures/figure1-accuracy-by-language.png` as an image. Put the links (dev.to post, repository, DOI) in the first
comment, not in the post body.

## Português

Seu classificador de intenções é 12 pontos pior em português.

Medi como pequenos modelos de decisão classificam o objetivo do cliente em mensagens de atendimento em PT-BR. Depois traduzi tudo para o inglês e rodei de novo, frase a frase.

O que encontrei:

→ O Strands Decider (2B) acerta 85%. O Laya multilíngue, 52%.
→ Um bom modelo de embeddings sozinho (Qwen3-Embedding-4B) chega a 94,7%. Nenhum modelo de decisão melhorou isso.
→ Nas mesmas frases, todos os componentes acertam menos em português. O pipeline completo perde 8,4 pontos.
→ O maior efeito: o checkpoint em inglês do Laya é 24 pontos melhor que o multilíngue. Para português, não existe checkpoint próprio.

E uma armadilha: em produção, as opções vão ordenadas por semelhança, e o certo costuma ser a primeira. Um modelo que só "gosta" da primeira opção parece ótimo sem ler nada. Teste sempre com as opções embaralhadas.

Conclusão: avalie no idioma dos seus usuários. E, para português, o caminho é fine-tuning. Esse é o meu próximo experimento.

Tudo é reprodutível: código, dados e os registros das 50 execuções estão abertos, com DOI no Zenodo.

Post completo e repositório nos comentários.

#IA #NLP #PLN #LLM #MachineLearning

## English

Your intent classifier is 12 points worse in Portuguese.

I measured how small decider models classify the customer's goal in Brazilian Portuguese customer-service messages. Then I translated everything into English and ran it again, phrase by phrase.

What I found:

→ The Strands Decider (2B) gets 85% right. Laya multilingual, 52%.
→ A good embedding model on its own (Qwen3-Embedding-4B) reaches 94.7%. No decider improved on it.
→ On the same phrases, every component is less accurate in Portuguese. The full pipeline loses 8.4 points.
→ The biggest effect: Laya's English checkpoint is 24 points better than its multilingual one. There is no Portuguese checkpoint.

And a trap: in production, options are sorted by similarity, so the right one is usually first. A model that just "likes" the first option looks great without reading anything. Always test with shuffled options.

Takeaway: evaluate in your users' language. And for Portuguese, the path is fine-tuning. That's my next experiment.

It's all reproducible: code, data and the logs of all 50 runs are open, with a DOI on Zenodo.

Full write-up and repository in the comments.

#AI #NLP #LLM #MachineLearning #Benchmark

## First comment (both versions)

Post completo / full write-up: <dev.to link>
Repositório / repository: https://github.com/fuljorge/goal-classification-bench
DOI: https://doi.org/10.5281/zenodo.23233352
