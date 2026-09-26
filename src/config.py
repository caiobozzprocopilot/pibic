"""Caminhos e constantes compartilhados pelos scripts."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS_RAW = RAIZ / "data" / "raw"
DADOS_PROC = RAIZ / "data" / "processed"
RESULTADOS = RAIZ / "results"

# Repositório do FEB (Marasović et al., 2022). Clonar com:
#   git clone https://github.com/allenai/feb.git data/raw/feb
FEB_DIR = DADOS_RAW / "feb"
FEB_SBIC_RESULTADOS = FEB_DIR / "human_eval" / "results" / "sbic"

ITENS_CSV = DADOS_PROC / "feb_sbic_itens.csv"
METRICAS_CSV = RESULTADOS / "metricas_por_item.csv"

# Escala de plausibilidade usada pelo próprio FEB (scripts/compute_kappa.py)
MAPA_PLAUSIBILIDADE = {"yes": 1.0, "w_yes": 2 / 3, "w_no": 1 / 3, "no": 0.0}

# Molde presente em quase todas as explicações do SBIC
PREFIXO = r"^\s*this post implies that\s*"

MODELOS = {"gpt3": "GPT-3", "3b": "T5-3B", "large": "T5-large", "base": "T5-base"}

SEMENTE = 20262027
B_BOOTSTRAP = 2000
