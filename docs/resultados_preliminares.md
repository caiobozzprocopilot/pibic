# Resultados preliminares — OE1 (n-gramas e BERTScore), OE2 (múltiplas referências) e prévia da SP3

> Cópia do documento `claude/resultados_preliminares.md` do projeto PIBIC no Claude (27/09/2026, após o BERTScore). A versão viva fica no projeto.

**Versão de referência: este repositório** (reimplementação de 25/09/2026, substitui a primeira rodada). Reprodução:

```
git clone https://github.com/caiobozzprocopilot/pibic.git && cd pibic
git clone --depth 1 https://github.com/allenai/feb.git data/raw/feb
pip install -r requirements.txt
python src/carregar_feb.py && python src/metricas_lexicais.py && python src/correlacoes.py
```

## Dados

- 4.320 julgamentos → 1.440 itens (4 modelos × 360), 3 anotadores por item, 563 posts distintos. Confirma o Passo 1.
- Análise restrita aos **720 itens ofensivos** (nos não ofensivos, gerada = referência em 100%). 254 com plausibilidade 0; dp 0,34.
- **16 itens ofensivos** com cópia exata da referência (plausibilidade média 0,85).
- Convenção (código do FEB): `Input.{k}_gt_idx = 0` → referência é a e1; `Input.gt_{k}` é o rótulo (0 = ofensivo). Os CSVs públicos não trazem WorkerId.

## Duas variantes de texto

Com e sem o molde "this post implies that". Sem o prefixo, **311 dos 720 itens (43%) têm ROUGE-L = 0** (plaus. média 0,24; 7 com nota máxima). ROUGE sem stemmer (padrão da biblioteca); com stemmer seriam 295.

## OE1 — Correlação por instância (n = 720, Kendall τ-b, IC 95% bootstrap agrupado por post, B = 2000)

| Métrica | τ (completo) | IC 95% | τ (sem prefixo) | IC 95% | ρ (sem prefixo) |
|---|---|---|---|---|---|
| BLEU | 0,159 | [0,094; 0,223] | 0,183 | [0,121; 0,242] | 0,238 |
| ROUGE-1 | 0,175 | [0,110; 0,239] | 0,189 | [0,125; 0,253] | 0,243 |
| ROUGE-2 | 0,160 | [0,096; 0,225] | 0,136 | [0,067; 0,205] | 0,161 |
| ROUGE-L | 0,173 | [0,109; 0,237] | 0,189 | [0,124; 0,250] | 0,242 |
| METEOR | 0,167 | [0,103; 0,231] | 0,190 | [0,127; 0,250] | 0,248 |
| Comprimento | −0,003 | [−0,067; 0,061] | 0,016 | [−0,048; 0,081] | 0,021 |

- Correlação **fraca** (τ < 0,2) em todas, acima de zero e da linha de base.
- Δτ pareado: única diferença significativa é **ROUGE-2 sem prefixo abaixo** de ROUGE-1, ROUGE-L e METEOR (Δτ ≈ −0,05).
- Sem as 16 cópias exatas: τ ≈ 0,13–0,16.

### Por modelo (τ sem prefixo, n = 180; ICs em results/correlacoes_por_modelo.csv)

| Métrica | GPT-3 | T5-3B | T5-large | T5-base |
|---|---|---|---|---|
| BLEU | 0,320 | 0,159 | 0,204 | 0,053 |
| ROUGE-L | 0,331 | 0,171 | 0,223 | 0,032 |
| METEOR | 0,286 | 0,208 | 0,195 | 0,064 |

T5-base: IC inclui zero para todas as métricas.

## OE1 — BERTScore (27/09/2026, commit 3aea59d)

roberta-large, F1, `rescale_with_baseline=True` (o reescalonamento não altera τ). Mesmos 720 itens e bootstrap.

| Métrica | τ (completo) | τ (sem prefixo) | IC 95% (sem prefixo) | ρ (sem prefixo) |
|---|---|---|---|---|
| BERTScore | 0,199 | 0,201 | [0,142; 0,262] | 0,277 |
| ROUGE-L (ref. única) | 0,173 | 0,189 | [0,124; 0,250] | 0,242 |
| ROUGE-L (múltiplas refs) | — | 0,228 | [0,168; 0,292] | 0,299 |

- **O BERTScore também fica na faixa fraca (τ ≈ 0,20).** No texto completo, supera BLEU e ROUGE-2 (Δτ ≈ +0,04, significativo); sem prefixo, só o ROUGE-2 (+0,065). **Não difere significativamente** de ROUGE-1, ROUGE-L e METEOR, nem das n-gramas com múltiplas referências.
- **O prefixo não afeta o BERTScore** (0,199 × 0,201; Δτ = −0,002, n.s.): as embeddings já "descontam" o molde que infla as n-gramas.
- **Onde as n-gramas zeram, o BERTScore também falha:** nos 311 itens com ROUGE-L = 0, τ = 0,05. Nos 409 com ROUGE-L > 0, τ = 0,18.
- Correlação entre BERTScore e ROUGE-L sem prefixo: τ = 0,59. As duas famílias medem quase a mesma coisa.
- Por modelo: GPT-3 0,284; T5-3B 0,197; T5-large 0,205; T5-base 0,083 (IC inclui zero). Sem as 16 cópias exatas: 0,172.
- MoverScore ainda não calculado.

