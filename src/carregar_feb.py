"""Carrega as avaliações humanas do FEB (SBIC) em uma tabela com um item por linha.

Fonte: https://github.com/allenai/feb  -> human_eval/results/sbic/*.csv
Convenções (seguindo scripts/compute_kappa.py do FEB):
  - Input.{k}_gt_idx == 0 -> explicação de referência é a e1 (explanation_{k}_i)
  - Input.gt_{k} é o rótulo: 0 = ofensivo, 1 = não ofensivo
  - Escala: yes=1, w_yes=2/3, w_no=1/3, no=0
Saída: data/feb_sbic_itens.csv
"""
import glob, os
import pandas as pd

ESCALA = {"yes": 1.0, "w_yes": 2 / 3, "w_no": 1 / 3, "no": 0.0}
MODELOS = {"gpt3": "GPT-3", "base": "T5-base", "large": "T5-large", "3b": "T5-3B"}

def carregar(pasta="feb/human_eval/results/sbic"):
    linhas = []
    for arq in sorted(glob.glob(os.path.join(pasta, "*.csv"))):
        modelo = MODELOS[os.path.basename(arq).split("_")[0]]
        df = pd.read_csv(arq, dtype=str, keep_default_na=False)
        for _, r in df.iterrows():
            for k in range(1, 11):
                e1, e2 = r[f"Input.explanation_{k}_i"], r[f"Input.explanation_{k}_j"]
                a1, a2 = r[f"Answer.{k}-e1"], r[f"Answer.{k}-e2"]
                ref_primeiro = int(r[f"Input.{k}_gt_idx"]) == 0
                linhas.append(dict(
                    modelo=modelo,
                    ques_id=int(r[f"Input.{k}_ques_id"]),
                    anotador=r.get("WorkerId", r.get("HITId", "")),
                    ofensivo=r[f"Input.gt_{k}"] == "0",
                    post=r[f"Input.question_{k}"],
                    referencia=e1 if ref_primeiro else e2,
                    gerada=e2 if ref_primeiro else e1,
                    nota_ref=ESCALA[a1 if ref_primeiro else a2],
                    nota_gerada=ESCALA[a2 if ref_primeiro else a1],
                ))
    anot = pd.DataFrame(linhas)
    itens = (anot.groupby(["modelo", "ques_id"])
             .agg(ofensivo=("ofensivo", "first"), post=("post", "first"),
                  referencia=("referencia", "first"), gerada=("gerada", "first"),
                  n_anot=("nota_gerada", "size"),
                  plaus_gerada=("nota_gerada", "mean"),
                  plaus_gerada_notas=("nota_gerada", lambda s: ";".join(f"{x:.3f}" for x in s)),
                  plaus_ref=("nota_ref", "mean"))
             .reset_index())
    return anot, itens

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    anot, itens = carregar()
    itens.to_csv("data/feb_sbic_itens.csv", index=False)
    print("anotações:", len(anot), "| itens:", len(itens), "| posts distintos:", itens.post.nunique())
    print(itens.groupby("modelo").agg(n=("ques_id", "size"), ofensivos=("ofensivo", "sum"),
                                      plaus_gerada=("plaus_gerada", "mean"), plaus_ref=("plaus_ref", "mean")).round(3))
    print("n_anot:", itens.n_anot.value_counts().to_dict())
    nao = itens[~itens.ofensivo]
    print("não ofensivos com gerada == referência:", (nao.gerada == nao.referencia).mean())
    of = itens[itens.ofensivo]
    print("ofensivos:", len(of), "| nota média 0:", (of.plaus_gerada == 0).sum(), "| dp:", round(of.plaus_gerada.std(), 3))
    print("ofensivos com gerada == referência:", (of.gerada.str.lower().str.strip() == of.referencia.str.lower().str.strip()).sum())
