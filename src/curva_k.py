"""P8 — curva de τ em função do número de referências (k fixo).

Desenho pedido pelo Orientador: em vez do τ parcial, fixar k referências por item
(k = 1, 2, 3, 5), sorteadas do conjunto de referências do SBIC (inclui a do FEB),
repetir o sorteio R vezes e ver como τ muda com k. Restrito a itens cujo post tem
>= K_MAX referências distintas, para que todos os k usem os mesmos itens.

Métricas: ROUGE-1/2/L, METEOR e BLEU, cada uma como o MÁXIMO sobre as k referências
sorteadas (para o BLEU isso difere do BLEU multi-referência nativo usado em
referencias_multiplas.py; aqui é max de BLEU por referência, para ser decomponível).
Texto sem prefixo (variante principal, P2).

Incerteza relatada: faixa 2,5–97,5% do τ entre as R repetições (variação devida ao
sorteio das referências). A incerteza por amostragem de posts é outra e não está aqui.

Entrada : results/metricas_por_item.csv, results/referencias_sbic_por_item.jsonl
          (gerado por src/referencias_multiplas.py, que precisa do SBIC v2)
Saída   : results/curva_k.csv
Uso     : python src/curva_k.py [--repeticoes 200]
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from nltk.translate.meteor_score import meteor_score
from sacrebleu.metrics import BLEU

from config import METRICAS_CSV, RESULTADOS, SEMENTE
from correlacoes import tau
from metricas_lexicais import _rouge, limpar, tokens

KS = (1, 2, 3, 5)
K_MAX = max(KS)
METRICAS = ("bleu", "rouge1", "rouge2", "rougeL", "meteor")
_bleu = BLEU(effective_order=True)


def escores_por_referencia(gerada: str, refs: list[str]) -> dict[str, np.ndarray]:
    """Escore da gerada contra CADA referência isoladamente (o máximo é tirado depois)."""
    tg = tokens(gerada)
    out = {m: [] for m in METRICAS}
    for ref in refs:
        r = _rouge.score(ref, gerada)
        out["rouge1"].append(r["rouge1"].fmeasure)
        out["rouge2"].append(r["rouge2"].fmeasure)
        out["rougeL"].append(r["rougeL"].fmeasure)
        out["meteor"].append(meteor_score([tokens(ref)], tg) if tg and tokens(ref) else 0.0)
        out["bleu"].append(_bleu.sentence_score(gerada, [ref]).score / 100 if tg else 0.0)
    return {m: np.array(v) for m, v in out.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeticoes", type=int, default=200)
    args = ap.parse_args()
    rng = np.random.default_rng(SEMENTE)

    arq = RESULTADOS / "referencias_sbic_por_item.jsonl"
    if not arq.exists():
        raise SystemExit(f"{arq} não existe: rode antes src/referencias_multiplas.py (precisa do SBIC v2).")
    refs = pd.read_json(arq, lines=True)
    df = pd.read_csv(METRICAS_CSV)
    of = df[df.ofensivo].merge(refs, on=["modelo", "ques_id"])
    of = of[of.refs.map(len) >= K_MAX].reset_index(drop=True)
    if len(of) < 30:
        raise SystemExit(f"Só {len(of)} itens com >= {K_MAX} referências; curva não é confiável.")
    print(f"Itens com >= {K_MAX} referências: {len(of)} ({of.post_id.nunique()} posts)")

    escores = [escores_por_referencia(limpar(g, True), list(r)) for g, r in zip(of.gerada, of.refs)]
    y = of.plausibilidade.to_numpy()

    linhas = []
    for k in KS:
        taus = {m: [] for m in METRICAS}
        for _ in range(args.repeticoes):
            escolha = [rng.choice(len(e["rougeL"]), size=k, replace=False) for e in escores]
            for m in METRICAS:
                x = np.array([e[m][idx].max() for e, idx in zip(escores, escolha)])
                taus[m].append(tau(x, y))
        for m in METRICAS:
            t = np.array(taus[m])
            linhas.append({"k": k, "metrica": m, "n_itens": len(of), "repeticoes": args.repeticoes,
                           "tau_medio": t.mean(), "faixa_2_5": np.percentile(t, 2.5),
                           "faixa_97_5": np.percentile(t, 97.5)})
    # referência do FEB sozinha (o k = 1 "oficial"), no mesmo subconjunto de itens
    for m in METRICAS:
        linhas.append({"k": "FEB", "metrica": m, "n_itens": len(of), "repeticoes": 1,
                       "tau_medio": tau(of[f"{m}_semprefixo"], y), "faixa_2_5": np.nan, "faixa_97_5": np.nan})
    out = pd.DataFrame(linhas)
    out.to_csv(RESULTADOS / "curva_k.csv", index=False)
    pd.set_option("display.float_format", "{:.3f}".format)
    print(out.pivot(index="metrica", columns="k", values="tau_medio").to_string())
    print(f"-> {RESULTADOS / 'curva_k.csv'}")


if __name__ == "__main__":
    main()
