"""BERTScore e MoverScore por item (OE1). **Rodar no Google Colab com GPU.**

Lê results/metricas_por_item.csv, adiciona as colunas
    bertscore_{completo,semprefixo}, moverscore_{completo,semprefixo}
e grava de volta no mesmo arquivo. Depois, rode `python src/correlacoes.py`.

Configuração:
- BERTScore: roberta-large (padrão do bert-score para inglês), F1, rescale_with_baseline=True
  (o reescalonamento é monotônico: não muda τ nem ρ, só deixa os valores legíveis).
- MoverScore: implementação v2 (distilbert-base-uncased), unigramas, IDF calculado
  no próprio conjunto (referências e geradas separadamente), sem stopwords.

Uso (Colab):
    pip install -r requirements-colab.txt
    python src/metricas_embeddings.py [--so-bertscore]
"""
from __future__ import annotations

import argparse
import os

import pandas as pd

from config import METRICAS_CSV
from metricas_lexicais import limpar


def bertscore(ger: list[str], ref: list[str]) -> list[float]:
    from bert_score import score

    _, _, f1 = score(ger, ref, lang="en", rescale_with_baseline=True, batch_size=64, verbose=True)
    return f1.tolist()


def moverscore(ger: list[str], ref: list[str]) -> list[float]:
    os.environ.setdefault("MOVERSCORE_MODEL", "distilbert-base-uncased")
    from moverscore_v2 import get_idf_dict, word_mover_score

    idf_ref = get_idf_dict(ref)
    idf_ger = get_idf_dict(ger)
    return word_mover_score(
        ref, ger, idf_ref, idf_ger, stop_words=[], n_gram=1, remove_subwords=True, batch_size=48
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-bertscore", action="store_true", help="pula o MoverScore")
    args = ap.parse_args()

    df = pd.read_csv(METRICAS_CSV)
    for variante, tirar in [("completo", False), ("semprefixo", True)]:
        ger = [limpar(t, tirar) or "." for t in df.gerada]  # string vazia quebra os tokenizadores
        ref = [limpar(t, tirar) or "." for t in df.referencia]
        print(f"BERTScore ({variante})...")
        df[f"bertscore_{variante}"] = bertscore(ger, ref)
        if not args.so_bertscore:
            print(f"MoverScore ({variante})...")
            df[f"moverscore_{variante}"] = moverscore(ger, ref)
        df.to_csv(METRICAS_CSV, index=False)  # grava a cada variante (Colab pode cair)
    print(f"-> {METRICAS_CSV}")


if __name__ == "__main__":
    main()
