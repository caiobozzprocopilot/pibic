# PIBIC 2026–2027 — Métricas automáticas para explicações de discurso de ódio

**Pergunta de pesquisa:** em que medida as métricas automáticas de similaridade textual (n-gramas e embeddings) concordam com o julgamento humano de plausibilidade de explicações em linguagem natural (ELNs) sobre discurso ofensivo, e onde e por que divergem?

Estudante: Caio Lamoglia · PUCPR · PIBIC 2026–2027

## Dados

Usamos a avaliação humana do **FEB** (Marasović et al., 2022) na tarefa **SBIC** (Sap et al., 2020): explicações geradas por 4 modelos (GPT-3, T5-3B, T5-large, T5-base), cada uma julgada por 3 anotadores quanto à plausibilidade.

| | |
|---|---|
| Julgamentos | 4.320 |
| Itens (explicação gerada + referência) | 1.440 (4 modelos × 360) |
| Posts distintos | 563 |
| Itens ofensivos (recorte da análise) | 720 |
| Ofensivos com plausibilidade 0 | 254 (dp = 0,34) |
| Cópias exatas (gerada = referência) | 16 (plaus. média 0,85) |

Nos 720 itens não ofensivos a gerada é idêntica à referência ("this post does not imply anything offensive") em 100% dos casos, por isso ficam de fora.

## Como reproduzir

```bash
git clone https://github.com/caiobozzprocopilot/pibic.git && cd pibic
git clone --depth 1 https://github.com/allenai/feb.git data/raw/feb
pip install -r requirements.txt
python -m nltk.downloader wordnet omw-1.4

python src/carregar_feb.py        # -> data/processed/feb_sbic_itens.csv
python src/metricas_lexicais.py   # -> results/metricas_por_item.csv
python src/correlacoes.py         # -> results/correlacoes*.csv, delta_tau.csv, divergencias_rougeL.csv
```

**BERTScore, MoverScore e múltiplas referências** precisam de GPU e de acesso ao HuggingFace e ao site do SBIC: abra [`notebooks/colab_embeddings.ipynb`](notebooks/colab_embeddings.ipynb) no Google Colab. O `correlacoes.py` incorpora as novas colunas automaticamente.

## Estrutura

```
src/
  config.py                 caminhos, escala de plausibilidade, semente, B do bootstrap
  carregar_feb.py           CSVs brutos do MTurk -> 1 linha por item
  metricas_lexicais.py      BLEU, ROUGE-1/2/L, METEOR, comprimento (texto completo e sem prefixo)
  metricas_embeddings.py    BERTScore e MoverScore (Colab)
  referencias_multiplas.py  OE2: todas as implicações do SBIC como referências (Colab/local)
  correlacoes.py            τ-b, ρ, IC bootstrap agrupado por post, Δτ pareado, por modelo, divergências
notebooks/
  colab_embeddings.ipynb    roteiro completo para o Colab
data/processed/             tabela de itens (gerada pelos scripts)
results/                    saídas versionadas
docs/metodologia.md         decisões metodológicas e convenções
```

## Resultados preliminares (OE1, n-gramas)

Correlação por instância nos 720 itens ofensivos. Kendall τ-b, IC 95% por bootstrap percentil agrupado por post (B = 2000, semente 20262027).

| Métrica | τ (completo) | IC 95% | τ (sem prefixo) | IC 95% | ρ Spearman (sem prefixo) |
|---|---|---|---|---|---|
| BLEU | 0,159 | [0,094; 0,223] | 0,183 | [0,121; 0,242] | 0,238 |
| ROUGE-1 | 0,175 | [0,110; 0,239] | 0,189 | [0,125; 0,253] | 0,243 |
| ROUGE-2 | 0,160 | [0,096; 0,225] | 0,136 | [0,067; 0,205] | 0,161 |
| ROUGE-L | 0,173 | [0,109; 0,237] | 0,189 | [0,124; 0,250] | 0,242 |
| METEOR | 0,167 | [0,103; 0,231] | 0,190 | [0,127; 0,250] | 0,248 |
| Comprimento (linha de base) | −0,003 | [−0,067; 0,061] | 0,016 | [−0,048; 0,081] | 0,021 |

