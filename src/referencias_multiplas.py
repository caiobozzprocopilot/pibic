"""OE2 — referência única (a do FEB) vs. múltiplas referências (todas as do SBIC).

No SBIC (Sap et al., 2020) cada post foi anotado por vários anotadores, e cada um pode
ter escrito uma implicação (`targetStereotype`) diferente. O FEB usa só uma delas como
referência. Aqui juntamos todas as implicações distintas de cada post e recalculamos as
métricas contra o conjunto:
- BLEU: multi-referência nativo do sacrebleu;
- ROUGE-1/2/L e METEOR: máximo sobre as referências (convenção usual).

Precisa do SBIC v2 em data/raw/SBIC.v2/ (SBIC.v2.trn.csv, .dev.csv, .tst.csv).
Download: https://maartensap.com/social-bias-frames/SBIC.v2.tgz  (bloqueado no ambiente
da Coordenação; rodar no Colab ou localmente).

Saída: results/metricas_multiref.csv  (colunas *_multiref_semprefixo + n_refs)
       results/referencias_sbic_por_item.jsonl  (referências de cada item, para src/curva_k.py)
Depois: python src/correlacoes.py  (o arquivo é incorporado automaticamente)

Uso:  python src/referencias_multiplas.py
"""
from __future__ import annotations

import re

import pandas as pd
from nltk.translate.meteor_score import meteor_score
from sacrebleu.metrics import BLEU

from config import DADOS_RAW, METRICAS_CSV, RESULTADOS
from metricas_lexicais import _rouge, limpar, tokens

SBIC_DIR = DADOS_RAW / "SBIC.v2"
_bleu = BLEU(effective_order=True)


def norm_post(t: str) -> str:
    return re.sub(r"\s+", " ", str(t)).strip().lower()


def carregar_sbic() -> pd.DataFrame:
    partes = [pd.read_csv(p) for p in sorted(SBIC_DIR.glob("SBIC.v2.*.csv"))]
    if not partes:
        raise SystemExit(f"SBIC não encontrado em {SBIC_DIR}. Veja o docstring.")
    s = pd.concat(partes, ignore_index=True)
    s = s[s.targetStereotype.notna() & (s.targetStereotype.str.strip() != "")]
    s["chave"] = s.post.map(norm_post)
    return (
        s.groupby("chave")["targetStereotype"]
        .agg(lambda x: sorted({limpar(v, False) for v in x}))
        .rename("refs_sbic")
        .reset_index()
    )


def main() -> None:
    df = pd.read_csv(METRICAS_CSV)
    of = df[df.ofensivo].copy()
    of["chave"] = of.post.map(norm_post)
    of = of.merge(carregar_sbic(), on="chave", how="left")

    sem_match = of.refs_sbic.isna().sum()
    print(f"Itens ofensivos sem post correspondente no SBIC: {sem_match} de {len(of)}")

    linhas, refs_por_item = [], []
    for _, r in of.iterrows():
        ref_feb = limpar(r.referencia, True)
        refs = [limpar(x, True) for x in (r.refs_sbic if isinstance(r.refs_sbic, list) else [])]
        refs = sorted({x for x in refs + [ref_feb] if x})  # garante que a do FEB está incluída
        g = limpar(r.gerada, True)
        tg = tokens(g)
        rouges = [_rouge.score(x, g) for x in refs]
        refs_por_item.append({"modelo": r.modelo, "ques_id": int(r.ques_id), "ref_feb": ref_feb, "refs": refs})
        linhas.append(
            {
                "modelo": r.modelo,
                "ques_id": r.ques_id,
                "n_refs": len(refs),
                "bleu_multiref_semprefixo": _bleu.sentence_score(g, refs).score / 100 if tg else 0.0,
                "rouge1_multiref_semprefixo": max(x["rouge1"].fmeasure for x in rouges),
                "rouge2_multiref_semprefixo": max(x["rouge2"].fmeasure for x in rouges),
                "rougeL_multiref_semprefixo": max(x["rougeL"].fmeasure for x in rouges),
                "meteor_multiref_semprefixo": meteor_score([tokens(x) for x in refs], tg) if tg else 0.0,
            }
        )
    out = pd.DataFrame(linhas)
    out.to_csv(RESULTADOS / "metricas_multiref.csv", index=False)
    # lista de referências por item, usada pela curva com k fixo (src/curva_k.py, P8)
    pd.DataFrame(refs_por_item).to_json(RESULTADOS / "referencias_sbic_por_item.jsonl",
                                         orient="records", lines=True, force_ascii=False)
    print(out.n_refs.describe().to_string())
    print(f"-> {RESULTADOS / 'metricas_multiref.csv'}")


if __name__ == "__main__":
    main()
