# 00 — Quadro de coordenação PIBIC

> Cópia do documento `claude/00_COORDENACAO.md` do projeto PIBIC no Claude (27/09/2026). A versão viva fica no projeto.

**Leia este arquivo primeiro.** As duas conversas do projeto não se enxergam diretamente: elas se comunicam por aqui.

| Conversa | Papel |
|---|---|
| **Coordenação** | Plano mestre, experimentos, código, redação do relatório parcial |
| **Orientador PIBIC** | Revisa, critica e decide: pergunta, objetivos, desenho metodológico, texto |

**Como usar:** cada conversa, ao terminar uma rodada, atualiza as seções *Perguntas abertas*, *Decisões* e *Registro* deste arquivo. Respostas do Orientador entram na coluna "Resposta". Caio leva o recado quando preciso ("leia o 00_COORDENACAO no projeto").

## Documentos do projeto

| Doc | Conteúdo | Dono |
|---|---|---|
| plano_estudos_pibic_2026_2027 (2).docx | Plano original | Caio |
| PIBIC 2026–2027 — Passos 1 a 3 ….docx | FEB, pergunta, objetivos | Orientador |
| claude/00_COORDENACAO.md | Este quadro | ambos |
| claude/plano_mestre_ate_fevereiro.md | Cronograma até o relatório parcial | Coordenação |
| claude/resultados_preliminares.md | Números do OE1, OE2 e prévia da SP3 | Coordenação |
| **github.com/caiobozzprocopilot/pibic** | Código, dados processados, resultados, notebook do Colab, planilha da SP3; `docs/` tem cópias destes três .md | Coordenação (Caio faz o push) |

## Decisões (vigentes até o Orientador dizer o contrário)

| # | Decisão | Status |
|---|---|---|
| D1 | Pergunta, subperguntas e objetivos: os do doc "Passos 1 a 3" | Adotada |
| D2 | Geração de ELNs: **opção A** para o relatório parcial (só FEB); B/C citadas como trabalho futuro | **Provisória** — aguarda Orientador (P1) |
| D3 | Correlação por instância, Kendall τ-b + Spearman, IC bootstrap agrupado por post, só os 720 itens ofensivos | Adotada (prévia do Passo 4) |
| D4 | Relatar métricas com e sem o prefixo "this post implies that" | Proposta — aguarda Orientador (P2) |
| D5 | Embeddings (BERTScore/MoverScore) e múltiplas referências rodam no Colab (ambiente da Coordenação não acessa HuggingFace nem o site do SBIC) | Adotada |
| D6 | Números válidos do OE1 são os do repositório GitHub (reimplementação reprodutível); ROUGE sem stemmer | Adotada |
| D7 | OE2: múltiplas referências = todas as `targetStereotype` do SBIC v2 + a do FEB; BLEU multi-ref nativo, ROUGE/METEOR pelo máximo; relatar também τ parcial controlando o nº de referências | Proposta — aguarda Orientador (P8) |
| D8 | SP3: amostra de 100 divergências (50 métrica alta/humano ≤ 1/3; 50 métrica baixa/humano ≥ 2/3; sem cópias exatas; ROUGE-L sem prefixo). Livro de códigos A1–A4/A9 e B1–B4/B9; categoria sugerida por heurística, decisão final do Caio | Proposta — aguarda Orientador (P9) |

## Perguntas abertas para o Orientador

| # | Pergunta | Resposta |
|---|---|---|
| P1 | Confirma a opção A (sem geração própria) para o relatório parcial? Se B ou C, quando entra? | |
| P2 | A variante principal deve ser o texto sem prefixo? (Tirar o molde muda τ e expõe 43% de itens com ROUGE-L = 0) | |
| P3 | Tratar as 16 cópias exatas (gerada = referência): manter, excluir ou relatar as duas versões? | |
| P4 | Teste entre métricas: bootstrap pareado de Δτ (já feito) basta, ou quer também o teste de Williams/Steiger? | |
| P5 | O Passo 4 (redesenho da Seção 4.3) pode ser dado como fechado com D3? | |
| P6 | O relatório parcial deve trazer os resultados preliminares ou só metodologia (o modelo da PUCPR pode exigir "resultados parciais")? | |
| P7 | LLM-as-a-judge (Passo 6): entra como leitura ou também como uma métrica a mais no experimento? | |
| P8 | OE2: múltiplas refs sobem τ (ROUGE-L 0,189 → 0,228; ROUGE-2 0,136 → 0,237), mas o nº de refs varia de 1 a 21 e infla a sobreposição. O τ parcial controlando nº de refs basta, ou prefere limitar a k refs sorteadas por post? | |
| P9 | SP3: o livro de códigos (D8) serve? A sugestão automática pode enviesar a anotação; aceitável para o parcial ou quer um segundo anotador / anotação cega em parte da amostra? | |
| P10 | **Achado:** 200 dos 720 itens ofensivos (28%) têm referência genérica ("personal attack", "trivializes harm"), com ROUGE-L médio 0,09 contra 0,24 nos demais; é a causa de 27 dos 50 falsos negativos da amostra. Excluir esses itens, relatar à parte, ou tratar como achado central? | |