- Todas as métricas de n-gramas têm correlação **fraca** (τ < 0,2), porém acima de zero e da linha de base de comprimento.
- Sem o prefixo "this post implies that", **311 dos 720 itens (43%) têm ROUGE-L = 0**: a métrica não consegue ordenar quase metade dos itens (plaus. média 0,24; 7 deles com nota máxima dos humanos).
- Entre as métricas, a única diferença significativa (Δτ pareado) é o **ROUGE-2 sem prefixo, abaixo** de ROUGE-1, ROUGE-L e METEOR (Δτ ≈ −0,05).
- Sem as 16 cópias exatas, τ cai para ~0,13–0,16: parte da correlação vem de poucos casos triviais.

**Por modelo (τ sem prefixo, n = 180 cada):**

| Métrica | GPT-3 | T5-3B | T5-large | T5-base |
|---|---|---|---|---|
| BLEU | 0,320 | 0,159 | 0,204 | 0,053 |
| ROUGE-L | 0,331 | 0,171 | 0,223 | 0,032 |
| METEOR | 0,286 | 0,208 | 0,195 | 0,064 |

A concordância depende muito do gerador: moderada no GPT-3, nula no T5-base (IC inclui zero). ICs completos em `results/correlacoes_por_modelo.csv`.

**Prévia da tipologia de divergência (SP3):** os casos com métrica alta e humano 0 seguem o padrão "acerta o grupo-alvo, erra o estereótipo" (ex.: ref. *black folks are violent* × gerada *black folks are stupid*, ROUGE-L 0,75). Lista em `results/divergencias_rougeL.csv`.

## Resultados preliminares (OE2, múltiplas referências)

Cada post do SBIC tem várias implicações escritas por anotadores diferentes; o FEB usa só uma. Juntando todas (mediana de 5 referências por item, de 1 a 21), recalculamos as métricas sem prefixo contra o conjunto (BLEU multi-referência; ROUGE e METEOR pelo máximo).

| Métrica | τ referência única | τ múltiplas refs | IC 95% (múltiplas) | Δτ (IC 95%) |
|---|---|---|---|---|
| BLEU | 0,183 | 0,201 | [0,140; 0,263] | +0,017 [−0,018; 0,059], n.s. |
| ROUGE-1 | 0,189 | 0,233 | [0,173; 0,298] | +0,044 [0,009; 0,085] |
| ROUGE-2 | 0,136 | 0,237 | [0,172; 0,305] | +0,100 [0,052; 0,151] |
| ROUGE-L | 0,189 | 0,228 | [0,168; 0,292] | +0,039 [0,004; 0,078] |
| METEOR | 0,190 | 0,235 | [0,177; 0,298] | +0,045 [0,013; 0,080] |

- Com múltiplas referências, a correlação **sobe em todas as métricas**, e a alta é significativa em todas exceto o BLEU. O maior ganho é do ROUGE-2, que deixa de ser a pior métrica.
- Os itens com ROUGE-L = 0 caem de 311 para 231. Parte do "zero" era falta de referência, não explicação ruim.
- **Controle:** posts com mais referências ganham sobreposição só por ter mais chances (τ entre nº de refs e ROUGE-L multi = 0,44). Controlando o nº de referências (τ parcial), o ganho se mantém: ROUGE-L 0,172 → 0,210; METEOR 0,172 → 0,218.
- Mesmo assim, a correlação continua **fraca** (τ < 0,25): mais referências ajudam, mas não resolvem.
- Por modelo, o ganho aparece nos T5 (ex.: ROUGE-L no T5-3B 0,171 → 0,262); no GPT-3 o τ cai um pouco (0,331 → 0,293).

## Pendências

- [ ] Rodar BERTScore e MoverScore no Colab (1ª tentativa não gerou as colunas)
- [x] Baixar o SBIC v2 e rodar múltiplas referências (OE2)
- [ ] Tipologia de divergência: anotar ~100 casos (SP3)
- [ ] Relatório parcial (meta interna: 23/01/2027)

## Referências

- MARASOVIĆ, A. et al. Few-shot self-rationalization with natural language prompts. *Findings of NAACL*, 2022. Repositório: https://github.com/allenai/feb
- SAP, M. et al. Social bias frames: reasoning about social and power implications of language. *ACL*, 2020.
- ZHANG, T. et al. BERTScore: evaluating text generation with BERT. *ICLR*, 2020.
- ZHAO, W. et al. MoverScore: text generation evaluating with contextualized embeddings and earth mover distance. *EMNLP*, 2019.
