| Decider | Embeddings | Order | Seeds | shortlist_recall | first_option | embeddings_alone | classifier_alone | fitted_platform_grid | fitted_grid_with_zero | oracle_on_test |
|---|---|---|---|---|---|---|---|---|---|---|
| laya-multilingual | text-embedding-qwen3-embedding-0.6b | random | 0,1,2 | 98.0% ± 0.0 | 9.6% ± 2.5 | 81.3% ± 0.0 | 51.8% ± 2.5 | 58.4% ± 1.7 | 81.3% ± 0.0 | 81.3% ± 0.0 |
| laya-multilingual | text-embedding-qwen3-embedding-0.6b | reversed | 0 | 98.0% ± 0.0 | 0.0% ± 0.0 | 81.3% ± 0.0 | 44.7% ± 0.0 | 56.7% ± 0.0 | 81.3% ± 0.0 | 81.3% ± 0.0 |
| laya-multilingual | text-embedding-qwen3-embedding-0.6b | similarity | 0 | 98.0% ± 0.0 | 81.3% ± 0.0 | 81.3% ± 0.0 | 56.0% ± 0.0 | 61.3% ± 0.0 | 81.3% ± 0.0 | 81.3% ± 0.0 |
| laya-multilingual | text-embedding-qwen3-embedding-4b | random | 0,1,2 | 100.0% ± 0.0 | 10.4% ± 3.3 | 94.7% ± 0.0 | 50.9% ± 1.5 | 63.8% ± 1.7 | 94.7% ± 0.0 | 94.7% ± 0.0 |
| laya-multilingual | text-embedding-qwen3-embedding-4b | reversed | 0 | 100.0% ± 0.0 | 0.0% ± 0.0 | 94.7% ± 0.0 | 48.0% ± 0.0 | 64.7% ± 0.0 | 94.7% ± 0.0 | 94.7% ± 0.0 |
| laya-multilingual | text-embedding-qwen3-embedding-4b | similarity | 0 | 100.0% ± 0.0 | 94.7% ± 0.0 | 94.7% ± 0.0 | 54.0% ± 0.0 | 68.0% ± 0.0 | 94.7% ± 0.0 | 94.7% ± 0.0 |
| strands-decider-2B-hobson-v21 | text-embedding-qwen3-embedding-0.6b | random | 0,1,2 | 98.0% ± 0.0 | 9.6% ± 2.5 | 81.3% ± 0.0 | 84.9% ± 1.4 | 85.8% ± 0.4 | 85.8% ± 0.4 | 86.9% ± 0.4 |
| strands-decider-2B-hobson-v21 | text-embedding-qwen3-embedding-0.6b | reversed | 0 | 98.0% ± 0.0 | 0.0% ± 0.0 | 81.3% ± 0.0 | 84.7% ± 0.0 | 84.7% ± 0.0 | 84.7% ± 0.0 | 86.0% ± 0.0 |
| strands-decider-2B-hobson-v21 | text-embedding-qwen3-embedding-0.6b | similarity | 0 | 98.0% ± 0.0 | 81.3% ± 0.0 | 81.3% ± 0.0 | 84.7% ± 0.0 | 85.3% ± 0.0 | 85.3% ± 0.0 | 87.3% ± 0.0 |
| strands-decider-2B-hobson-v21 | text-embedding-qwen3-embedding-4b | random | 0,1,2 | 100.0% ± 0.0 | 10.4% ± 3.3 | 94.7% ± 0.0 | 85.8% ± 1.4 | 89.6% ± 0.8 | 89.6% ± 0.8 | 94.7% ± 0.0 |
| strands-decider-2B-hobson-v21 | text-embedding-qwen3-embedding-4b | reversed | 0 | 100.0% ± 0.0 | 0.0% ± 0.0 | 94.7% ± 0.0 | 85.3% ± 0.0 | 87.3% ± 0.0 | 87.3% ± 0.0 | 94.7% ± 0.0 |
| strands-decider-2B-hobson-v21 | text-embedding-qwen3-embedding-4b | similarity | 0 | 100.0% ± 0.0 | 94.7% ± 0.0 | 94.7% ± 0.0 | 86.7% ± 0.0 | 91.3% ± 0.0 | 91.3% ± 0.0 | 94.7% ± 0.0 |

