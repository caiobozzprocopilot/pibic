"""P10 — referências genéricas: definição operacional e análise estratificada.

Definição (fixa, decidida antes da análise estratificada): a referência é GENÉRICA quando,
depois de normalizada (minúsculas, espaços, ponto final), é exatamente um dos moldes do SBIC
que não nomeiam grupo-alvo nem estereótipo:

    - "this post is a personal attack"
    - "this post trivializes harm to victims"

Qualquer outra referência é ESPECÍFICA, inclusive as que fogem do molde "this post implies
that" mas nomeiam o tema (ex.: "this post makes light of slavery").

Saídas:
- results/referencias_genericas.csv    -> τ por estrato (genérica × específica) com IC 95%
                                          e Δτ entre estratos (bootstrap agrupado por post)
- results/genericas_conferencia.csv    -> amostra de 30 referências para conferência humana
                                          da classificação (15 de cada estrato; semente fixa)

Uso: python src/referencias_genericas.py
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from config import B_BOOTSTRAP, METRICAS_CSV, RESULTADOS, SEMENTE
from correlacoes import ic, indices_bootstrap, tau

MOLDES_GENERICOS = (
    "this post is a personal attack",
    "this post trivializes harm to victims",
)
METRICAS = ["bleu", "rouge1", "rouge2", "rougeL", "meteor", "bertscore"]


def normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", str(t).strip().lower()).rstrip(". ")


def eh_generica(ref: str) -> bool:
    return normalizar(ref) in MOLDES_GENERICOS


def main() -> None:
    rng = np.random.default_rng(SEMENTE)
    df = pd.read_csv(METRICAS_CSV)
    of = df[df.ofensivo].reset_index(drop=True)
    of["ref_generica"] = of.referencia.map(eh_generica)
    g = of.ref_generica.to_numpy()
    y = of.plausibilidade.to_numpy()
    reamostras = indices_bootstrap(of.post_id.to_numpy(), B_BOOTSTRAP, rng)

    linhas = []
    for m in METRICAS:
        col = f"{m}_semprefixo"
        if col not in of:
            continue
        x = of[col].to_numpy()
        t_gen, t_esp = tau(x[g], y[g]), tau(x[~g], y[~g])
        b_gen, b_esp = [], []
        for idx in reamostras:
            gi = g[idx]
            b_gen.append(tau(x[idx][gi], y[idx][gi]))
            b_esp.append(tau(x[idx][~gi], y[idx][~gi]))
        b_gen, b_esp = np.array(b_gen), np.array(b_esp)
        d = b_esp - b_gen
        linhas.append({
            "metrica": col,
            "n_generica": int(g.sum()), "tau_generica": t_gen,
            "ic95_inf_generica": ic(b_gen)[0], "ic95_sup_generica": ic(b_gen)[1],
            "n_especifica": int((~g).sum()), "tau_especifica": t_esp,
            "ic95_inf_especifica": ic(b_esp)[0], "ic95_sup_especifica": ic(b_esp)[1],
            "delta_esp_menos_gen": t_esp - t_gen,
            "ic95_inf_delta": ic(d)[0], "ic95_sup_delta": ic(d)[1],
        })
    out = pd.DataFrame(linhas)
    out.to_csv(RESULTADOS / "referencias_genericas.csv", index=False)

    # descritivos
    desc = of.groupby("ref_generica").agg(
        n=("plausibilidade", "size"),
        plaus_gerada=("plausibilidade", "mean"),
        plaus_referencia=("plausibilidade_ref", "mean"),
        rougeL=("rougeL_semprefixo", "mean"),
        rougeL_zero=("rougeL_semprefixo", lambda s: (s == 0).mean()),
    )

    # amostra para conferência humana da regra (P10): todas as referências distintas fora do
    # molde "this post implies that" (onde a regra decide algo) + 12 do molde, sorteadas
    refs = of.drop_duplicates("referencia")[["referencia", "ref_generica"]].copy()
    fora = refs[~refs.referencia.str.lower().str.startswith("this post implies that")]
    dentro = refs.drop(fora.index).sample(12, random_state=SEMENTE)
    amostra = pd.concat([fora, dentro]).sample(frac=1, random_state=SEMENTE)
    amostra = amostra.rename(columns={"ref_generica": "regra_generica"})
    amostra["conferencia_humana_generica_sim_nao"] = ""
    amostra["observacao"] = ""
    amostra.to_csv(RESULTADOS / "genericas_conferencia.csv", index=False)

    # τ geral × τ dentro dos estratos (efeito entre estratos)
    geral = {m: tau(of[f"{m}_semprefixo"], of.plausibilidade) for m in METRICAS if f"{m}_semprefixo" in of}

    pd.set_option("display.float_format", "{:.3f}".format, "display.width", 200)
    print(desc.to_string())
    print()
    print(out[["metrica", "tau_generica", "ic95_inf_generica", "ic95_sup_generica",
               "tau_especifica", "ic95_inf_especifica", "ic95_sup_especifica",
               "delta_esp_menos_gen", "ic95_inf_delta", "ic95_sup_delta"]].to_string(index=False))
    print("\nτ geral (todos os 720):", {k: round(v, 3) for k, v in geral.items()})
    print(f"Amostra de conferência: {len(amostra)} referências distintas "
          f"({amostra.regra_generica.sum()} classificadas como genéricas pela regra)")


if __name__ == "__main__":
    main()
