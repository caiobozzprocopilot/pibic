"""Monta a tabela de itens (1 linha = 1 explicação gerada avaliada) a partir do FEB/SBIC.

Entrada : data/raw/feb/human_eval/results/sbic/*.csv (resultados brutos do MTurk)
Saída   : data/processed/feb_sbic_itens.csv

Convenções (conferidas no código do FEB, scripts/compute_kappa.py):
- `Input.{k}_gt_idx = 0`  -> a referência (gold) é a explicação e1 (`explanation_{k}_i`);
                              a gerada é a e2 (`explanation_{k}_j`). Com 1, o inverso.
- `Input.gt_{k}`          -> rótulo do post: 0 = ofensivo, 1 = não ofensivo.
  (O comentário em compute_kappa.py descreve as duas colunas trocadas; o código está certo.)
- Plausibilidade de um item = média das notas dos anotadores com
  yes = 1, w_yes = 2/3, w_no = 1/3, no = 0.

Uso:  python src/carregar_feb.py
"""
from __future__ import annotations

import re
import sys

import pandas as pd

from config import DADOS_PROC, FEB_SBIC_RESULTADOS, ITENS_CSV, MAPA_PLAUSIBILIDADE, MODELOS


def modelo_do_arquivo(nome: str) -> str:
    chave = nome.split("_", 1)[0]
    if chave not in MODELOS:
        raise ValueError(f"Arquivo inesperado: {nome}")
    return MODELOS[chave]


def ler_julgamentos() -> pd.DataFrame:
    arquivos = sorted(FEB_SBIC_RESULTADOS.glob("*.csv"))
    if not arquivos:
        sys.exit(
            f"Nenhum CSV em {FEB_SBIC_RESULTADOS}.\n"
            "Clone o FEB primeiro: git clone https://github.com/allenai/feb.git data/raw/feb"
        )
    linhas = []
    for arq in arquivos:
        modelo = modelo_do_arquivo(arq.name)
        df = pd.read_csv(arq)
        for i, r in df.iterrows():
            for k in range(1, 11):
                gt_idx = int(r[f"Input.{k}_gt_idx"])
                e_i, e_j = r[f"Input.explanation_{k}_i"], r[f"Input.explanation_{k}_j"]
                resp_e1, resp_e2 = r[f"Answer.{k}-e1"], r[f"Answer.{k}-e2"]
                if gt_idx == 0:
                    ref, ger, nota_ref, nota_ger = e_i, e_j, resp_e1, resp_e2
                else:
                    ref, ger, nota_ref, nota_ger = e_j, e_i, resp_e2, resp_e1
                linhas.append(
                    {
                        "modelo": modelo,
                        "ques_id": int(r[f"Input.{k}_ques_id"]),
                        "hit": i,  # os CSVs públicos não trazem WorkerId; cada linha = 1 HIT de 1 anotador
                        "post": r[f"Input.question_{k}"],
                        "referencia": ref,
                        "gerada": ger,
                        "ofensivo": int(r[f"Input.gt_{k}"]) == 0,
                        "nota_ger": nota_ger,
                        "nota_ref": nota_ref,
                    }
                )
    return pd.DataFrame(linhas)


def agregar(j: pd.DataFrame) -> pd.DataFrame:
    j = j.copy()
    j["p_ger"] = j["nota_ger"].map(MAPA_PLAUSIBILIDADE)
    j["p_ref"] = j["nota_ref"].map(MAPA_PLAUSIBILIDADE)
    if j[["p_ger", "p_ref"]].isna().any().any():
        raise ValueError("Resposta fora da escala yes/w_yes/w_no/no")

    chave = ["modelo", "ques_id"]
    itens = (
        j.groupby(chave)
        .agg(
            post=("post", "first"),
            referencia=("referencia", "first"),
            gerada=("gerada", "first"),
            ofensivo=("ofensivo", "first"),
            n_anotadores=("nota_ger", "size"),
            plausibilidade=("p_ger", "mean"),
            plausibilidade_ref=("p_ref", "mean"),
            notas=("nota_ger", lambda s: "|".join(s)),
        )
        .reset_index()
    )
    # identificador do post (o mesmo post aparece para vários modelos) -> usado no bootstrap agrupado
    itens["post_id"] = pd.factorize(itens["post"])[0]
    norm = lambda s: re.sub(r"\s+", " ", str(s).strip().lower().rstrip("."))
    itens["copia_exata"] = itens["gerada"].map(norm) == itens["referencia"].map(norm)
    return itens


def main() -> None:
    j = ler_julgamentos()
    itens = agregar(j)
    DADOS_PROC.mkdir(parents=True, exist_ok=True)
    itens.to_csv(ITENS_CSV, index=False)

    of = itens[itens.ofensivo]
    print(f"Julgamentos: {len(j)}  |  itens: {len(itens)}  |  posts distintos: {itens.post_id.nunique()}")
    print(itens.groupby("modelo").size().to_string())
    print(f"Anotadores por item: {itens.n_anotadores.value_counts().to_dict()}")
    print(f"Itens ofensivos: {len(of)}  |  não ofensivos: {len(itens) - len(of)}")
    print(f"Não ofensivos com gerada = referência: {itens[~itens.ofensivo].copia_exata.mean():.1%}")
    print(f"Ofensivos com cópia exata: {of.copia_exata.sum()} (plaus. média {of[of.copia_exata].plausibilidade.mean():.2f})")
    print(f"Ofensivos com plausibilidade 0: {(of.plausibilidade == 0).sum()}  |  dp: {of.plausibilidade.std():.2f}")
    print(f"-> {ITENS_CSV}")


if __name__ == "__main__":
    main()