| Run | shortlist_recall | first_option | embeddings_alone | classifier_alone | fitted_platform_grid | fitted_grid_with_zero | oracle_on_test | picks first | p50 / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed0 | 98.0% [94.3%, 99.3%] | 11.3% [7.2%, 17.4%] | 81.3% [74.3%, 86.8%] | 54.7% [46.7%, 62.4%] | 60.0% [52.0%, 67.5%] (a=0.5, b=8, T=1.5) | 81.3% [74.3%, 86.8%] (a=0, b=8, T=0.25) | 81.3% [74.3%, 86.8%] (a=0, b=1, T=1) | 16.0% | 31 / 35 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed1 | 98.0% [94.3%, 99.3%] | 6.7% [3.7%, 11.8%] | 81.3% [74.3%, 86.8%] | 50.7% [42.7%, 58.6%] | 58.7% [50.7%, 66.2%] (a=0.5, b=8, T=1.5) | 81.3% [74.3%, 86.8%] (a=0, b=8, T=0.25) | 81.3% [74.3%, 86.8%] (a=0, b=1, T=1) | 13.3% | 32 / 34 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed2 | 98.0% [94.3%, 99.3%] | 10.7% [6.7%, 16.6%] | 81.3% [74.3%, 86.8%] | 50.0% [42.1%, 57.9%] | 56.7% [48.7%, 64.3%] (a=0.5, b=8, T=1.5) | 81.3% [74.3%, 86.8%] (a=0, b=8, T=0.25) | 81.3% [74.3%, 86.8%] (a=0, b=1, T=1) | 14.0% | 31 / 34 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | 98.0% [94.3%, 99.3%] | 0.0% [0.0%, 2.5%] | 81.3% [74.3%, 86.8%] | 44.7% [36.9%, 52.7%] | 56.7% [48.7%, 64.3%] (a=0.5, b=8, T=1.5) | 81.3% [74.3%, 86.8%] (a=0, b=8, T=0.25) | 81.3% [74.3%, 86.8%] (a=0, b=1, T=1) | 10.0% | 31 / 43 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | 98.0% [94.3%, 99.3%] | 81.3% [74.3%, 86.8%] | 81.3% [74.3%, 86.8%] | 56.0% [48.0%, 63.7%] | 61.3% [53.3%, 68.8%] (a=0.5, b=8, T=1.5) | 81.3% [74.3%, 86.8%] (a=0, b=8, T=0.25) | 81.3% [74.3%, 86.8%] (a=0, b=1, T=1) | 62.0% | 35 / 50 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed0 | 100.0% [97.5%, 100.0%] | 12.7% [8.3%, 18.9%] | 94.7% [89.8%, 97.3%] | 50.0% [42.1%, 57.9%] | 64.0% [56.1%, 71.2%] (a=0.5, b=8, T=1.5) | 94.7% [89.8%, 97.3%] (a=0, b=8, T=0.25) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 14.0% | 35 / 47 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed1 | 100.0% [97.5%, 100.0%] | 6.7% [3.7%, 11.8%] | 94.7% [89.8%, 97.3%] | 50.0% [42.1%, 57.9%] | 62.0% [54.0%, 69.4%] (a=0.5, b=8, T=1.5) | 94.7% [89.8%, 97.3%] (a=0, b=8, T=0.25) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 14.0% | 31 / 43 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed2 | 100.0% [97.5%, 100.0%] | 12.0% [7.7%, 18.2%] | 94.7% [89.8%, 97.3%] | 52.7% [44.7%, 60.5%] | 65.3% [57.4%, 72.5%] (a=0.5, b=8, T=1.5) | 94.7% [89.8%, 97.3%] (a=0, b=8, T=0.25) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 15.3% | 30 / 33 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__reversed__seed0 | 100.0% [97.5%, 100.0%] | 0.0% [0.0%, 2.5%] | 94.7% [89.8%, 97.3%] | 48.0% [40.2%, 55.9%] | 64.7% [56.7%, 71.9%] (a=0.5, b=8, T=1.5) | 94.7% [89.8%, 97.3%] (a=0, b=8, T=0.25) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 8.0% | 34 / 48 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__similarity__seed0 | 100.0% [97.5%, 100.0%] | 94.7% [89.8%, 97.3%] | 94.7% [89.8%, 97.3%] | 54.0% [46.0%, 61.8%] | 68.0% [60.2%, 74.9%] (a=0.5, b=8, T=1.5) | 94.7% [89.8%, 97.3%] (a=0, b=8, T=0.25) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 56.7% | 31 / 42 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed0 | 98.0% [94.3%, 99.3%] | 11.3% [7.2%, 17.4%] | 81.3% [74.3%, 86.8%] | 83.3% [76.6%, 88.4%] | 86.0% [79.5%, 90.7%] (a=0.5, b=4, T=0.5) | 86.0% [79.5%, 90.7%] (a=0.5, b=4, T=0.5) | 86.7% [80.3%, 91.2%] (a=0.5, b=8, T=1) | 9.3% | 119 / 128 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed1 | 98.0% [94.3%, 99.3%] | 6.7% [3.7%, 11.8%] | 81.3% [74.3%, 86.8%] | 86.0% [79.5%, 90.7%] | 85.3% [78.8%, 90.1%] (a=0.5, b=4, T=0.5) | 85.3% [78.8%, 90.1%] (a=0.5, b=4, T=0.5) | 87.3% [81.1%, 91.7%] (a=0.5, b=8, T=1) | 7.3% | 131 / 157 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed2 | 98.0% [94.3%, 99.3%] | 10.7% [6.7%, 16.6%] | 81.3% [74.3%, 86.8%] | 85.3% [78.8%, 90.1%] | 86.0% [79.5%, 90.7%] (a=0.5, b=4, T=0.5) | 86.0% [79.5%, 90.7%] (a=0.5, b=4, T=0.5) | 86.7% [80.3%, 91.2%] (a=0.5, b=8, T=1) | 11.3% | 117 / 121 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | 98.0% [94.3%, 99.3%] | 0.0% [0.0%, 2.5%] | 81.3% [74.3%, 86.8%] | 84.7% [78.0%, 89.6%] | 84.7% [78.0%, 89.6%] (a=0.5, b=4, T=0.5) | 84.7% [78.0%, 89.6%] (a=0.5, b=4, T=0.5) | 86.0% [79.5%, 90.7%] (a=0.5, b=8, T=1) | 0.7% | 119 / 136 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | 98.0% [94.3%, 99.3%] | 81.3% [74.3%, 86.8%] | 81.3% [74.3%, 86.8%] | 84.7% [78.0%, 89.6%] | 85.3% [78.8%, 90.1%] (a=0.5, b=4, T=0.5) | 85.3% [78.8%, 90.1%] (a=0.5, b=4, T=0.5) | 87.3% [81.1%, 91.7%] (a=0.5, b=8, T=1) | 76.7% | 116 / 170 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed0 | 100.0% [97.5%, 100.0%] | 12.7% [8.3%, 18.9%] | 94.7% [89.8%, 97.3%] | 85.3% [78.8%, 90.1%] | 88.7% [82.6%, 92.8%] (a=0.5, b=8, T=0.5) | 88.7% [82.6%, 92.8%] (a=0.5, b=8, T=0.5) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 10.7% | 131 / 175 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed1 | 100.0% [97.5%, 100.0%] | 6.7% [3.7%, 11.8%] | 94.7% [89.8%, 97.3%] | 87.3% [81.1%, 91.7%] | 90.0% [84.2%, 93.8%] (a=0.5, b=8, T=0.5) | 90.0% [84.2%, 93.8%] (a=0.5, b=8, T=0.5) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 6.7% | 125 / 170 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed2 | 100.0% [97.5%, 100.0%] | 12.0% [7.7%, 18.2%] | 94.7% [89.8%, 97.3%] | 84.7% [78.0%, 89.6%] | 90.0% [84.2%, 93.8%] (a=0.5, b=8, T=0.5) | 90.0% [84.2%, 93.8%] (a=0.5, b=8, T=0.5) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 12.0% | 124 / 175 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__reversed__seed0 | 100.0% [97.5%, 100.0%] | 0.0% [0.0%, 2.5%] | 94.7% [89.8%, 97.3%] | 85.3% [78.8%, 90.1%] | 87.3% [81.1%, 91.7%] (a=0.5, b=8, T=0.5) | 87.3% [81.1%, 91.7%] (a=0.5, b=8, T=0.5) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 0.0% | 119 / 154 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__similarity__seed0 | 100.0% [97.5%, 100.0%] | 94.7% [89.8%, 97.3%] | 94.7% [89.8%, 97.3%] | 86.7% [80.3%, 91.2%] | 91.3% [85.7%, 94.9%] (a=0.5, b=8, T=0.5) | 91.3% [85.7%, 94.9%] (a=0.5, b=8, T=0.5) | 94.7% [89.8%, 97.3%] (a=0, b=1, T=1) | 82.7% | 117 / 128 |

