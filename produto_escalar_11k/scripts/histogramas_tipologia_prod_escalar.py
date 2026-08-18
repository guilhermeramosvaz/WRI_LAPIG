"""
histogramas_tipologia_prod_escalar.py
=====================================
Gera dois histogramas a partir do prod_escalar_embrapa_mapbiomas_filtrado.parquet:

  1. Grafico de barras comparativo: Amostras Existentes vs. Amostras Representadas (>= LIMIAR) por Tipologia_
  2. Distribuicao completa do produto escalar (sem filtro) por Tipologia_

Uso:
    python histogramas_tipologia_prod_escalar.py               # default: limiar = 0.95
    python histogramas_tipologia_prod_escalar.py --limiar 0.75
"""

import argparse
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
parser.add_argument("--limiar", type=float, default=0.95,
                    help="Limiar mínimo de similaridade (default: 0.95)")
args = parser.parse_args()

LIMIAR = args.limiar
LIMIAR_INT = int(LIMIAR * 100)

# ----------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------
DIR_BASE = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_BASE / "saida"
DIR_SAIDA_LIMIAR = DIR_SAIDA / str(LIMIAR_INT)
DIR_SAIDA_LIMIAR.mkdir(parents=True, exist_ok=True)

PARQUET = DIR_SAIDA / "prod_escalar_embrapa_mapbiomas_filtrado.parquet"
COLUNA_ID = "TARGET_FID"
COLUNA_TIPOLOGIA = "Tipologia_"

CORES_Tipologia_ = {
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
# Carregar dados
# ----------------------------------------------------------------
print(f"Carregando dados (limiar = {LIMIAR})...")
df = pd.read_parquet(PARQUET)
print(f"  {len(df):,} pares carregados")

# Ordenar tipologias por contagem de amostras totais (decrescente)
amostras_total_raw = df.groupby(COLUNA_TIPOLOGIA)[COLUNA_ID].nunique()
ordem = amostras_total_raw.sort_values(ascending=False).index.tolist()
cores = {tip: CORES_Tipologia_.get(tip, "#cccccc") for tip in ordem}


# ================================================================
# GRAFICO 1: Comparacao de Amostras (Total vs. Match >= LIMIAR)
# ================================================================
print(f"\nGerando histograma 1: comparacao de amostras >= {LIMIAR}...")

# Filtrar pares acima do limiar
df_filtrado = df[df["resultado_multiplicacao"] >= LIMIAR]

# Amostras unicas totais por tipologia
amostras_total = df.groupby(COLUNA_TIPOLOGIA)[COLUNA_ID].nunique().reindex(ordem).fillna(0).astype(int)

# Amostras unicas com pelo menos 1 match >= LIMIAR
amostras_filtradas = df_filtrado.groupby(COLUNA_TIPOLOGIA)[COLUNA_ID].nunique().reindex(ordem).fillna(0).astype(int)

# Porcentagem representada
pct_representada = (amostras_filtradas / amostras_total * 100).round(1)

# Configuracao do grafico de barras agrupadas
fig, ax = plt.subplots(figsize=(12, 7))
fig.subplots_adjust(top=0.82, bottom=0.22)

x = np.arange(len(ordem))
largura = 0.35

# Barras de Amostras Existentes (Total)
barras_totais = ax.bar(x - largura/2, amostras_total.values, largura,
                       label="Amostras Totais (Existentes)",
                       color="#e0e0e0", edgecolor="#888888", linewidth=0.7, zorder=3)

# Barras de Amostras Representadas (Match >= LIMIAR)
barras_filtradas = ax.bar(x + largura/2, amostras_filtradas.values, largura,
                          label=f"Amostras Representadas (Match >= {LIMIAR})",
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
    pct_val = pct_representada.iloc[i]
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
fig.text(0.06, 0.97,
         f"Representatividade das Amostras de Campo no MapBiomas (Limiar >= {LIMIAR})",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
fig.text(0.06, 0.925,
         f"{amostras_filtradas.sum()} de {amostras_total.sum()} amostras de campo ({amostras_filtradas.sum()/amostras_total.sum()*100:.1f}%) possuem pelo menos 1 match",
         fontsize=10.5, color="#666666", ha="left", va="top")

caminho1 = DIR_SAIDA_LIMIAR / "histograma_tipologia_comparacao_amostras.png"
fig.savefig(caminho1, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho1.name}")

# Imprimir tabela no console
print(f"\n  {'Tipologia':<25s} {'Existentes':>12s} {'Com Match':>12s} {'Representado (%)':>18s}")
print("  " + "-" * 71)
for tip in ordem:
    t = amostras_total[tip]
    f = amostras_filtradas[tip]
    p = pct_representada[tip]
    print(f"  {tip:<25s} {t:>12,} {f:>12,} {p:>17.1f}%")


# ================================================================
# GRAFICO 2: Distribuicao completa do produto escalar por Tipologia_
# ================================================================
print(f"\nGerando histograma 2: distribuicao completa por Tipologia_...")

# Amostrar para performance (3.84M e pesado para histograma sobreposto)
np.random.seed(42)
n_amostra = min(300_000, len(df))
df_amostra = df.sample(n=n_amostra, random_state=42)

fig, ax = plt.subplots(figsize=(13, 7))
fig.subplots_adjust(top=0.85, bottom=0.12)

bins = np.arange(0.15, 1.005, 0.01)

for tip in ordem:
    vals = df_amostra.loc[df_amostra[COLUNA_TIPOLOGIA] == tip, "resultado_multiplicacao"].values
    ax.hist(vals, bins=bins, alpha=0.55, color=cores[tip],
            label=f"{tip} (n={len(vals):,})", density=True, edgecolor="none")

# Linha vertical no limiar
ax.axvline(LIMIAR, color="#e74c3c", linestyle="--", linewidth=2,
           label=f"Limiar = {LIMIAR}", zorder=5)

ax.set_xlabel("Produto Escalar (Similaridade Cosseno)", fontsize=11, color="#333333")
ax.set_ylabel("Densidade", fontsize=11, color="#333333")
ax.legend(fontsize=8.5, loc="upper left", framealpha=0.9, ncol=2)

estilo_limpo(ax)
fig.text(0.06, 0.96,
         "Distribuicao do Produto Escalar por Tipologia (sem filtro)",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
fig.text(0.06, 0.92,
         f"Amostra de {n_amostra:,} pares | Todas as 7 tipologias sobrepostas | Limiar = {LIMIAR}",
         fontsize=10.5, color="#666666", ha="left", va="top")

caminho2 = DIR_SAIDA_LIMIAR / "histograma_tipologia_distribuicao_completa.png"
fig.savefig(caminho2, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho2.name}")

print(f"\nConcluido. Graficos salvos em {DIR_SAIDA_LIMIAR}")
