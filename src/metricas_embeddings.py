"""BERTScore e MoverScore por instância nos itens ofensivos do FEB/SBIC.

Precisa de acesso ao HuggingFace (rode no Colab ou na máquina do grupo):
    pip install bert-score moverscore pyemd pandas
    python src/carregar_feb.py && python src/metricas_embeddings.py
Saída: data/feb_sbic_metricas_embeddings.csv (mesmo formato de metricas_lexicais.csv)
Depois: python src/correlacoes.py data/feb_sbic_metricas_lexicais.csv data/feb_sbic_metricas_embeddings.csv
"""
import pandas as pd
from bert_score import score as bertscore
from metricas_lexicais import tira_prefixo

def moverscore(ger, ref):
    try:
        from moverscore_v2 import get_idf_dict, word_mover_score
    except ImportError:
        print("moverscore não instalado; pulando"); return None
    idf_h, idf_r = get_idf_dict(ger), get_idf_dict(ref)
    return word_mover_score(ref, ger, idf_r, idf_h, stop_words=[], n_gram=1, remove_subwords=True)

if __name__ == "__main__":
    itens = pd.read_csv("data/feb_sbic_itens.csv")
    of = itens[itens.ofensivo].reset_index(drop=True)
    saida = []
    for var, f in [("completo", str), ("sem_prefixo", tira_prefixo)]:
        ger = [f(t) for t in of.gerada]; ref = [f(t) for t in of.referencia]
        # roberta-large, camada padrão; rescale_with_baseline só muda escala, não a ordem
        _, _, F = bertscore(ger, ref, lang="en", rescale_with_baseline=False, verbose=True)
        d = of[["modelo", "ques_id"]].assign(variante=var, bertscore=F.numpy())
        ms = moverscore(ger, ref)
        if ms is not None:
            d["moverscore"] = ms
        saida.append(d)
    pd.concat(saida).to_csv("data/feb_sbic_metricas_embeddings.csv", index=False)
    print("ok")