| Condition | First | Second | Only first | Only second | McNemar p |
|---|---|---|---|---|---|
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed0 | 3 | 46 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed1 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed1 | 6 | 59 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed2 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed2 | 5 | 58 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | 5 | 65 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | 2 | 45 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed0 | 3 | 56 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed1 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed1 | 3 | 59 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed2 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed2 | 4 | 52 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-4b__reversed__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__reversed__seed0 | 4 | 60 | 0.0000 |
| classifier_alone | laya-multilingual__text-embedding-qwen3-embedding-4b__similarity__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__similarity__seed0 | 4 | 53 | 0.0000 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed0 | 10 | 17 | 0.2478 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed1 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed1 | 10 | 16 | 0.3269 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed2 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed2 | 9 | 16 | 0.2295 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | 12 | 17 | 0.4583 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | 10 | 16 | 0.3269 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed0 | 15 | 6 | 0.0784 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed1 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed1 | 13 | 6 | 0.1671 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed2 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed2 | 13 | 6 | 0.1671 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-4b__reversed__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__reversed__seed0 | 17 | 6 | 0.0347 |
| fitted_grid_with_zero | laya-multilingual__text-embedding-qwen3-embedding-4b__similarity__seed0 | strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__similarity__seed0 | 11 | 6 | 0.3323 |

