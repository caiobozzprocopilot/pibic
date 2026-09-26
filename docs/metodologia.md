# Decisões metodológicas e convenções

Espelho técnico do quadro de coordenação do projeto (claude.ai → Projeto PIBIC → `00_COORDENACAO.md`). Status "provisória" = aguarda o orientador.

| # | Decisão | Status |
|---|---|---|
| D1 | Pergunta, subperguntas e objetivos do doc "Passos 1 a 3" | Adotada |
| D2 | Relatório parcial só com o FEB (sem geração própria de ELNs); geração citada como trabalho futuro | Provisória |
| D3 | Correlação por instância, Kendall τ-b + Spearman, IC bootstrap agrupado por post, só os 720 itens ofensivos | Adotada |
| D4 | Relatar métricas com e sem o prefixo "this post implies that" | Proposta |
| D5 | Embeddings e múltiplas referências rodam no Colab | Adotada |

## Convenções de dados (FEB/SBIC)

- `Input.{k}_gt_idx = 0` → a referência é `explanation_{k}_i` (e1); com 1, é `explanation_{k}_j` (e2). Segue o código de `scripts/compute_kappa.py` do FEB (o comentário no script descreve as colunas trocadas).
- `Input.gt_{k}` → rótulo do post: 0 = ofensivo, 1 = não ofensivo.
- Plausibilidade = média de 3 anotadores com yes = 1, w_yes = 2/3, w_no = 1/3, no = 0 (mesma escala do FEB).
- Os CSVs públicos não trazem `WorkerId`; cada linha é um HIT de um anotador.
- Um item = (modelo, `ques_id`). O mesmo post aparece para vários modelos → `post_id` é a unidade do bootstrap.

## Pré-processamento das métricas

- Minúsculas; ponto final removido; prefixo removido por regex `^\s*this post implies that\s*` na variante "sem prefixo".
- BLEU: sacrebleu `sentence_score`, `effective_order=True`, suavização padrão (exp).
- ROUGE: `rouge-score`, F1, **sem stemmer** (padrão da biblioteca). Com stemmer, 295 itens ficam com ROUGE-L = 0 em vez de 311.
- METEOR: NLTK, tokens `[a-z0-9']+`.
- Comprimento: número de tokens da gerada (linha de base ingênua).

## Estatística

- τ-b (scipy, trata empates, importantes aqui: a plausibilidade só tem 10 valores possíveis).
- Bootstrap percentil agrupado por post, B = 2000, semente 20262027.
- Δτ entre métricas: diferenças calculadas nas mesmas réplicas bootstrap (pareado); significativo se o IC 95% não inclui 0.

## Diferenças em relação à rodada de 25/09/2026

A primeira rodada (conversa Coordenação) foi feita num ambiente descartado; este repositório reimplementa os scripts. Os números mudam na 2ª–3ª casa decimal (tokenização e pontuação) e as conclusões se mantêm, com uma exceção: aqui o **ROUGE-2 sem prefixo** fica significativamente abaixo das demais (antes, τ = 0,155 e sem diferença significativa), e a vantagem mínima de ROUGE-1 sobre BLEU no texto completo não aparece mais. **Os números válidos são os deste repositório.**
