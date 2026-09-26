"""Recupera do SBIC v2 todas as implicações (targetStereotype) de cada post avaliado no FEB (OE2 / SP2).

Precisa baixar o SBIC (rode no Colab ou máquina do grupo):
    wget https://homes.cs.washington.edu/~msap/social-bias-frames/SBIC.v2.tgz && tar xzf SBIC.v2.tgz
Saída: data/feb_sbic_refs_multiplas.csv  (ques_id, modelo, post, referencias = lista separada por " ||| ")
"""
import glob, re
import pandas as pd

def norm(t):
    return re.sub(r"\s+", " ", str(t).lower()).strip()

if __name__ == "__main__":
    sbic = pd.concat([pd.read_csv(a) for a in glob.glob("SBIC.v2*.csv")])
    sbic = sbic[sbic.targetStereotype.notna()]
    refs = sbic.groupby(sbic.post.map(norm)).targetStereotype.agg(lambda s: sorted(set(map(norm, s))))
    itens = pd.read_csv("data/feb_sbic_itens.csv")
    of = itens[itens.ofensivo].copy()
    of["refs"] = of.post.map(norm).map(refs)
    print("posts encontrados:", of.refs.notna().mean().round(3),
          "| média de refs por post:", of.refs.dropna().str.len().mean().round(2))
    of["referencias"] = of.refs.map(lambda r: " ||| ".join(f"this post implies that {x}" for x in r) if isinstance(r, list) else "")
    of[["modelo", "ques_id", "post", "referencias"]].to_csv("data/feb_sbic_refs_multiplas.csv", index=False)
