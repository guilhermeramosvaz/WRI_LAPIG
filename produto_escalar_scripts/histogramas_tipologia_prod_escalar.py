"""
histogramas_tipologia_prod_escalar.py
=====================================
Gera dois histogramas a partir do prod_escalar_50k.parquet:

  1. Grafico de barras comparativo: Amostras Existentes vs. Amostras Representadas (>= LIMIAR) por Tipologia_
  2. Distribuicao completa do produto escalar (sem filtro) por Tipologia_

Uso:
    python histogramas_tipologia_prod_escalar.py               # default: limiar = 0.75
    python histogramas_tipologia_prod_escalar.py --limiar 0     # sem limiar
    python histogramas_tipologia_prod_escalar.py --limiar 0.75
"""

import argparse
import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------------
# Argumentos de linha de comando
# ----------------------------------------------------------------
parser = argparse.ArgumentParser(description="Histogramas de tipologia por produto escalar.")
parser.add_argument("--limiar", type=float, default=0.75,
                    help="Limiar mínimo de similaridade (default: 0.75). Use 0 para sem limiar.")
parser.add_argument("--year", default="2025",
                    help="Ano a processar (default: 2025).")
args = parser.parse_args()

LIMIAR = args.limiar
ANO = args.year
SEM_LIMIAR = (LIMIAR <= 0)
LIMIAR_LABEL = "sem_limiar" if SEM_LIMIAR else str(int(LIMIAR * 100))
LIMIAR_DISPLAY = "sem limiar (todos)" if SEM_LIMIAR else f">= {LIMIAR}"

# ----------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------
DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_ARQUIVOS_BASE = DIR_METRICAS / "arquivos_base"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_SAIDA_LIMIAR = DIR_SAIDA / LIMIAR_LABEL
DIR_SAIDA_LIMIAR.mkdir(parents=True, exist_ok=True)

PARQUET = DIR_METRICAS / f"prod_escalar_50k_{ANO}.parquet"
if not PARQUET.exists():
    alt = DIR_METRICAS / "prod_escalar_50k_serie_completa.parquet"
    if alt.exists():
        PARQUET = alt
    else:
        alt2 = DIR_SAIDA / "prod_escalar_50k_serie_completa.parquet"
        if alt2.exists():
            PARQUET = alt2
        else:
            alt3 = DIR_SAIDA / "prod_escalar_50k.parquet"
            if alt3.exists():
                PARQUET = alt3

COLUNA_ID = "TARGET_FID"
COLUNA_TIPOLOGIA = "Tipologia_"

# Paleta de cores oficial Embrapa (mesma usada no pipeline 11k)
CORES_TIPOLOGIA = {
    "PASTO PRODUTIVO": "#faea40",
    "PASTO COM ERVAS": "#d8ff6c",
    "REG NATURAL": "#0e5f0e",
    "INTERMEDIARIO": "#f4b346",
    "DEG BIOLOGICA": "#813209",
    "PASTO COM LENHOSAS": "#66c600",
    "MISCELANEA": "#ec2b10",
}


def estilo_limpo(ax):
    ax.set_facecolor("white")
    ax.figure.set_facecolor("white")
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(axis="both", length=0, labelsize=10, colors="#333333")


# ----------------------------------------------------------------
# Carregar dados via DuckDB (35M linhas — não cabe em pandas direto)
# ----------------------------------------------------------------
print(f"Carregando dados via DuckDB ({LIMIAR_DISPLAY})...")
con = duckdb.connect()

# Contagem total de pares
n_total = con.execute(f"SELECT count(*) FROM '{PARQUET}'").fetchone()[0]
print(f"  {n_total:,} pares no prod_escalar")

# Amostras totais por tipologia (IDs únicos de TARGET_FID)
df_total = con.execute(f"""
    SELECT {COLUNA_TIPOLOGIA}, count(distinct {COLUNA_ID}) as n_amostras
    FROM '{PARQUET}'
    GROUP BY {COLUNA_TIPOLOGIA}
    ORDER BY n_amostras DESC
""").fetchdf()

ordem = df_total[COLUNA_TIPOLOGIA].tolist()
cores = {tip: CORES_TIPOLOGIA.get(tip, "#cccccc") for i, tip in enumerate(ordem)}
amostras_total = df_total.set_index(COLUNA_TIPOLOGIA)["n_amostras"]

# ================================================================
# GRAFICO 1: Comparacao de Amostras (Total vs. Match >= LIMIAR)
# ================================================================
print(f"\nGerando histograma 1: comparacao de amostras {LIMIAR_DISPLAY}...")

if SEM_LIMIAR:
    # Sem limiar: todas as amostras contam como representadas
    amostras_filtradas = amostras_total.copy()
else:
    # Amostras com pelo menos 1 match >= LIMIAR
    df_filt = con.execute(f"""
        SELECT {COLUNA_TIPOLOGIA}, count(distinct {COLUNA_ID}) as n_amostras
        FROM '{PARQUET}'
        WHERE resultado_multiplicacao >= {LIMIAR}
        GROUP BY {COLUNA_TIPOLOGIA}
    """).fetchdf()
    amostras_filtradas = df_filt.set_index(COLUNA_TIPOLOGIA)["n_amostras"].reindex(ordem).fillna(0).astype(int)

# Porcentagem representada
pct_representada = (amostras_filtradas / amostras_total * 100).round(1)

