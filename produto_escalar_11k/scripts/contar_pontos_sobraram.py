"""
contar_pontos_sobraram.py
=========================
Conta quantos matches (valores não-nulos) existem por pixel MapBiomas
no CSV filtrado, e gera um histograma com intervalos configuráveis (ex: 5 em 5 ou 50 em 50).

Uso:
    python contar_pontos_sobraram.py               # default: limiar = 0.95 (bin_step = 5)
    python contar_pontos_sobraram.py --limiar 0.75 # default: limiar = 0.75 (bin_step = 50)
    python contar_pontos_sobraram.py --limiar 0.75 --bin-step 50
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
parser = argparse.ArgumentParser(description="Conta matches por pixel no CSV filtrado.")
parser.add_argument("--limiar", type=float, default=0.95,
                    help="Limiar usado na filtragem (default: 0.95)")
parser.add_argument("--bin-step", type=int, default=None,
                    help="Tamanho do intervalo do histograma (ex: 5 ou 50)")
args = parser.parse_args()

LIMIAR = args.limiar
LIMIAR_INT = int(LIMIAR * 100)

# Se bin-step não for informado, usa 50 para limiares <= 0.75 e 5 para limiares maiores
if args.bin_step is not None:
    STEP = args.bin_step
else:
    STEP = 50 if LIMIAR <= 0.75 else 5

# ----------------------------------------------------------------
# Caminhos (relativos ao projeto)
# ----------------------------------------------------------------
DIR_BASE = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_BASE / "saida"
DIR_SAIDA_LIMIAR = DIR_SAIDA / str(LIMIAR_INT)
DIR_SAIDA_LIMIAR.mkdir(parents=True, exist_ok=True)

caminho_csv = DIR_SAIDA_LIMIAR / f"matriz_similaridade_2024_mais_{LIMIAR_INT}.csv"

# ----------------------------------------------------------------
# 1. Carregar o arquivo CSV
# ----------------------------------------------------------------
print(f"Carregando arquivo CSV filtrado (limiar >= {LIMIAR})...")
print(f"  Arquivo: {caminho_csv}")
df = pd.read_csv(caminho_csv)

# 2. Identificar colunas de identificação e coordenadas
colunas_protegidas = ['id_mapbiomas', 'latitude_alvo', 'longitude_alvo']
colunas_pontos = [col for col in df.columns if col not in colunas_protegidas]

# 3. Contar quantos valores não são nulos (notna) por linha (n_matches)
df['n_matches'] = df[colunas_pontos].notna().sum(axis=1)

# 4. Exibir as primeiras linhas com o resultado
print("\nExemplo das primeiras linhas com a contagem:")
print(df[['id_mapbiomas', 'latitude_alvo', 'longitude_alvo', 'n_matches']].head(10))

# 5. Resumo estatístico
print(f"\nResumo estatistico de n_matches (>= {LIMIAR}) por ponto MapBiomas:")
print(df['n_matches'].describe())

# 6. Salvar tabela de resumo em CSV
caminho_resumo = DIR_SAIDA_LIMIAR / 'resumo_contagem_pontos_por_mapbiomas.csv'
df[['id_mapbiomas', 'latitude_alvo', 'longitude_alvo', 'n_matches']].to_csv(caminho_resumo, index=False)
print(f"\nResumo salvo em: {caminho_resumo.name}")

# ---------------------------------------------------------------------------
# 7. GERAR HISTOGRAMA (BINS DE STEP EM STEP)
# ---------------------------------------------------------------------------
print(f"\nGerando histograma com intervalos de {STEP} em {STEP}...")

max_matches = df['n_matches'].max()
bins = range(0, max_matches + STEP + 1, STEP)

fig, ax = plt.subplots(figsize=(12, 6))

# Estilo visual clean
ax.set_facecolor("white")
fig.set_facecolor("white")
ax.grid(axis="y", color="#e6e6e6", linewidth=0.9, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#cccccc")
ax.tick_params(axis="both", length=0, labelsize=10, colors="#333333")

# Plotar o histograma
n, bins_out, patches = ax.hist(
    df['n_matches'],
    bins=bins,
    color="#1abc9c",
    edgecolor="white",
    linewidth=1.2,
    zorder=3
)

# Colorir as barras com um gradiente suave
for i, patch in enumerate(patches):
    if i == 0:
        patch.set_facecolor("#ff7f6b")  # Destacar bin inicial
    else:
        patch.set_facecolor("#2ea6ff")

# Adicionar o valor da contagem acima das barras principais
for i in range(len(n)):
    if n[i] > 0:
        ax.text(
            (bins[i] + bins[i+1]) / 2,
            n[i] + max(n) * 0.015,
            f"{int(n[i])}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#222222",
            fontweight="bold"
        )

# Títulos e rótulos
n_pixels = len(df)
fig.text(0.06, 0.96, f"Distribuição de n_matches por Ponto MapBiomas (Intervalos de {STEP} em {STEP})",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
fig.text(0.06, 0.915, f"Total de {n_pixels:,} pixels MapBiomas | Limiar de similaridade >= {LIMIAR} | Bins de tamanho {STEP}",
         fontsize=10.5, color="#666666", ha="left", va="top")

ax.set_xlabel("Número de Matches por Pixel (n_matches)", fontsize=11, color="#333333")
ax.set_ylabel("Quantidade de Pixels MapBiomas", fontsize=11, color="#333333")
ax.set_xticks(range(0, max_matches + STEP + 1, STEP))
plt.xticks(rotation=45)

plt.tight_layout()
fig.subplots_adjust(top=0.85)

caminho_grafico = DIR_SAIDA_LIMIAR / f"histograma_n_matches_{STEP}em{STEP}.png"
plt.savefig(caminho_grafico, dpi=200, bbox_inches="tight")

# Se STEP != 5, também mantemos/atualizamos histograma_n_matches_5em5.png para compatibilidade retroativa se necessário
caminho_legado = DIR_SAIDA_LIMIAR / "histograma_n_matches_5em5.png"
plt.savefig(caminho_legado, dpi=200, bbox_inches="tight")

plt.close(fig)

print(f"Histograma salvo em: {caminho_grafico.name}")
print(f"Pasta de saida: {DIR_SAIDA_LIMIAR}")
