"""Correlação por instância entre métricas automáticas e plausibilidade humana (FEB/SBIC, itens ofensivos).

- Kendall tau-b e Spearman rho (escala humana ordinal, com empates)
- IC 95% por bootstrap por agrupamento em posts (o mesmo post aparece para vários modelos)
- Diferença pareada de tau entre métricas, com IC bootstrap
- Linha de base: comprimento (nº de palavras) da explicação gerada
Aceita qualquer CSV de métricas com colunas modelo, ques_id, variante, <métricas...>
Uso: python src/correlacoes.py data/feb_sbic_metricas_lexicais.csv [outros.csv ...]
"""
import sys, itertools
import numpy as np, pandas as pd
from scipy.stats import kendalltau, spearmanr

B = 2000
rng = np.random.default_rng(42)

def carrega(arqs):
    itens = pd.read_csv("data/feb_sbic_itens.csv")
    of = itens[itens.ofensivo][["modelo", "ques_id", "post", "gerada", "plaus_gerada"]]
    of = of.assign(comprimento=of.gerada.str.split().str.len())
    ms = [pd.read_csv(a) for a in arqs]
    m = ms[0]
    for x in ms[1:]:
        m = m.merge(x, on=["modelo", "ques_id", "variante"], how="outer")
    return of.merge(m, on=["modelo", "ques_id"])

def tau(x, y):
    return kendalltau(x, y, variant="b").statistic

def boot_idx(df):
    grupos = df.groupby("post").indices
    chaves = list(grupos)
    for _ in range(B):
        esc = rng.choice(len(chaves), len(chaves), replace=True)
        yield np.concatenate([grupos[chaves[i]] for i in esc])

def tabela(df, metricas):
    h = df.plaus_gerada.to_numpy()
    X = {m: df[m].to_numpy() for m in metricas}
    pontos = {m: (tau(X[m], h), spearmanr(X[m], h).statistic) for m in metricas}
    bt = {m: [] for m in metricas}
    for idx in boot_idx(df.reset_index(drop=True)):
        for m in metricas:
            bt[m].append(tau(X[m][idx], h[idx]))
    linhas = []
    for m in metricas:
        lo, hi = np.nanpercentile(bt[m], [2.5, 97.5])
        linhas.append(dict(metrica=m, n=len(df), kendall_tau=pontos[m][0], ic95_inf=lo, ic95_sup=hi,
                           spearman_rho=pontos[m][1]))
    return pd.DataFrame(linhas), {m: np.array(v) for m, v in bt.items()}

if __name__ == "__main__":
    arqs = sys.argv[1:] or ["data/feb_sbic_metricas_lexicais.csv"]
    dados = carrega(arqs)
    metricas = [c for c in dados.columns if c not in
                ("modelo", "ques_id", "post", "gerada", "plaus_gerada", "variante")]
    saidas = []
    for var, d in dados.groupby("variante"):
        d = d.reset_index(drop=True)
        t, bt = tabela(d, metricas)
        t.insert(0, "escopo", "todos"); t.insert(0, "variante", var)
        saidas.append(t)
        print(f"\n=== variante={var} | todos os modelos (n={len(d)}) ===")
        print(t.drop(columns=["variante", "escopo"]).round(3).to_string(index=False))
        # diferenças pareadas
        print("  diferenças pareadas de tau (IC95% bootstrap):")
        for a, b in itertools.combinations([m for m in metricas if m != "comprimento"], 2):
            dif = bt[a] - bt[b]
            lo, hi = np.nanpercentile(dif, [2.5, 97.5])
            marca = "*" if lo > 0 or hi < 0 else ""
            print(f"    {a:>10} - {b:<10} {np.nanmean(dif):+.3f} [{lo:+.3f}, {hi:+.3f}] {marca}")
        for mod, dm in d.groupby("modelo"):
            tm, _ = tabela(dm.reset_index(drop=True), metricas)
            tm.insert(0, "escopo", mod); tm.insert(0, "variante", var)
            saidas.append(tm)
    res = pd.concat(saidas)
    res.to_csv("results/correlacoes.csv", index=False)
    piv = res.pivot_table(index=["variante", "metrica"], columns="escopo", values="kendall_tau").round(3)
    print("\nKendall tau por modelo:\n", piv)
