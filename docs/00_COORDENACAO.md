# 00 — Quadro de coordenação PIBIC

**Leia este arquivo primeiro.** As duas conversas do projeto não se enxergam diretamente: elas se comunicam por aqui.

| Conversa | Papel |
|---|---|
| **Coordenação** (esta) | Plano mestre, experimentos, código, redação do relatório parcial |
| **Orientador PIBIC** | Revisa, critica e decide: pergunta, objetivos, desenho metodológico, texto |

**Como usar:** cada conversa, ao terminar uma rodada, atualiza as seções *Perguntas abertas*, *Decisões* e *Registro* deste arquivo. Respostas do Orientador entram na coluna "Resposta". Caio leva o recado quando preciso ("leia o 00_COORDENACAO no projeto").

## Documentos do projeto

| Doc | Conteúdo | Dono |
|---|---|---|
| plano_estudos_pibic_2026_2027 (2).docx | Plano original | Caio |
| PIBIC 2026–2027 — Passos 1 a 3 ….docx | FEB, pergunta, objetivos | Orientador |
| claude/00_COORDENACAO.md | Este quadro | ambos |
| claude/plano_mestre_ate_fevereiro.md | Cronograma até o relatório parcial | Coordenação |
| claude/resultados_preliminares.md | Números do OE1 (n-gramas) | Coordenação |

## Decisões (vigentes até o Orientador dizer o contrário)

| # | Decisão | Status |
|---|---|---|
| D1 | Pergunta, subperguntas e objetivos: os do doc "Passos 1 a 3" | Adotada |
| D2 | Geração de ELNs: **opção A** para o relatório parcial (só FEB); B/C citadas como trabalho futuro | **Provisória** — aguarda Orientador (P1) |
| D3 | Correlação por instância, Kendall τ-b + Spearman, IC bootstrap agrupado por post, só os 720 itens ofensivos | Adotada (prévia do Passo 4) |
| D4 | Relatar métricas com e sem o prefixo "this post implies that" | Proposta — aguarda Orientador (P2) |
| D5 | Embeddings (BERTScore/MoverScore) e múltiplas referências rodam no Colab (ambiente da Coordenação não acessa HuggingFace nem o site do SBIC) | Adotada |

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

## Perguntas abertas para o Caio

| # | Pergunta | Resposta |
|---|---|---|
| C1 | Baixar o modelo oficial do relatório parcial e anexar ao projeto: static.pucpr.br/pucpr/2025/12/Modelo-Relatório-Parcial_PIBIC_2025-2026.docx (não consigo abrir daqui) | |
| C2 | Confirmar a data. No ciclo 2025–26 o prazo foi **6 a 10 de fevereiro**; o calendário 2027 ainda não saiu. Mantemos janeiro como meta interna? | |
| C3 | Nome completo e titulação do orientador (o plano atual assina "Emerson Cabrera Paraiso — Estudante", o que parece um erro) | |
| C4 | Tem acesso ao Google Colab ou à GPU do grupo para rodar BERTScore/MoverScore? | |

## Registro

- **25/09/2026 — Coordenação:** lidos os dois docs. Reproduzidos os números do Passo 1 (1.440 itens, 720 ofensivos, 254 com nota 0, dp 0,34). Calculadas BLEU, ROUGE-1/2/L e METEOR com correlações (ver resultados_preliminares). Achados novos: 43% dos itens com ROUGE-L = 0 sem prefixo; 16 cópias exatas; divergências confirmam H3 (grupo certo, estereótipo errado). Criados este quadro e o plano mestre.
