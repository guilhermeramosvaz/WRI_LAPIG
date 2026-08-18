"""
analise_matriz_similaridade.py
==============================
Analisa a tabela pivotada top-3 (tabela_top3_pivotada.parquet) gerada a
partir dos produtos escalares entre pontos MapBiomas e amostras Embrapa.

Para cada ponto MapBiomas (id_alvo) temos os 3 TARGET_FIDs com maior
produto escalar, a class_embrapa (= tipologia do top-1) e o campo md3
(concordancia entre os 3 tops).

Graficos gerados (salvos em saida/):
  1. Distribuicao de class_embrapa por Tipologia_ (quantos pontos MapBiomas
     foram classificados em cada classe).
  2. Distribuicao do campo md3 (concordancia entre os 3 tops).
  3. Top 25 TARGET_FIDs que mais aparecem como melhor match (target_fid_1).
  4. Boxplots da composicao de cobertura (capim, lenhosa_co, ruderal, solo)
     do top-1 por class_embrapa.
  5. Boxplot de altitude do top-1 por class_embrapa.

Uso:
    python analise_matriz_similaridade.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------
DIR_BASE = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_BASE / "saida"
DIR_SAIDA.mkdir(parents=True, exist_ok=True)

PARQUET = DIR_BASE / "output" / "tabela_top3_pivotada.parquet"

CORES_TIPOLOGIA = {
    "PASTO PRODUTIVO": "#faea40",
    "PASTO COM ERVAS": "#d8ff6c",
    "REG NATURAL": "#0e5f0e",
    "INTERMEDIARIO": "#f4b346",
    "DEG BIOLOGICA": "#813209",
    "PASTO COM LENHOSAS": "#66c600",
    "MISCELANEA": "#ec2b10",
}

VALORES_EXCLUIR = ["nao se aplica", "não se aplica", "NA", "nan"]


def estilo_limpo(ax):
    ax.set_facecolor("white")
    ax.figure.set_facecolor("white")
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(axis="both", length=0, labelsize=10, colors="#333333")


def titulo_subtitulo(fig, titulo, subtitulo):
    fig.text(0.06, 0.97, titulo, fontsize=15, fontweight="bold",
             color="#222222", ha="left", va="top")
    fig.text(0.06, 0.925, subtitulo, fontsize=10.5, color="#666666",
             ha="left", va="top")


# ----------------------------------------------------------------
# 1. Carregar dados
# ----------------------------------------------------------------
print("=" * 70)
print("ANALISE DA TABELA TOP-3 PIVOTADA")
print("=" * 70)
print(f"\n[1/6] Carregando {PARQUET.name}...")

df = pd.read_parquet(PARQUET)

# Filtrar valores excluidos de class_embrapa
df = df[~df["class_embrapa"].isin(VALORES_EXCLUIR)].copy()

print(f"  {len(df):,} pontos MapBiomas carregados")

# Definir ordem e cores por frequencia
contagem_classes = df["class_embrapa"].value_counts()
ordem = contagem_classes.index.tolist()
cores = {tip: CORES_TIPOLOGIA.get(tip, "#cccccc") for tip in ordem}


# ----------------------------------------------------------------
# 2a. Grafico 1: Pontos MapBiomas por class_embrapa (Simples)
# ----------------------------------------------------------------
print("\n[2a/6] Gerando grafico 1: pontos MapBiomas por class_embrapa (Simples)...")

fig, ax = plt.subplots(figsize=(11, 7))
fig.subplots_adjust(top=0.82, bottom=0.22)

barras = ax.bar(range(len(ordem)), contagem_classes.values,
                color=[cores[t] for t in ordem],
                width=0.65, zorder=3, edgecolor="white", linewidth=0.5)

for barra, valor in zip(barras, contagem_classes.values):
    pct = valor / len(df) * 100
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + contagem_classes.max() * 0.015,
            f"{valor:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=9.5,
            color="#222222", fontweight="bold")

ax.set_xticks(range(len(ordem)))
ax.set_xticklabels(ordem, rotation=30, ha="right", fontsize=10)
ax.set_ylabel("Nº de Pontos MapBiomas", fontsize=11, color="#333333")
ax.set_xlabel("Classe Embrapa (Tipologia do Top-1)", fontsize=11, color="#333333")
ax.set_ylim(0, contagem_classes.max() * 1.20)

estilo_limpo(ax)
titulo_subtitulo(fig,
    "Classificação dos Pontos MapBiomas via Similaridade (Top-1)",
    f"{len(df):,} pontos classificados pelo TARGET_FID com maior produto escalar")

caminho1 = DIR_SAIDA / "pontos_por_class_embrapa.png"
fig.savefig(caminho1, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho1.name}")


# ----------------------------------------------------------------
# 2b. Grafico 1b: Pontos MapBiomas por class_embrapa com composicao md3 (Duplo Normalizado)
# ----------------------------------------------------------------
print("\n[2b/6] Gerando grafico 1b: pontos MapBiomas por class_embrapa com composicao md3 (normalizado)...")

# Calcular as porcentagens de md3 por classe (normalizado para 100%)
pct_md3_1 = []
pct_md3_2 = []
pct_md3_3 = []
for t in ordem:
    sub = df[df["class_embrapa"] == t]
    tot = len(sub)
    if tot > 0:
        pct_md3_1.append((sub["md3"] == 1).sum() / tot * 100)
        pct_md3_2.append((sub["md3"] == 2).sum() / tot * 100)
        pct_md3_3.append((sub["md3"] == 3).sum() / tot * 100)
    else:
        pct_md3_1.append(0)
        pct_md3_2.append(0)
        pct_md3_3.append(0)

pct_md3_1 = np.array(pct_md3_1)
pct_md3_2 = np.array(pct_md3_2)
pct_md3_3 = np.array(pct_md3_3)

fig, ax = plt.subplots(figsize=(13, 8))
fig.subplots_adjust(top=0.82, bottom=0.22)

x = np.arange(len(ordem))
width = 0.35

# Barra principal (Identificador da classe - 100% de altura)
barras_total = ax.bar(x - width/2, [100] * len(ordem),
                      color=[cores[t] for t in ordem],
                      width=width, zorder=3, edgecolor="white", linewidth=0.5,
                      label="Identificador da Classe")

# Barra ao lado em 3 tons de cinza normalizada para 100% (md3 = 1, 2, 3)
barras_md3_1 = ax.bar(x + width/2, pct_md3_1, width=width, color="#d9d9d9",
                       edgecolor="white", linewidth=0.5, zorder=3, label="md3 = 1 (Nenhum concorda)")
barras_md3_2 = ax.bar(x + width/2, pct_md3_2, bottom=pct_md3_1, width=width, color="#969696",
                       edgecolor="white", linewidth=0.5, zorder=3, label="md3 = 2 (1 de 2 concorda)")
barras_md3_3 = ax.bar(x + width/2, pct_md3_3, bottom=pct_md3_1 + pct_md3_2, width=width, color="#525252",
                       edgecolor="white", linewidth=0.5, zorder=3, label="md3 = 3 (Todos concordam)")

# Rotular a barra de totais com a quantidade absoluta e porcentagem geral no topo (acima de 100%)
for barra, valor in zip(barras_total, contagem_classes.values):
    pct = valor / len(df) * 100
    ax.text(barra.get_x() + barra.get_width() / 2,
            101.5,
            f"{valor:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=8.5,
            color="#222222", fontweight="bold")

# Rotular os segmentos de md3 na barra empilhada cinza com a porcentagem interna
for i in range(len(ordem)):
    tot = contagem_classes.values[i]
    if tot == 0:
        continue
    
    # md3 = 1
    p1 = pct_md3_1[i]
    if p1 > 4.0:
        ax.text(x[i] + width/2, p1 / 2, f"{p1:.0f}%",
                ha="center", va="center", fontsize=8.5, color="#222222", fontweight="bold")
        
    # md3 = 2
    p2 = pct_md3_2[i]
    if p2 > 4.0:
        ax.text(x[i] + width/2, p1 + p2 / 2, f"{p2:.0f}%",
                ha="center", va="center", fontsize=8.5, color="#ffffff", fontweight="bold")
        
    # md3 = 3
    p3 = pct_md3_3[i]
    if p3 > 4.0:
        ax.text(x[i] + width/2, p1 + p2 + p3 / 2, f"{p3:.0f}%",
                ha="center", va="center", fontsize=8.5, color="#ffffff", fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(ordem, rotation=30, ha="right", fontsize=10)
ax.set_ylabel("Proporção de Concordância (%)", fontsize=11, color="#333333")
ax.set_xlabel("Classe Embrapa (Tipologia do Top-1)", fontsize=11, color="#333333")
ax.set_ylim(0, 100)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.08), ncol=4, fontsize=8.5, framealpha=0.9, edgecolor="#cccccc")

estilo_limpo(ax)
titulo_subtitulo(fig,
    "Composição de Concordância (md3) por Classe",
    f"{len(df):,} pontos classificados. Barra colorida indica a classe (rótulo = amostras totais); Barra cinza = proporção interna de md3")

caminho1b = DIR_SAIDA / "pontos_por_class_embrapa_md3.png"
fig.savefig(caminho1b, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho1b.name}")

# Tabela no console
print(f"\n  {'Classe':<25s} {'Pontos':>8s} {'%':>7s}")
print("  " + "-" * 42)
for tip in ordem:
    n = contagem_classes[tip]
    print(f"  {tip:<25s} {n:>8,} {n/len(df)*100:>6.1f}%")


# ----------------------------------------------------------------
# 2c. Grafico 1c: Distribuicao do Produto Escalar Maximo (Top-1)
# ----------------------------------------------------------------
print("\n[2c/6] Gerando grafico 1c: distribuicao do produto escalar maximo...")

fig, ax = plt.subplots(figsize=(9, 6))
fig.subplots_adjust(top=0.82, bottom=0.18)

# Histograma do produto escalar_1
ax.hist(df["prod_escalar_1"], bins=40, color="#2ea6ff", edgecolor="white", linewidth=0.5, zorder=3)

ax.set_ylabel("Nº de Pontos MapBiomas", fontsize=11, color="#333333")
ax.set_xlabel("Maior Produto Escalar (Similaridade do Top-1)", fontsize=11, color="#333333")

estilo_limpo(ax)
titulo_subtitulo(fig,
    "Distribuição da Maior Similaridade por Ponto (Top-1)",
    f"Produto escalar máximo alcançado por cada um dos {len(df):,} pontos MapBiomas")

caminho1c = DIR_SAIDA / "distribuicao_prod_escalar_maximo.png"
fig.savefig(caminho1c, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho1c.name}")


# ----------------------------------------------------------------
# 3. Grafico 2: Distribuicao do md3 (concordancia)
# ----------------------------------------------------------------
print("\n[3/6] Gerando grafico 2: distribuicao do md3...")

md3_counts = df["md3"].value_counts().sort_index()
md3_labels = {
    1: "md3 = 1\n(nenhum concorda)",
    2: "md3 = 2\n(1 de 2 concorda)",
    3: "md3 = 3\n(todos concordam)"
}
md3_cores = ["#ff7f6b", "#c9a300", "#1abc9c"]

fig, ax = plt.subplots(figsize=(9, 6))
fig.subplots_adjust(top=0.82, bottom=0.18)

labels = [md3_labels.get(v, str(v)) for v in md3_counts.index]
barras = ax.bar(range(len(md3_counts)), md3_counts.values,
                color=md3_cores[:len(md3_counts)],
                width=0.55, zorder=3, edgecolor="white", linewidth=0.5)

for barra, valor in zip(barras, md3_counts.values):
    pct = valor / len(df) * 100
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + md3_counts.max() * 0.02,
            f"{valor:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=10.5,
            color="#222222", fontweight="bold")

ax.set_xticks(range(len(md3_counts)))
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("Nº de Pontos MapBiomas", fontsize=11, color="#333333")
ax.set_ylim(0, md3_counts.max() * 1.22)

estilo_limpo(ax)
titulo_subtitulo(fig,
    "Concordância entre os 3 Melhores Matches (md3)",
    "Quantos dos 3 TARGET_FIDs mais similares atribuem a mesma classe ao ponto")

caminho2 = DIR_SAIDA / "distribuicao_md3.png"
fig.savefig(caminho2, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho2.name}")

# Console
for v in md3_counts.index:
    n = md3_counts[v]
    print(f"  md3 = {v}: {n:>7,} pontos ({n/len(df)*100:.1f}%)")


# ----------------------------------------------------------------
# 4. Grafico 3: Top 25 TARGET_FIDs mais frequentes como top-1
# ----------------------------------------------------------------
print("\n[4/6] Gerando grafico 3: top 25 TARGET_FIDs mais frequentes...")

top_targets = df["target_fid_1"].value_counts().head(25)
df_top = top_targets.iloc[::-1]  # Inverter para barh (maior em cima)

# Mapear cada TARGET_FID para sua classe (tipologia_1)
fid_to_class = df.drop_duplicates("target_fid_1").set_index("target_fid_1")["tipologia_1"]
classes_top = [fid_to_class.get(fid, "?") for fid in df_top.index]
cores_bar = [cores.get(c, "#cccccc") for c in classes_top]

fig, ax = plt.subplots(figsize=(12, 9))
fig.subplots_adjust(top=0.88, left=0.15, right=0.82)

barras = ax.barh(range(len(df_top)), df_top.values,
                 color=cores_bar, height=0.7, zorder=3,
                 edgecolor="white", linewidth=0.5)

for barra, valor in zip(barras, df_top.values):
    pct = valor / len(df) * 100
    ax.text(barra.get_width() + df_top.max() * 0.01,
            barra.get_y() + barra.get_height() / 2,
            f"{valor:,} ({pct:.1f}%)",
            ha="left", va="center", fontsize=9, color="#333333")

ax.set_yticks(range(len(df_top)))
ax.set_yticklabels([f"FID {int(fid)}" for fid in df_top.index], fontsize=9.5)
ax.set_xlabel("Nº de Pontos MapBiomas classificados", fontsize=11, color="#333333")
ax.set_xlim(0, df_top.max() * 1.25)

estilo_limpo(ax)
ax.grid(axis="y", visible=False)
ax.grid(axis="x", color="#e6e6e6", linewidth=0.9, zorder=0)

# Legenda por classe
from matplotlib.patches import Patch
classes_presentes = list(dict.fromkeys(classes_top))  # ordem de aparição, sem duplicatas
legend_handles = [Patch(facecolor=cores.get(c, "#ccc"), edgecolor="#555",
                        label=c) for c in sorted(classes_presentes)]
ax.legend(handles=legend_handles, title="Classe (Tipologia_)",
          fontsize=9, title_fontsize=10, loc="lower right",
          framealpha=0.9, edgecolor="#cccccc")

titulo_subtitulo(fig,
    "Top 25 Amostras Embrapa Mais Representativas (Top-1)",
    "TARGET_FIDs que mais vezes foram o melhor match para pontos MapBiomas")

caminho3 = DIR_SAIDA / "top25_target_fids.png"
fig.savefig(caminho3, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho3.name}")


# ----------------------------------------------------------------
# 5. Grafico 4: Composicao de cobertura (top-1) por class_embrapa
# ----------------------------------------------------------------
print("\n[5/6] Gerando grafico 4: composicao de cobertura por class_embrapa...")

variaveis = ["capim_1", "lenhosa_co_1", "ruderal_1", "solo_1"]
var_labels = ["Capim", "Lenhosa", "Ruderal", "Solo"]

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.subplots_adjust(top=0.88, hspace=0.55, wspace=0.25, bottom=0.12)

for ax, var, var_label in zip(axes.flat, variaveis, var_labels):
    dados = [df.loc[df["class_embrapa"] == cat, var].dropna().values for cat in ordem]
    bp = ax.boxplot(dados, patch_artist=True, showfliers=False,
                    medianprops=dict(color="#333333", linewidth=1.5))
    for patch, cat in zip(bp["boxes"], ordem):
        patch.set_facecolor(cores[cat])
        patch.set_alpha(0.75)
        patch.set_edgecolor("#555555")
    ax.set_xticks(range(1, len(ordem) + 1))
    ax.set_xticklabels(ordem, rotation=35, ha="right", fontsize=8.5)
    ax.set_title(var_label, fontsize=11, fontweight="bold", color="#333333")
    estilo_limpo(ax)

titulo_subtitulo(fig,
    "Composição de Cobertura do Melhor Match por Classe",
    "Distribuição (%) de capim, lenhosa, ruderal e solo do TARGET_FID top-1")

caminho4 = DIR_SAIDA / "composicao_por_class_embrapa.png"
fig.savefig(caminho4, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho4.name}")


# ----------------------------------------------------------------
# 6. Grafico 5: Altitude (top-1) por class_embrapa
# ----------------------------------------------------------------
print("\n[6/6] Gerando grafico 5: altitude por class_embrapa...")

dados = [df.loc[df["class_embrapa"] == cat, "altitude_1"].dropna().values for cat in ordem]

fig, ax = plt.subplots(figsize=(9, 6))
fig.subplots_adjust(top=0.85, bottom=0.28)

bp = ax.boxplot(dados, patch_artist=True, showfliers=False,
                medianprops=dict(color="#333333", linewidth=1.5))
for patch, cat in zip(bp["boxes"], ordem):
    patch.set_facecolor(cores[cat])
    patch.set_alpha(0.75)
    patch.set_edgecolor("#555555")

ax.set_xticks(range(1, len(ordem) + 1))
ax.set_xticklabels(ordem, rotation=30, ha="right")
ax.set_ylabel("Altitude (m)", fontsize=11, color="#333333")

estilo_limpo(ax)
titulo_subtitulo(fig,
    "Altitude do Melhor Match por Classe",
    "Distribuição da altitude (m) do TARGET_FID top-1 em cada class_embrapa")

caminho5 = DIR_SAIDA / "altitude_por_class_embrapa.png"
fig.savefig(caminho5, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  [ok] {caminho5.name}")


# ----------------------------------------------------------------
# Resumo
# ----------------------------------------------------------------
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"\n  Pontos MapBiomas analisados: {len(df):,}")
print(f"  Classes (class_embrapa):     {len(ordem)}")
print(f"  md3 = 3 (todos concordam):   {md3_counts.get(3, 0):,} ({md3_counts.get(3, 0)/len(df)*100:.1f}%)")
print(f"  md3 = 2 (1 concorda):        {md3_counts.get(2, 0):,} ({md3_counts.get(2, 0)/len(df)*100:.1f}%)")
print(f"  md3 = 1 (nenhum concorda):   {md3_counts.get(1, 0):,} ({md3_counts.get(1, 0)/len(df)*100:.1f}%)")
print(f"\n  Arquivos gerados em {DIR_SAIDA}:")
print(f"    * {caminho1.name}")
print(f"    * {caminho1b.name}")
print(f"    * {caminho1c.name}")
print(f"    * {caminho2.name}")
print(f"    * {caminho3.name}")
print(f"    * {caminho4.name}")
print(f"    * {caminho5.name}")
print("\nConcluido.\n")