| Run | First | Second | Only first | Only second | McNemar p |
|---|---|---|---|---|---|
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed0 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed1 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed2 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed0 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed1 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed2 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__reversed__seed0 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__similarity__seed0 | fitted_grid_with_zero | embeddings_alone | 0 | 0 | 1.0000 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed0 | fitted_grid_with_zero | embeddings_alone | 17 | 10 | 0.2478 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed1 | fitted_grid_with_zero | embeddings_alone | 16 | 10 | 0.3269 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed2 | fitted_grid_with_zero | embeddings_alone | 16 | 9 | 0.2295 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | fitted_grid_with_zero | embeddings_alone | 17 | 12 | 0.4583 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | fitted_grid_with_zero | embeddings_alone | 16 | 10 | 0.3269 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed0 | fitted_grid_with_zero | embeddings_alone | 6 | 15 | 0.0784 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed1 | fitted_grid_with_zero | embeddings_alone | 6 | 13 | 0.1671 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed2 | fitted_grid_with_zero | embeddings_alone | 6 | 13 | 0.1671 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__reversed__seed0 | fitted_grid_with_zero | embeddings_alone | 6 | 17 | 0.0347 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__similarity__seed0 | fitted_grid_with_zero | embeddings_alone | 6 | 11 | 0.3323 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed0 | fitted_platform_grid | embeddings_alone | 5 | 37 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed1 | fitted_platform_grid | embeddings_alone | 5 | 39 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed2 | fitted_platform_grid | embeddings_alone | 5 | 42 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | fitted_platform_grid | embeddings_alone | 4 | 41 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | fitted_platform_grid | embeddings_alone | 3 | 33 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed0 | fitted_platform_grid | embeddings_alone | 0 | 46 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed1 | fitted_platform_grid | embeddings_alone | 0 | 49 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed2 | fitted_platform_grid | embeddings_alone | 1 | 45 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__reversed__seed0 | fitted_platform_grid | embeddings_alone | 0 | 45 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__similarity__seed0 | fitted_platform_grid | embeddings_alone | 0 | 40 | 0.0000 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed0 | fitted_platform_grid | embeddings_alone | 17 | 10 | 0.2478 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed1 | fitted_platform_grid | embeddings_alone | 16 | 10 | 0.3269 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed2 | fitted_platform_grid | embeddings_alone | 16 | 9 | 0.2295 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | fitted_platform_grid | embeddings_alone | 17 | 12 | 0.4583 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | fitted_platform_grid | embeddings_alone | 16 | 10 | 0.3269 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed0 | fitted_platform_grid | embeddings_alone | 6 | 15 | 0.0784 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed1 | fitted_platform_grid | embeddings_alone | 6 | 13 | 0.1671 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed2 | fitted_platform_grid | embeddings_alone | 6 | 13 | 0.1671 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__reversed__seed0 | fitted_platform_grid | embeddings_alone | 6 | 17 | 0.0347 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__similarity__seed0 | fitted_platform_grid | embeddings_alone | 6 | 11 | 0.3323 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed0 | classifier_alone | embeddings_alone | 5 | 45 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed1 | classifier_alone | embeddings_alone | 4 | 50 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__random__seed2 | classifier_alone | embeddings_alone | 6 | 53 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | classifier_alone | embeddings_alone | 5 | 60 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | classifier_alone | embeddings_alone | 3 | 41 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed0 | classifier_alone | embeddings_alone | 0 | 67 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed1 | classifier_alone | embeddings_alone | 0 | 67 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__random__seed2 | classifier_alone | embeddings_alone | 1 | 64 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__reversed__seed0 | classifier_alone | embeddings_alone | 0 | 70 | 0.0000 |
| laya-multilingual__text-embedding-qwen3-embedding-4b__similarity__seed0 | classifier_alone | embeddings_alone | 0 | 61 | 0.0000 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed0 | classifier_alone | embeddings_alone | 17 | 14 | 0.7201 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed1 | classifier_alone | embeddings_alone | 17 | 10 | 0.2478 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__random__seed2 | classifier_alone | embeddings_alone | 16 | 10 | 0.3269 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__reversed__seed0 | classifier_alone | embeddings_alone | 17 | 12 | 0.4583 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-0.6b__similarity__seed0 | classifier_alone | embeddings_alone | 16 | 11 | 0.4421 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed0 | classifier_alone | embeddings_alone | 6 | 20 | 0.0094 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed1 | classifier_alone | embeddings_alone | 6 | 17 | 0.0347 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__random__seed2 | classifier_alone | embeddings_alone | 6 | 21 | 0.0059 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__reversed__seed0 | classifier_alone | embeddings_alone | 6 | 20 | 0.0094 |
| strands-decider-2b-hobson-v21__text-embedding-qwen3-embedding-4b__similarity__seed0 | classifier_alone | embeddings_alone | 6 | 18 | 0.0227 |

Conditions:
- `shortlist_recall`: true goal is in the shortlist (upper bound of every other row)
- `first_option`: always pick the first presented option (position baseline)
- `embeddings_alone`: argmax of the similarity (a = 0)
- `classifier_alone`: argmax of the classifier distribution (b = 0)
- `fitted_platform_grid`: (a, b, T) fitted by CV on the examples, a in {0.5, 1, 2}
- `fitted_grid_with_zero`: (a, b, T) fitted by CV on the examples, a in {0, 0.5, 1, 2}
- `oracle_on_test`: (a, b) chosen on the test phrases: optimistic ceiling, not a result
