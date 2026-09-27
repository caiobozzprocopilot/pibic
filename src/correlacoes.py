"""Correlação por instância entre métricas automáticas e plausibilidade humana (OE1).

Desenho (decisão D3): só os itens ofensivos (n = 720); Kendall τ-b e Spearman ρ;
IC 95% por bootstrap percentil **agrupado por post** (o mesmo post aparece para até
4 modelos, então os itens não são independentes); B = 2000.

Também calcula:
- Δτ pareado entre métricas (mesmas reamostragens) -> diferença significativa?
- τ por modelo gerador (com IC);
- τ sem as cópias exatas (gerada = referência);
- lista de divergências (métrica alta e humano 0; métrica 0 e humano 1).

Entrada : results/metricas_por_item.csv (+ colunas de embeddings, se existirem)
          results/metricas_multiref.csv (opcional; OE2)
Saída   : results/correlacoes.csv, correlacoes_por_modelo.csv, delta_tau.csv,
          divergencias_rougeL.csv

Uso:  python src/correlacoes.py
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from config import B_BOOTSTRAP, METRICAS_CSV, RESULTADOS, SEMENTE

BASE = ["bleu", "rouge1", "rouge2", "rougeL", "meteor", "comprimento"]
EMBEDDINGS = ["bertscore", "moverscore"]  # colunas adicionadas por metricas_embeddings.py
MULTIREF = [f"{m}_multiref" for m in ["bleu", "rouge1", "rouge2", "rougeL", "meteor"]]  # referencias_multiplas.py
VARIANTES = ["completo", "semprefixo"]


def tau(x, y) -> float:
    return kendalltau(x, y, variant="b").statistic


def indices_bootstrap(grupos: np.ndarray, B: int, rng: np.random.Generator) -> list[np.ndarray]:
    """Reamostra posts com reposição e devolve os índices dos itens de cada réplica."""
    unicos = np.unique(grupos)
    por_grupo = {g: np.flatnonzero(grupos == g) for g in unicos}
    out = []
    for _ in range(B):
        sorteio = rng.choice(unicos, size=len(unicos), replace=True)
        out.append(np.concatenate([por_grupo[g] for g in sorteio]))
    return out


def ic(valores: np.ndarray) -> tuple[float, float]:
    v = valores[~np.isnan(valores)]
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def tabela(df: pd.DataFrame, colunas: list[str], reamostras) -> pd.DataFrame:
    y = df.plausibilidade.to_numpy()
    linhas, taus_boot = [], {}
    for c in colunas:
        x = df[c].to_numpy()
        boot = np.array([tau(x[i], y[i]) for i in reamostras])
        taus_boot[c] = boot
        lo, hi = ic(boot)
        linhas.append(
            {
                "metrica": c,
                "n": len(df),
                "tau_b": tau(x, y),
                "ic95_inf": lo,
                "ic95_sup": hi,
                "spearman": spearmanr(x, y).statistic,
            }
        )
    return pd.DataFrame(linhas), taus_boot


# Família principal de comparações (P4): as 6 métricas de referência única, texto sem prefixo
# (variante principal, P2) -> 15 pares com correção de Holm. Os demais pares são exploratórios.
FAMILIA_PRINCIPAL = [f"{m}_semprefixo" for m in ["bleu", "rouge1", "rouge2", "rougeL", "meteor", "bertscore"]]


def p_bootstrap(d: np.ndarray) -> float:
    """p bilateral do bootstrap: 2 × a menor fração de réplicas de um lado do zero."""
    d = d[~np.isnan(d)]
    return float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean())))


def holm(p: pd.Series) -> pd.Series:
    """Correção de Holm-Bonferroni (step-down), com monotonicidade."""
    ordem = p.sort_values().index
    m = len(p)
    ajust, acum = {}, 0.0
    for k, i in enumerate(ordem):
        acum = max(acum, min(1.0, (m - k) * p[i]))
        ajust[i] = acum
    return pd.Series(ajust).reindex(p.index)


def delta_tau(df: pd.DataFrame, taus_boot: dict[str, np.ndarray]) -> pd.DataFrame:
    y = df.plausibilidade.to_numpy()
    linhas = []
    for a, b in itertools.combinations([c for c in taus_boot if not c.startswith("comprimento")], 2):
        d = taus_boot[a] - taus_boot[b]
        lo, hi = ic(d)
        linhas.append(
            {
                "metrica_a": a,
                "metrica_b": b,
                "delta_tau": tau(df[a], y) - tau(df[b], y),
                "ic95_inf": lo,
                "ic95_sup": hi,
                "p_boot": p_bootstrap(d),
                "familia_principal": a in FAMILIA_PRINCIPAL and b in FAMILIA_PRINCIPAL,
            }
        )
    out = pd.DataFrame(linhas)
    fam = out.familia_principal
    out["p_holm"] = np.nan
    if fam.any():
        out.loc[fam, "p_holm"] = holm(out.loc[fam, "p_boot"])
    out["significativo_holm"] = out.p_holm < 0.05
    out["significativo_ic95_exploratorio"] = ~((out.ic95_inf <= 0) & (0 <= out.ic95_sup))
    return out


def main() -> None:
    rng = np.random.default_rng(SEMENTE)
    df = pd.read_csv(METRICAS_CSV)
    multiref = RESULTADOS / "metricas_multiref.csv"
    if multiref.exists():  # OE2: entra automaticamente quando o arquivo existir
        df = df.merge(pd.read_csv(multiref), on=["modelo", "ques_id"], how="left")
    of = df[df.ofensivo].reset_index(drop=True)

    colunas = [
        f"{m}_{v}" for v in VARIANTES for m in BASE + EMBEDDINGS + MULTIREF if f"{m}_{v}" in of.columns
    ]
    reamostras = indices_bootstrap(of.post_id.to_numpy(), B_BOOTSTRAP, rng)

    geral, boot = tabela(of, colunas, reamostras)
    geral.to_csv(RESULTADOS / "correlacoes.csv", index=False)
    delta_tau(of, boot).to_csv(RESULTADOS / "delta_tau.csv", index=False)

    # sem cópias exatas
    sem = of[~of.copia_exata].reset_index(drop=True)
    r_sem = indices_bootstrap(sem.post_id.to_numpy(), B_BOOTSTRAP, rng)
    t_sem, _ = tabela(sem, colunas, r_sem)
    t_sem.to_csv(RESULTADOS / "correlacoes_sem_copias.csv", index=False)

    # por modelo
    por_modelo = []
    for modelo, g in of.groupby("modelo"):
        g = g.reset_index(drop=True)
        r = indices_bootstrap(g.post_id.to_numpy(), B_BOOTSTRAP, rng)
        t, _ = tabela(g, colunas, r)
        por_modelo.append(t.assign(modelo=modelo))
    pd.concat(por_modelo).to_csv(RESULTADOS / "correlacoes_por_modelo.csv", index=False)

    # divergências (prévia da SP3)
    cols = ["modelo", "post", "referencia", "gerada", "plausibilidade", "notas", "rougeL_semprefixo"]
    alta_metrica = of[of.plausibilidade == 0].sort_values("rougeL_semprefixo", ascending=False).head(50)
    alta_humano = of[(of.plausibilidade == 1) & (of.rougeL_semprefixo == 0)]
    pd.concat(
        [alta_metrica[cols].assign(tipo="metrica_alta_humano_0"),
         alta_humano[cols].assign(tipo="metrica_0_humano_1")]
    ).to_csv(RESULTADOS / "divergencias_rougeL.csv", index=False)

    pd.set_option("display.float_format", "{:.3f}".format)
    print(f"n = {len(of)} itens ofensivos, {of.post_id.nunique()} posts, B = {B_BOOTSTRAP}\n")
    print(geral.to_string(index=False))
    print(f"\nSem as {of.copia_exata.sum()} cópias exatas:")
    print(t_sem[["metrica", "tau_b"]].to_string(index=False))
    print("\nτ por modelo (sem prefixo):")
    pm = pd.concat(por_modelo)
    pm = pm[pm.metrica.str.endswith("semprefixo")]
    print(pm.pivot(index="metrica", columns="modelo", values="tau_b").to_string())
    print(f"\n-> {RESULTADOS}")


if __name__ == "__main__":
    main()
