"""Métricas de n-gramas (BLEU, ROUGE-1/2/L, METEOR) por instância, nos itens ofensivos do FEB/SBIC.

Duas variantes de texto:
  - 'completo': explicação como está ("this post implies that ...")
  - 'sem_prefixo': remove o molde fixo "this post implies (that)" das duas explicações,
    que é idêntico em quase todos os pares e infla a sobreposição de forma uniforme.
Saída: data/feb_sbic_metricas_lexicais.csv
Requer: sacrebleu, rouge-score, nltk (wordnet, omw-1.4)
"""
import re
import pandas as pd
from sacrebleu.metrics import BLEU
from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score

PREFIXO = re.compile(r"^\s*this post (implies|imply|is)( that)?\s*", re.I)
bleu = BLEU(effective_order=True)  # BLEU de sentença com suavização padrão do sacrebleu (exp)
rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

def tira_prefixo(t):
    return PREFIXO.sub("", t).strip().rstrip(".")

def pontua(ger, ref):
    r = rouge.score(ref, ger)
    return {
        "bleu": bleu.sentence_score(ger, [ref]).score / 100,
        "rouge1": r["rouge1"].fmeasure,
        "rouge2": r["rouge2"].fmeasure,
        "rougeL": r["rougeL"].fmeasure,
        "meteor": meteor_score([ref.lower().split()], ger.lower().split()),
    }

if __name__ == "__main__":
    itens = pd.read_csv("data/feb_sbic_itens.csv")
    of = itens[itens.ofensivo].copy()
    linhas = []
    for _, r in of.iterrows():
        for var, g, ref in [("completo", r.gerada, r.referencia),
                            ("sem_prefixo", tira_prefixo(r.gerada), tira_prefixo(r.referencia))]:
            linhas.append({"modelo": r.modelo, "ques_id": r.ques_id, "variante": var, **pontua(g, ref)})
    m = pd.DataFrame(linhas)
    m.to_csv("data/feb_sbic_metricas_lexicais.csv", index=False)
    print(m.groupby("variante").mean(numeric_only=True).drop(columns="ques_id").round(3))
