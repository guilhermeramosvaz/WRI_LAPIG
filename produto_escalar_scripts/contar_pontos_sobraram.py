"""
contar_pontos_sobraram.py
=========================
Conta quantos matches (valores não-nulos) existem por ponto MapBiomas
no parquet filtrado, e gera um histograma com intervalos configuráveis.

Uso:
    python contar_pontos_sobraram.py               # default: limiar = 0.75
    python contar_pontos_sobraram.py --limiar 0     # sem limiar
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
parser = argparse.ArgumentParser(description="Conta matches por pixel no parquet filtrado.")
parser.add_argument("--limiar", type=float, default=0.75,
                    help="Limiar usado na filtragem (default: 0.75). Use 0 para sem limiar.")
parser.add_argument("--bin-step", type=int, default=None,
                    help="Tamanho do intervalo do histograma (ex: 5 ou 50)")
parser.add_argument("--year", default="2025",
                    help="Ano a processar (default: 2025).")
args = parser.parse_args()

LIMIAR = args.limiar
ANO = args.year
SEM_LIMIAR = (LIMIAR <= 0)
LIMIAR_LABEL = "sem_limiar" if SEM_LIMIAR else str(int(LIMIAR * 100))
LIMIAR_DISPLAY = "sem limiar (todos)" if SEM_LIMIAR else f">= {LIMIAR}"

# Se bin-step não for informado, usa 50 para sem_limiar e limiar baixo, 5 para limiares altos
if args.bin_step is not None:
    STEP = args.bin_step
else:
    STEP = 50 if (SEM_LIMIAR or LIMIAR <= 0.75) else 5

# ----------------------------------------------------------------
# Caminhos
# ----------------------------------------------------------------
DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_SAIDA_LIMIAR = DIR_SAIDA / LIMIAR_LABEL
DIR_SAIDA_LIMIAR.mkdir(parents=True, exist_ok=True)

caminho_parquet = DIR_SAIDA_LIMIAR / f"matriz_similaridade_50k_mais_{LIMIAR_LABEL}_{ANO}.parquet"
if not caminho_parquet.exists():
    alt_p = DIR_SAIDA_LIMIAR / f"matriz_similaridade_50k_mais_{LIMIAR_LABEL}.parquet"
    if alt_p.exists():
        caminho_parquet = alt_p

# ----------------------------------------------------------------
# 1. Carregar o arquivo Parquet
# ----------------------------------------------------------------
print(f"Carregando arquivo filtrado ({LIMIAR_DISPLAY})...")
print(f"  Arquivo: {caminho_parquet}")
df = pd.read_parquet(caminho_parquet)

# 2. Identificar colunas de identificação e metadados
colunas_protegidas = ['id', 'class_cvp', 'class_2025', 'stable_20_']
colunas_pontos = [col for col in df.columns if col not in colunas_protegidas]

# 3. Contar quantos valores não são nulos (notna) por linha (n_matches)
df['n_matches'] = df[colunas_pontos].notna().sum(axis=1)

# 4. Exibir as primeiras linhas com o resultado
print("\nExemplo das primeiras linhas com a contagem:")
print(df[['id', 'class_cvp', 'class_2025', 'stable_20_', 'n_matches']].head(10))

# 5. Resumo estatístico
print(f"\nResumo estatistico de n_matches ({LIMIAR_DISPLAY}) por ponto MapBiomas:")
print(df['n_matches'].describe())

# 6. Salvar tabela de resumo em CSV
caminho_resumo = DIR_SAIDA_LIMIAR / 'resumo_contagem_pontos_por_mapbiomas.csv'
df[['id', 'class_cvp', 'class_2025', 'stable_20_', 'n_matches']].to_csv(caminho_resumo, index=False)
print(f"\nResumo salvo em: {caminho_resumo.name}")

# ---------------------------------------------------------------------------
# 7. GERAR HISTOGRAMA (BINS DE STEP EM STEP)
# ---------------------------------------------------------------------------
print(f"\nGerando histograma com intervalos de {STEP} em {STEP}...")

max_matches = int(df['n_matches'].max())
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
            (bins_out[i] + bins_out[i+1]) / 2,
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
fig.text(0.06, 0.915, f"Total de {n_pixels:,} pontos MapBiomas | Similaridade {LIMIAR_DISPLAY} | Bins de tamanho {STEP}",
         fontsize=10.5, color="#666666", ha="left", va="top")

ax.set_xlabel("Número de Matches por Ponto (n_matches)", fontsize=11, color="#333333")
ax.set_ylabel("Quantidade de Pontos MapBiomas", fontsize=11, color="#333333")

# Ajustar xticks para não sobrecarregar
n_ticks = len(list(range(0, max_matches + STEP + 1, STEP)))
tick_step = max(1, n_ticks // 20)  # No máximo ~20 ticks
tick_vals = list(range(0, max_matches + STEP + 1, STEP * tick_step))
ax.set_xticks(tick_vals)
plt.xticks(rotation=45)

plt.tight_layout()
fig.subplots_adjust(top=0.85)

caminho_grafico = DIR_SAIDA_LIMIAR / f"histograma_n_matches_{STEP}em{STEP}.png"
plt.savefig(caminho_grafico, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Histograma salvo em: {caminho_grafico.name}")
print(f"Pasta de saida: {DIR_SAIDA_LIMIAR}")
