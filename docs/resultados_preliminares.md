# Resultados preliminares — OE1 (métricas de n-gramas)

Rodada de 25/09/2026, conversa **Coordenação**. Código em `src/`, reprodutível com:

```
git clone https://github.com/allenai/feb.git
python src/carregar_feb.py && python src/metricas_lexicais.py && python src/correlacoes.py
```

## Dados

- 4.320 julgamentos → 1.440 itens (4 modelos × 360), 3 anotadores por item, 563 posts distintos. Confirma os números do Passo 1.
- Análise restrita aos **720 itens ofensivos** (nos não ofensivos, gerada = referência em 100%).
- Novo: **16 itens ofensivos** em que a explicação gerada é cópia exata da referência (plausibilidade média 0,85).
- Convenção seguida (código do FEB): `Input.{k}_gt_idx = 0` → referência é a e1; `Input.gt_{k}` é o rótulo (0 = ofensivo). O comentário em compute_kappa.py troca os nomes das colunas; o código está certo.

## Duas variantes de texto

Quase todas as explicações começam com o molde "this post implies that". Esse trecho é idêntico entre gerada e referência e infla a sobreposição igualmente para todos os itens. Rodamos as métricas com o texto **completo** e **sem o prefixo**.

Após tirar o prefixo, **310 dos 720 itens (43%) têm ROUGE-L = 0**: as métricas de n-gramas não conseguem ordenar quase metade dos itens. Esses itens têm plausibilidade média 0,25, mas 8 deles receberam nota máxima dos humanos.

## Correlação por instância (n = 720, Kendall τ-b, IC 95% por bootstrap agrupado por post, B = 2000)

| Métrica | τ (completo) | IC 95% | τ (sem prefixo) | IC 95% | ρ Spearman (sem prefixo) |
|---|---|---|---|---|---|
| BLEU | 0,155 | [0,089; 0,222] | 0,188 | [0,124; 0,252] | 0,242 |
| ROUGE-1 | 0,179 | [0,116; 0,243] | 0,199 | [0,131; 0,263] | 0,254 |
| ROUGE-2 | 0,162 | [0,096; 0,229] | 0,155 | [0,082; 0,223] | 0,182 |
| ROUGE-L | 0,177 | [0,113; 0,241] | 0,199 | [0,132; 0,264] | 0,255 |
| METEOR | 0,163 | [0,098; 0,225] | 0,194 | [0,129; 0,258] | 0,252 |
| Comprimento (linha de base) | −0,003 | [−0,063; 0,062] | — | — | — |

- Todas as métricas de n-gramas têm correlação **fraca** (τ < 0,2), mas acima de zero e acima da linha de base de comprimento.
- As diferenças entre as métricas de n-gramas **não são significativas** (única exceção: ROUGE-1 > BLEU no texto completo, por margem mínima).
- Excluindo as 16 cópias exatas, τ cai para cerca de 0,16. Parte da correlação vem de poucos casos triviais.

### Por modelo (τ, sem prefixo)

| Métrica | GPT-3 | T5-3B | T5-large | T5-base |
|---|---|---|---|---|
| BLEU | 0,324 | 0,173 | 0,189 | 0,062 |
| ROUGE-L | 0,326 | 0,216 | 0,186 | 0,056 |
| METEOR | 0,310 | 0,226 | 0,168 | 0,066 |

A correlação depende muito do gerador: moderada para o GPT-3, quase nula para o T5-base. n = 180 por modelo, portanto ICs largos (a calcular no relatório).

## Prévia da SP3 (tipologia de divergência)

Os casos de maior divergência (métrica alta, humano 0) são exatamente o padrão previsto em H3: **acerta o grupo-alvo, erra o estereótipo**.

| Referência | Gerada | Humano | ROUGE-L |
|---|---|---|---|
| black folks are violent | black folks are stupid | 0 | 0,75 |
| jewish people are criminals | jewish people are incompetent | 0 | 0,75 |
| women are cowardly | women are smarter | 0 | 0,67 |
| black folks are bad fathers | black folks are exploited | 0 | 0,67 |

No sentido oposto, a referência "this post is a personal attack" leva a métrica zero em explicações que os humanos julgaram plenamente plausíveis. Lista completa em `results/divergencias_rougeL.csv`.

## Pendências técnicas

- **BERTScore e MoverScore** não rodaram aqui: o ambiente não acessa o HuggingFace. Script pronto em `src/metricas_embeddings.py` para rodar no Colab.
- **Múltiplas referências (OE2):** o site do SBIC também está bloqueado aqui. Script pronto em `src/referencias_multiplas.py`.
- Adicionar ICs por modelo e teste de diferença entre métricas de embeddings e de n-gramas quando BERTScore estiver pronto.