## OE2 — Referência única × múltiplas referências (Colab, 25/09/2026)

Todas as implicações (`targetStereotype`) do SBIC v2 para cada post, mais a do FEB. Mediana de 5 referências por item (1 a 21). Texto sem prefixo; BLEU multi-referência nativo, ROUGE/METEOR pelo máximo.

| Métrica | τ única | τ múltiplas | IC 95% (múlt.) | Δτ [IC 95%] | τ parcial única → múlt. (controla nº de refs) |
|---|---|---|---|---|---|
| BLEU | 0,183 | 0,201 | [0,140; 0,263] | +0,017 [−0,018; 0,059] n.s. | 0,167 → 0,180 |
| ROUGE-1 | 0,189 | 0,233 | [0,173; 0,298] | +0,044 [0,009; 0,085] | 0,173 → 0,216 |
| ROUGE-2 | 0,136 | 0,237 | [0,172; 0,305] | +0,100 [0,052; 0,151] | 0,126 → 0,220 |
| ROUGE-L | 0,189 | 0,228 | [0,168; 0,292] | +0,039 [0,004; 0,078] | 0,172 → 0,210 |
| METEOR | 0,190 | 0,235 | [0,177; 0,298] | +0,045 [0,013; 0,080] | 0,172 → 0,218 |

- Múltiplas referências **aumentam τ em todas as métricas** (significativo exceto BLEU); ROUGE-2 deixa de ser a pior.
- ROUGE-L = 0: de 311 para 231 itens (80 "resgatados", plaus. média 0,27).
- Viés possível: mais referências = mais chances de sobreposição (τ nº refs × ROUGE-L multi = 0,44; nº refs × plaus. = 0,09). O ganho **sobrevive** ao controle por τ parcial.
- Ainda **fraca** (τ < 0,25): mais referências ajudam, não resolvem.
- Por modelo (ROUGE-L): GPT-3 0,331 → 0,293; T5-3B 0,171 → 0,262; T5-large 0,223 → 0,216; T5-base 0,032 → 0,094.

## Prévia da SP3 (26/09/2026)

Amostra de 100 divergências em `results/sp3_anotacao.xlsx` (gerada por `src/amostra_sp3.py`), com categoria sugerida por heurística e anotação final pendente.

- **Direção A (métrica alta, humano baixo):** padrão dominante "acerta o grupo-alvo, erra o estereótipo" (sugerido em 26 de 50; ex.: *black folks are violent* × *black folks are stupid*, ROUGE-L 0,75). Em 18 de 50 os humanos também reprovaram a própria referência.
- **Direção B (métrica baixa, humano alto):** dominada por **referências genéricas** (27 de 50), como "this post is a personal attack".
- **Referências genéricas no conjunto todo:** 200 dos 720 itens ofensivos (28%), com ROUGE-L médio 0,09 contra 0,24 nos demais.

### SP3 — segunda anotação (Claude, 27/09/2026)

O Claude anotou os 100 casos como **segundo anotador** (colunas R–T de `results/sp3_anotacao_cega.xlsx`; justificativa por item em `results/sp3_anotacao_claude.tsv`). A anotação final, humana, é a do Caio (coluna P), ainda pendente. Como o Claude escreveu a heurística, a anotação dele não é às cegas.

| Direção | Categoria | Heurística | Claude |
|---|---|---|---|
| A | A1 Grupo certo, estereótipo errado | 26 | 14 |
| A | A2 Sobreposição só de molde | 3 | 3 |
| A | A3 Sentido invertido ou positivo | 2 | 7 |
| A | A4 Referência também implausível | 18 | 17 |
| A | A9 Outro | 1 | 9 |
| B | B1 Paráfrase | 11 | 7 |
| B | B2 Explicação genérica | 27 | 28 |
| B | B3 Alternativa coberta | 6 | 6 |
| B | B4 Alternativa não coberta | 6 | 7 |
| B | B9 Outro | 0 | 2 |

- Concordância heurística × Claude: 80% (κ = 0,76).
- **Padrão emergente, "leitura literal":** em 18 dos 100 casos a gerada repete as palavras da piada sem extrair a implicação (ex.: *jews are speeding bullets*, *jewish folks eat pizza*). É a maior parte dos A9 e candidata a categoria nova (A5). Quase só nos T5: 17 dos 77 itens T5 da amostra, contra 1 dos 23 do GPT-3.
- **B2 é robusto:** as referências genéricas explicam 28 dos 50 casos em que a métrica reprova o que os humanos aprovam (P10).

## Pendências técnicas

- **BERTScore:** calculado (commit 3aea59d, local no Windows, RTX 3060, bert-score 0.3.12). **MoverScore:** pendente.
- SP3: falta a anotação do Caio (coluna P de `results/sp3_anotacao_cega.xlsx`; A-01..A-15 e B-01..B-15 às cegas).
- Perguntas para o Orientador: P8 (controle do nº de refs), P9 (viés da sugestão automática), P10 (o que fazer com referências genéricas).
