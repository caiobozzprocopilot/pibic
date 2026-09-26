# Plano mestre — até o relatório parcial

**Meta interna:** relatório parcial pronto em **23/01/2027**. O prazo oficial deve cair no início de fevereiro (no ciclo 2025–26 foi de 6 a 10/02), o que deixa duas semanas de folga.

**Princípio:** o relatório parcial sai com resultados preliminares reais (OE1 com todas as métricas), e não só com metodologia planejada. Isso já está ao alcance: as métricas de n-gramas estão prontas.

## Blocos

| Semanas | Período | Frente | Entregas | Quem |
|---|---|---|---|---|
| 1 | 29/09 – 05/10 | Fechar desenho | Orientador responde P1–P7; Caio responde C1–C4; Passo 4 fechado | Orientador, Caio |
| 2–3 | 06/10 – 19/10 | Embeddings e refs. múltiplas | BERTScore + MoverScore no Colab; SBIC com múltiplas implicações; tabela completa do OE1 | Caio (roda), Coordenação (código e análise) |
| 4–5 | 20/10 – 02/11 | OE2 + ICs por modelo | Correlações com referência única vs. múltipla; testes n-gramas vs. embeddings | Coordenação |
| 6–7 | 03/11 – 16/11 | SP3: tipologia | Categorias de divergência (grupo certo/estereótipo errado, referência genérica, paráfrase etc.); anotação de ~100 casos pelo Caio | Caio + Coordenação |
| 3–8 | 13/10 – 23/11 | Leituras em paralelo | Fichas: Sap 2020, Marasović 2022, Zhang 2020 (BERTScore), Zhao 2019 (MoverScore), Gurrapu 2023, 1 de LLM-as-a-judge | Caio |
| 8–9 | 17/11 – 30/11 | Redação 1 | Introdução, objetivos, fundamentação, metodologia | Coordenação redige, Orientador revisa |
| 10–11 | 01/12 – 14/12 | Redação 2 | Resultados preliminares, discussão, próximas etapas, cronograma revisado | Coordenação redige, Orientador revisa |
| 12 | 15/12 – 21/12 | **Rascunho completo** | Versão 1 enviada ao orientador real (prof.) antes do recesso | Caio |
| 13–15 | 22/12 – 11/01 | Recesso / folga | Buffer para atrasos | — |
| 16 | 12/01 – 18/01 | Revisão final | Correções do professor, ABNT (NBR 6023 e 10520:2023), formatação no modelo PUCPR | Coordenação + Caio |
| 17 | 19/01 – 23/01 | **Entrega interna** | Versão final aprovada | Caio |

## Esqueleto do relatório parcial

Provisório: ajustar ao modelo oficial quando o Caio anexar (C1).

1. Identificação (estudante, orientador, projeto, vigência)
2. Resumo
3. Introdução: problema das métricas para ELNs em discurso de ódio
4. Objetivos: geral e OE1–OE3 (doc "Passos 1 a 3")
5. Fundamentação: discurso de ódio e SBIC; ELNs e FEB; métricas de n-gramas e de embeddings; avaliação humana de explicações
6. Metodologia: dados do FEB, recorte dos 720 itens, métricas, variantes de texto, correlação por instância e bootstrap
7. Resultados preliminares: tabela τ/ρ, análise por modelo, itens com ROUGE-L = 0, prévia da tipologia
8. Atividades realizadas vs. previstas: honestidade sobre a mudança de escopo (geração → FEB)
9. Próximas etapas e cronograma revisado (fev–ago/2027)
10. Referências (ABNT)

## Depois do parcial (visão rápida)

- **Fev–abr/2027:** OE3 completo, eventual extensão (opção B/C), LLM-as-a-judge como métrica adicional se aprovado
- **Mai–jun:** artigo (STIL/BRACIS: conferir prazos)
- **Jul–ago:** relatório final e resumo SEMIC
- **Set:** vídeo-pôster