## Perguntas abertas para o Caio

| # | Pergunta | Resposta |
|---|---|---|
| C1 | Baixar o modelo oficial do relatório parcial e anexar ao projeto: static.pucpr.br/pucpr/2025/12/Modelo-Relatório-Parcial_PIBIC_2025-2026.docx (não consigo abrir daqui) | |
| C2 | Confirmar a data. No ciclo 2025–26 o prazo foi **6 a 10 de fevereiro**; o calendário 2027 ainda não saiu. Mantemos janeiro como meta interna? | |
| C3 | Nome completo e titulação do orientador (o plano atual assina "Emerson Cabrera Paraiso — Estudante", o que parece um erro) | |
| C4 | Tem acesso ao Google Colab ou à GPU do grupo para rodar BERTScore/MoverScore? | Sim, Colab funcionando |
| C5 | Estrutura do repositório | Resolvido (commit 6416a37) |
| C6 | Rodar a célula do BERTScore no Colab (agora autossuficiente) e mandar o `resultados.zip` | Tentativa de 26/09 falhou: célula rodou antes da preparação |
| C7 | Subir `atualizacao_27set.zip` (SP3 + notebook limpo + docs atualizados) e anotar os 100 itens de `results/sp3_anotacao.xlsx` | |

## Registro

- **25/09/2026 — Coordenação:** lidos os dois docs. Reproduzidos os números do Passo 1 (1.440 itens, 720 ofensivos, 254 com nota 0, dp 0,34). Calculadas BLEU, ROUGE-1/2/L e METEOR com correlações. Achados: 43% dos itens com ROUGE-L = 0 sem prefixo; 16 cópias exatas; divergências confirmam H3 (grupo certo, estereótipo errado). Criados este quadro e o plano mestre.
- **25/09/2026 — Coordenação (2ª rodada):** estrutura do repositório GitHub montada; scripts reimplementados e resultados reproduzidos (ajuste: ROUGE-2 sem prefixo significativamente abaixo das demais, τ = 0,136).
- **25/09/2026 — Coordenação (3ª rodada):** push inicial corrigido (commit 6416a37); pipeline testado do zero, reprodutível.
- **25/09/2026 — Coordenação (4ª rodada):** Caio rodou o Colab. **OE2 concluído:** múltiplas referências aumentam τ em todas as métricas (significativo exceto BLEU); ganho sobrevive ao controle do nº de referências; correlação segue fraca (τ < 0,25). ROUGE-L = 0 cai de 311 para 231. BERTScore não gerou colunas. Aberta P8. Repositório no commit 31a93c7.
- **26/09/2026 — Coordenação (5ª rodada):** SP3 adiantada. `src/amostra_sp3.py` gera 100 divergências com categoria sugerida (A: 26 A1, 18 A4, 3 A2, 2 A3, 1 A9; B: 27 B2, 11 B1, 6 B3, 6 B4) e a planilha `sp3_anotacao.xlsx`. Achado P10: 28% dos itens ofensivos têm referência genérica. Abertas P9 e P10.
- **27/09/2026 — Coordenação (6ª rodada):** conferido o repositório (commit 6ca9324, salvo pelo Colab). Faltava a atualização da SP3; o notebook tinha a célula autossuficiente do BERTScore, mas salvo com a saída do erro antigo. Preparado `atualizacao_27set.zip`: SP3, notebook limpo, README, requirements e cópias atualizadas dos três .md em `docs/`. BERTScore ainda pendente.