# Configuracao do grafico de barras agrupadas
fig, ax = plt.subplots(figsize=(12, 7))
fig.subplots_adjust(top=0.82, bottom=0.22)

x = np.arange(len(ordem))
largura = 0.35

# Barras de Amostras Existentes (Total)
barras_totais = ax.bar(x - largura/2, amostras_total.reindex(ordem).values, largura,
                       label="Amostras Totais (Existentes)",
                       color="#e0e0e0", edgecolor="#888888", linewidth=0.7, zorder=3)

# Barras de Amostras Representadas (Match >= LIMIAR)
barras_filtradas = ax.bar(x + largura/2, amostras_filtradas.reindex(ordem).values, largura,
                          label=f"Amostras Representadas ({LIMIAR_DISPLAY})",
                          color=[cores[t] for t in ordem], edgecolor="#555555", linewidth=0.7, zorder=3)

# Rotulos das barras de totais
for barra in barras_totais:
    val = int(barra.get_height())
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + amostras_total.max() * 0.015,
            f"{val}",
            ha="center", va="bottom", fontsize=8.5, color="#666666", fontweight="bold")

# Rotulos das barras de representadas (com porcentagem)
for i, barra in enumerate(barras_filtradas):
    val = int(barra.get_height())
    pct_val = pct_representada.reindex(ordem).iloc[i]
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + amostras_total.max() * 0.015,
            f"{val}\n({pct_val}%)",
            ha="center", va="bottom", fontsize=8.5, color="#222222", fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(ordem, rotation=30, ha="right", fontsize=10)
ax.set_ylabel("Quantidade de Amostras de Campo (TARGET_FID)", fontsize=11, color="#333333")
ax.set_xlabel("Tipologia", fontsize=11, color="#333333")
ax.set_ylim(0, amostras_total.max() * 1.20)
ax.legend(fontsize=10, loc="upper right")

estilo_limpo(ax)
total_filt = int(amostras_filtradas.sum())
total_all = int(amostras_total.sum())
fig.text(0.06, 0.97,
         f"Representatividade das Amostras de Campo no MapBiomas ({LIMIAR_DISPLAY})",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
fig.text(0.06, 0.925,
         f"{total_filt} de {total_all} amostras de campo ({total_filt/total_all*100:.1f}%) possuem pelo menos 1 match",
         fontsize=10.5, color="#666666", ha="left", va="top")

caminho1 = DIR_SAIDA_LIMIAR / "histograma_tipologia_comparacao_amostras.png"
fig.savefig(caminho1, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho1.name}")

# Imprimir tabela no console
print(f"\n  {'Tipologia':<25s} {'Existentes':>12s} {'Com Match':>12s} {'Representado (%)':>18s}")
print("  " + "-" * 71)
for tip in ordem:
    t = int(amostras_total[tip])
    f = int(amostras_filtradas.reindex(ordem)[tip])
    p = pct_representada.reindex(ordem)[tip]
    print(f"  {tip:<25s} {t:>12,} {f:>12,} {p:>17.1f}%")


# ================================================================
# GRAFICO 2: Distribuicao completa do produto escalar por Tipologia_
# ================================================================
print(f"\nGerando histograma 2: distribuicao completa por Tipologia_...")

# Amostrar para performance (35M é pesado para histograma sobreposto)
n_amostra = min(500_000, n_total)
df_amostra = con.execute(f"""
    SELECT {COLUNA_TIPOLOGIA}, resultado_multiplicacao
    FROM '{PARQUET}'
    USING SAMPLE {n_amostra}
""").fetchdf()

fig, ax = plt.subplots(figsize=(13, 7))
fig.subplots_adjust(top=0.85, bottom=0.12)

bins = np.arange(0.15, 1.005, 0.01)

for tip in ordem:
    vals = df_amostra.loc[df_amostra[COLUNA_TIPOLOGIA] == tip, "resultado_multiplicacao"].values
    if len(vals) > 0:
        ax.hist(vals, bins=bins, alpha=0.55, color=cores[tip],
                label=f"{tip} (n={len(vals):,})", density=True, edgecolor="none")

# Linha vertical no limiar (apenas se tiver limiar)
if not SEM_LIMIAR:
    ax.axvline(LIMIAR, color="#e74c3c", linestyle="--", linewidth=2,
               label=f"Limiar = {LIMIAR}", zorder=5)

ax.set_xlabel("Produto Escalar (Similaridade Cosseno)", fontsize=11, color="#333333")
ax.set_ylabel("Densidade", fontsize=11, color="#333333")
ax.legend(fontsize=8.5, loc="upper left", framealpha=0.9, ncol=2)

estilo_limpo(ax)
fig.text(0.06, 0.96,
         "Distribuicao do Produto Escalar por Tipologia (sem filtro)",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
subtitle = f"Amostra de {n_amostra:,} pares | Todas as tipologias sobrepostas"
if not SEM_LIMIAR:
    subtitle += f" | Limiar = {LIMIAR}"
fig.text(0.06, 0.92, subtitle,
         fontsize=10.5, color="#666666", ha="left", va="top")

caminho2 = DIR_SAIDA_LIMIAR / "histograma_tipologia_distribuicao_completa.png"
fig.savefig(caminho2, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho2.name}")

print(f"\nConcluido. Graficos salvos em {DIR_SAIDA_LIMIAR}")
