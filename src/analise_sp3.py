"""SP3 — consolida a anotação da tipologia e mede concordância.

Lê results/sp3_anotacao_cega_final.xlsx (aba "Anotação"):
- M  "Sugerida"            -> heurística de src/amostra_sp3.py
- P  "CATEGORIA FINAL"          -> anotação final, feita pelo Claude em 27/09/2026,
                                  sem validação humana (decisão do Caio; P9 descartada)
- Q  "Justificativa (Claude)"
- R  "Leitura literal?"         -> padrão emergente (candidato à categoria A5)
Validação humana independente: results/sp3_validacao_humana.xlsx (40 itens às cegas,
gerado por src/amostra_validacao_sp3.py). Se a coluna "Categoria (humano)" estiver
preenchida, o script calcula a concordância e o κ Claude × humano nesses itens.

Calcula distribuição por categoria e concordância (% e kappa de Cohen) entre
heurística e anotação final, por direção.

Saída: results/sp3_resumo.csv, results/sp3_concordancia.csv
Uso:   python src/analise_sp3.py
"""
from __future__ import annotations

import pandas as pd
from openpyxl import load_workbook

from config import RESULTADOS

PLANILHA = RESULTADOS / "sp3_anotacao_cega_final.xlsx"


def kappa(a: pd.Series, b: pd.Series) -> float:
    """Kappa de Cohen para dois rótulos nominais (sem dependência do sklearn)."""
    n = len(a)
    if n == 0:
        return float("nan")
    po = (a.values == b.values).mean()
    cats = set(a) | set(b)
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def ler() -> pd.DataFrame:
    ws = load_workbook(PLANILHA, data_only=True)["Anotação"]
    linhas = [[c.value for c in r] for r in ws.iter_rows()]
    df = pd.DataFrame(linhas[1:], columns=linhas[0])
    df = df[df["ID"].notna()].copy()
    df["direcao"] = df["ID"].str[0]
    df = df.rename(columns={"Sugerida": "heuristica", "CATEGORIA FINAL": "claude", "CATEGORIA FINAL (Claude)": "claude",
                            "Categoria (humano)": "humano"})
    df = df.drop(columns=["humano"], errors="ignore")
    val = RESULTADOS / "sp3_validacao_humana.xlsx"
    df["humano"] = None
    if val.exists():
        wv = load_workbook(val, data_only=True)["Anotação"]
        lv = [[c.value for c in r] for r in wv.iter_rows()]
        v = pd.DataFrame(lv[1:], columns=lv[0])[["ID", "Categoria (humano)"]].dropna()
        df = df.drop(columns=["humano"]).merge(
            v.rename(columns={"Categoria (humano)": "humano"}), on="ID", how="left")
    return df


def main() -> None:
    df = ler()
    anotadores = [c for c in ["heuristica", "claude", "humano"] if df[c].notna().any()]

    # distribuição
    dist = pd.concat(
        {a: df.groupby(["direcao", a]).size() for a in anotadores}, axis=1
    ).fillna(0).astype(int)
    dist.index.names = ["direcao", "categoria"]
    dist.to_csv(RESULTADOS / "sp3_resumo.csv")

    # concordância par a par, total e por subconjunto (cego / não cego)
    linhas = []
    for i, a in enumerate(anotadores):
        for b in anotadores[i + 1:]:
            for nome, sub in [("todos", df), ("direcao_A", df[df.direcao == "A"]),
                              ("direcao_B", df[df.direcao == "B"])]:
                # pares com o humano só existem nos itens da validação (os demais ficam NaN)
                s = sub[sub[a].notna() & sub[b].notna()]
                linhas.append({"par": f"{a} x {b}", "subconjunto": nome, "n": len(s),
                               "concordancia": (s[a] == s[b]).mean() if len(s) else float("nan"),
                               "kappa": kappa(s[a], s[b])})
    conc = pd.DataFrame(linhas)
    conc.to_csv(RESULTADOS / "sp3_concordancia.csv", index=False)

    pd.set_option("display.float_format", "{:.2f}".format)
    print("Anotadores com dados:", ", ".join(anotadores))
    print(dist.to_string())
    print()
    print(conc.to_string(index=False))
    lit = (df["Leitura literal?"] == "sim").sum()
    print(f"\nLeitura literal: {lit} de {len(df)} itens")
    n_h = df["humano"].notna().sum()
    print(f"Itens com anotação humana independente: {n_h}" + ("" if n_h else " (validação pendente)"))


if __name__ == "__main__":
    main()
