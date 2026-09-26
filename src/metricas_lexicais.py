"""Métricas de n-gramas por item: BLEU, ROUGE-1/2/L, METEOR, e comprimento (linha de base).

Cada métrica é calculada em duas variantes de texto:
- `completo`    : explicação como está;
- `semprefixo`  : sem o molde "this post implies that" (idêntico entre gerada e referência).

Entrada : data/processed/feb_sbic_itens.csv
Saída   : results/metricas_por_item.csv

Uso:  python src/metricas_lexicais.py
Obs.: METEOR precisa do WordNet (`python -m nltk.downloader wordnet omw-1.4`).
"""
from __future__ import annotations

import re

import nltk
import pandas as pd
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from sacrebleu.metrics import BLEU

from config import ITENS_CSV, METRICAS_CSV, PREFIXO, RESULTADOS

_bleu = BLEU(effective_order=True)  # BLEU por sentença com suavização padrão do sacrebleu
_rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)  # padrão da biblioteca; com stemmer, 295 itens com ROUGE-L = 0 em vez de 311
_tok = re.compile(r"[a-z0-9']+")


def limpar(texto: str, tirar_prefixo: bool) -> str:
    t = str(texto).strip().lower()
    if tirar_prefixo:
        t = re.sub(PREFIXO, "", t)
    return t.rstrip(". ")


def tokens(t: str) -> list[str]:
    return _tok.findall(t)


def metricas(ger: str, ref: str) -> dict[str, float]:
    r = _rouge.score(ref, ger)
    tg, tr = tokens(ger), tokens(ref)
    return {
        "bleu": _bleu.sentence_score(ger, [ref]).score / 100 if tg else 0.0,
        "rouge1": r["rouge1"].fmeasure,
        "rouge2": r["rouge2"].fmeasure,
        "rougeL": r["rougeL"].fmeasure,
        "meteor": meteor_score([tr], tg) if tg and tr else 0.0,
        "comprimento": len(tg),
    }


def main() -> None:
    for rec in ("wordnet", "omw-1.4"):
        try:
            nltk.data.find(f"corpora/{rec}.zip")
        except LookupError:
            nltk.download(rec, quiet=True)

    itens = pd.read_csv(ITENS_CSV)
    blocos = [itens]
    for variante, tirar in [("completo", False), ("semprefixo", True)]:
        linhas = [
            metricas(limpar(g, tirar), limpar(r, tirar))
            for g, r in zip(itens.gerada, itens.referencia)
        ]
        blocos.append(pd.DataFrame(linhas).add_suffix(f"_{variante}"))
    out = pd.concat(blocos, axis=1)

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    out.to_csv(METRICAS_CSV, index=False)

    of = out[out.ofensivo]
    zero = of.rougeL_semprefixo == 0
    print(f"Itens ofensivos: {len(of)}")
    print(f"ROUGE-L = 0 sem prefixo: {zero.sum()} ({zero.mean():.0%}); "
          f"plaus. média {of[zero].plausibilidade.mean():.2f}; "
          f"com nota máxima: {(of[zero].plausibilidade == 1).sum()}")
    print(f"-> {METRICAS_CSV}")


if __name__ == "__main__":
    main()
