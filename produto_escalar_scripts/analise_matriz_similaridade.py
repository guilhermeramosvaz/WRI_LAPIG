"""
analise_matriz_similaridade.py
==============================
Analisa a matriz de similaridade pivotada (matriz_similaridade_50k.parquet)
para identificar, por pixel MapBiomas, quantos e quais TARGET_FIDs de campo
atingiram similaridade >= LIMIAR.

Uso:
    python analise_matriz_similaridade.py               # default: limiar = 0.75
    python analise_matriz_similaridade.py --limiar 0     # sem limiar
    python analise_matriz_similaridade.py --limiar 0.75

Saidas (na pasta arquivos_saida/<limiar>/):
  - tabela_matches_por_pixel.csv    (cada pixel com contagem de matches)
  - tabela_matches_por_target.csv   (cada TARGET_FID com contagem de pixels pareados)
  - analise_matches_distribuicao.png (grafico de barras)
  - analise_matches_por_target.png   (grafico dos top TARGET_FIDs)
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------------
# Argumentos de linha de comando
# ----------------------------------------------------------------
parser = argparse.ArgumentParser(description="Análise da matriz de similaridade.")
parser.add_argument("--limiar", type=float, default=0.75,
                    help="Limiar mínimo de similaridade (default: 0.75). Use 0 para sem limiar.")
parser.add_argument("--year", default="2025",
                    help="Ano da matriz a analisar (default: 2025).")
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

PARQUET_MATRIZ = DIR_SAIDA / f"matriz_similaridade_50k_{ANO}.parquet"
if not PARQUET_MATRIZ.exists():
    alt_m = DIR_SAIDA / "matriz_similaridade_50k.parquet"
    if alt_m.exists():
        PARQUET_MATRIZ = alt_m
    else:
        alt_m2 = DIR_METRICAS / "matriz_similaridade_50k.parquet"
        if alt_m2.exists():
            PARQUET_MATRIZ = alt_m2

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

# Fallback para cores genéricas quando a tipologia não está no dicionário
PALETA_FALLBACK = ["#a58bfb", "#1abc9c", "#ff5fc1", "#c9a300",
                   "#2ea6ff", "#ff7f6b", "#66c14a", "#ffb347"]


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
# 1. Carregar dados
# ----------------------------------------------------------------
print("=" * 70)
print(f"ANALISE DA MATRIZ DE SIMILARIDADE ({LIMIAR_DISPLAY})")
print("=" * 70)
print(f"\n[1/4] Carregando {PARQUET_MATRIZ.name}...")


df = pd.read_parquet(PARQUET_MATRIZ)
meta_cols = ["id", "class_cvp", "class_2025", "stable_20_"]
target_cols = [c for c in df.columns if c not in meta_cols]

vals = df[target_cols].values.astype(np.float64)
print(f"  Matriz: {vals.shape[0]} pontos MapBiomas x {vals.shape[1]} TARGET_FIDs")
print(f"  Critério de similaridade: {LIMIAR_DISPLAY}")


# ----------------------------------------------------------------
# 2. Calcular matches por pixel (linha)
# ----------------------------------------------------------------
print(f"\n[2/4] Calculando matches {LIMIAR_DISPLAY} por ponto...")

if SEM_LIMIAR:
    # Sem limiar: todos os valores não-NaN contam como match
    high_mask = ~np.isnan(vals)
else:
    high_mask = vals >= LIMIAR

n_matches_per_row = high_mask.sum(axis=1)
max_sim_per_row = np.nanmax(vals, axis=1)
best_target_per_row = np.array(target_cols)[np.nanargmax(vals, axis=1)]

# Construir tabela de pixels
df_pixel = pd.DataFrame({
    "id": df["id"].values,
    "class_cvp": df["class_cvp"].values,
    "class_2025": df["class_2025"].values,
    "stable_20_": df["stable_20_"].values,
    f"n_matches_{LIMIAR_LABEL}": n_matches_per_row,

    "max_similaridade": max_sim_per_row,
    "melhor_TARGET_FID": best_target_per_row
})
df_pixel = df_pixel.sort_values(f"n_matches_{LIMIAR_LABEL}", ascending=False)

n_com_match = (n_matches_per_row > 0).sum()
n_sem_match = (n_matches_per_row == 0).sum()
print(f"  Pontos COM match ({LIMIAR_DISPLAY}): {n_com_match:>5d} ({n_com_match/len(df)*100:.1f}%)")
print(f"  Pontos SEM match:              {n_sem_match:>5d} ({n_sem_match/len(df)*100:.1f}%)")  

# Tabela de distribuicao por faixas
faixas = [
    ("0 (sem match)", 0, 0),

    ("1", 1, 1),
    ("2-3", 2, 3),
    ("4-5", 4, 5),
    ("6-10", 6, 10),
    ("11-20", 11, 20),
    ("21-40", 21, 40),
    ("41-100", 41, 100),
    ("101-200", 101, 200),
    ("201-400", 201, 400),
    ("401+", 401, 99999),
]

print(f"\n  {'Faixa':>18s}  {'Pontos':>7s}  {'%':>7s}  {'Acum.':>7s}")
print("  " + "-" * 45)
cumul = 0
faixa_labels = []
faixa_counts = []
for label, lo, hi in faixas:
    mask = (n_matches_per_row >= lo) & (n_matches_per_row <= hi)
    count = mask.sum()
    if count == 0 and lo > 100:
        continue  # Não exibir faixas vazias nas altas
    pct = count / len(df) * 100
    cumul += pct
    print(f"  {label:>18s}  {count:>7d}  {pct:>6.1f}%  {cumul:>6.1f}%")
    faixa_labels.append(label)
    faixa_counts.append(count)

# Salvar CSV
csv_pixel = DIR_SAIDA_LIMIAR / "tabela_matches_por_pixel.csv"
df_pixel.to_csv(csv_pixel, index=False)

print(f"\n  Tabela salva: {csv_pixel.name}")


# ----------------------------------------------------------------
# 3. Calcular matches por TARGET_FID (coluna)
# ----------------------------------------------------------------
print(f"\n[3/4] Calculando matches por TARGET_FID...")


n_matches_per_col = high_mask.sum(axis=0)
df_target = pd.DataFrame({
    "TARGET_FID": target_cols,
    "n_pontos_pareados": n_matches_per_col,
    "pct_pontos": (n_matches_per_col / len(df) * 100).round(2)
})
df_target = df_target.sort_values("n_pontos_pareados", ascending=False)

n_target_com = (n_matches_per_col > 0).sum()
n_target_sem = (n_matches_per_col == 0).sum()
print(f"  TARGET_FIDs COM pontos pareados: {n_target_com} de {len(target_cols)}")
print(f"  TARGET_FIDs SEM pontos pareados: {n_target_sem} de {len(target_cols)}")

print(f"\n  TOP 15 TARGET_FIDs com mais pontos pareados:")
print(f"  {'TARGET_FID':>12s}  {'Pontos':>7s}  {'%':>7s}")
print("  " + "-" * 30)
for _, row in df_target.head(15).iterrows():
    print(f"  {row['TARGET_FID']:>12s}  {row['n_pontos_pareados']:>7d}  {row['pct_pontos']:>6.1f}%")

csv_target = DIR_SAIDA_LIMIAR / "tabela_matches_por_target.csv"
df_target.to_csv(csv_target, index=False)
print(f"\n  Tabela salva: {csv_target.name}")


# ----------------------------------------------------------------
# 4. Graficos
# ----------------------------------------------------------------
print(f"\n[4/4] Gerando graficos...")

# --- Grafico 1: Distribuicao de matches por pixel ---
fig, ax = plt.subplots(figsize=(11, 6))
fig.subplots_adjust(top=0.82, bottom=0.15)

cores = PALETA_FALLBACK[:len(faixa_labels)]
if len(cores) < len(faixa_labels):
    cores = cores * ((len(faixa_labels) // len(cores)) + 1)
    cores = cores[:len(faixa_labels)]

barras = ax.bar(range(len(faixa_labels)), faixa_counts, color=cores,
                width=0.7, zorder=3, edgecolor="white", linewidth=0.5)

for barra, valor in zip(barras, faixa_counts):
    pct = valor / len(df) * 100
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + max(faixa_counts) * 0.02,
            f"{valor}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=9.5,
            color="#222222", fontweight="bold")

ax.set_xticks(range(len(faixa_labels)))
ax.set_xticklabels(faixa_labels, fontsize=10, rotation=30, ha="right")
ax.set_ylabel("N. de Pontos MapBiomas", fontsize=11, color="#333333")
ax.set_xlabel(f"Quantidade de TARGET_FIDs com similaridade {LIMIAR_DISPLAY}", fontsize=11, color="#333333")
ax.set_ylim(0, max(faixa_counts) * 1.18)

estilo_limpo(ax)
fig.text(0.06, 0.97,
         f"Matriz de Similaridade: Matches por Ponto ({LIMIAR_DISPLAY})",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
fig.text(0.06, 0.925,
         f"{n_com_match:,} de {len(df):,} pontos tem pelo menos 1 match com amostra de campo",
         fontsize=10.5, color="#666666", ha="left", va="top")

caminho1 = DIR_SAIDA_LIMIAR / "analise_matches_distribuicao.png"
fig.savefig(caminho1, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho1.name}")

# --- Grafico 2: Top TARGET_FIDs com mais matches ---
top_n = 25
df_top = df_target.head(top_n).copy()
df_top = df_top.iloc[::-1]  # Inverter para barh (maior em cima)

# Mapear cada TARGET_FID para sua Tipologia_
PARQUET_EMBRAPA = DIR_ARQUIVOS_BASE / "embeddings_embrapa_year_colet.parquet"
if PARQUET_EMBRAPA.exists():
    df_emb = pd.read_parquet(PARQUET_EMBRAPA)[["TARGET_FID", "Tipologia_"]].drop_duplicates("TARGET_FID")
    df_emb["TARGET_FID"] = df_emb["TARGET_FID"].astype(str)
    fid_to_tip = dict(zip(df_emb["TARGET_FID"], df_emb["Tipologia_"]))
else:
    fid_to_tip = {}

classes_top = [fid_to_tip.get(str(fid), "Desconhecido") for fid in df_top["TARGET_FID"].values]
cores_bar = [CORES_TIPOLOGIA.get(c, "#cccccc") for c in classes_top]

fig, ax = plt.subplots(figsize=(12, 9))
fig.subplots_adjust(top=0.88, left=0.15, right=0.82)

barras = ax.barh(range(len(df_top)), df_top["n_pontos_pareados"].values,
                 color=cores_bar, height=0.7, zorder=3, edgecolor="white", linewidth=0.5)

for barra, (_, row) in zip(barras, df_top.iterrows()):
    ax.text(barra.get_width() + max(df_top["n_pontos_pareados"]) * 0.01,
            barra.get_y() + barra.get_height() / 2,
            f"{int(row['n_pontos_pareados'])} ({row['pct_pontos']:.1f}%)",
            ha="left", va="center", fontsize=9, color="#333333")

ax.set_yticks(range(len(df_top)))
ax.set_yticklabels([f"FID {fid}" for fid in df_top["TARGET_FID"].values], fontsize=9.5)
ax.set_xlabel(f"N. de Pontos MapBiomas pareados ({LIMIAR_DISPLAY})", fontsize=11, color="#333333")
ax.set_xlim(0, max(df_top["n_pontos_pareados"]) * 1.25)

estilo_limpo(ax)
ax.grid(axis="y", visible=False)
ax.grid(axis="x", color="#e6e6e6", linewidth=0.9, zorder=0)

# Legenda por classe
from matplotlib.patches import Patch
classes_presentes = list(dict.fromkeys(classes_top))
legend_handles = [Patch(facecolor=CORES_TIPOLOGIA.get(c, "#cccccc"), edgecolor="#555555",
                        label=c) for c in sorted(classes_presentes)]
ax.legend(handles=legend_handles, title="Classe (Tipologia_)",
          fontsize=9, title_fontsize=10, loc="lower right",
          framealpha=0.9, edgecolor="#cccccc")

fig.text(0.06, 0.97,
         f"Top {top_n} Amostras de Campo com Mais Pontos Pareados ({LIMIAR_DISPLAY})",
         fontsize=14, fontweight="bold", color="#222222", ha="left", va="top")
fig.text(0.06, 0.935,
         "Quais amostras Embrapa melhor representam os pontos MapBiomas",
         fontsize=10.5, color="#666666", ha="left", va="top")

caminho2 = DIR_SAIDA_LIMIAR / "analise_matches_por_target.png"
fig.savefig(caminho2, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho2.name}")


# ----------------------------------------------------------------
# Resumo
# ----------------------------------------------------------------
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"\n  Critério utilizado: {LIMIAR_DISPLAY}")
print(f"  Pasta de saida:  {DIR_SAIDA_LIMIAR}")
print(f"  Pontos com match:  {n_com_match:,} / {len(df):,} ({n_com_match/len(df)*100:.1f}%)")
print(f"  Pontos sem match:  {n_sem_match:,} / {len(df):,} ({n_sem_match/len(df)*100:.1f}%)")
print(f"  TARGET_FIDs representados: {n_target_com} / {len(target_cols)}")
print(f"\n  Arquivos gerados:")
print(f"    * {csv_pixel.name}")
print(f"    * {csv_target.name}")
print(f"    * {caminho1.name}")
print(f"    * {caminho2.name}")
print("\nConcluido.\n")
