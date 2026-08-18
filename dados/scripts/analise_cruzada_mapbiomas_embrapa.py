"""
analise_cruzada_mapbiomas_embrapa.py
====================================
Gera gráficos avançados cruzando dados do MapBiomas (CVP, 2025, Stable 20)
com os resultados da classificação Embrapa (Top-3 + MD3).

Gráficos gerados:
1. Diagrama de Sankey (Fluxo de Transição: Stable 20 -> Class 2025 -> Embrapa)
2. Gráfico de Barras Empilhadas 100% (Vigor vs Embrapa)
3. Boxplots Múltiplos Biofísicos (Vigor vs Frações de Cobertura)
4. Gráfico de Rosca Agrupado (Embrapa vs MD3)

Uso:
    python analise_cruzada_mapbiomas_embrapa.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import argparse
parser = argparse.ArgumentParser(description="Análise cruzada MapBiomas vs Embrapa.")
parser.add_argument("--year", default="2025", help="Ano a analisar (default: 2025).")
args = parser.parse_args()
ANO = args.year

# ----------------------------------------------------------------
# Caminhos
# ----------------------------------------------------------------
DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_SAIDA.mkdir(parents=True, exist_ok=True)

PARQUET_TOP3 = DIR_SAIDA / f"tabela_top3_pivotada_50k_{ANO}.parquet"
if not PARQUET_TOP3.exists():
    alt_t = DIR_SAIDA / "tabela_top3_pivotada_50k.parquet"
    if alt_t.exists():
        PARQUET_TOP3 = alt_t
    else:
        alt_t2 = DIR_METRICAS / "tabela_top3_pivotada_50k.parquet"
        if alt_t2.exists():
            PARQUET_TOP3 = alt_t2

PASTA_GRAFICOS = DIR_SAIDA / "analises_cruzadas"
PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------
# Configurações de Cores e Mapeamentos
# ----------------------------------------------------------------
CORES_TIPOLOGIA = {
    "PASTO PRODUTIVO": "#faea40",
    "PASTO COM ERVAS": "#d8ff6c",
    "REG NATURAL": "#0e5f0e",
    "INTERMEDIARIO": "#f4b346",
    "DEG BIOLOGICA": "#813209",
    "PASTO COM LENHOSAS": "#66c600",
    "MISCELANEA": "#ec2b10",
    "Desconhecido": "#cccccc"
}

# Dicionário MapBiomas
MAPBIOMAS_DICT = {
    3: "Form. Savânica",
    4: "Form. Florestal",
    9: "Silvicultura",
    12: "Form. Campestre",
    15: "Pastagem",
    20: "Cult. Semi-Perene",
    21: "Mosaico de Usos",
    24: "Área Urbana",
    39: "Soja",
    41: "Outras Lavouras"
}

CORES_MAPBIOMAS = {
    "Pastagem": "#FFD966",
    "Soja": "#C27BA0",
    "Outras Lavouras": "#E06666",
    "Form. Florestal": "#006400",
    "Form. Savânica": "#00FF00",
    "Mosaico de Usos": "#ffebaf",
    "Form. Campestre": "#B8860B",
    "Silvicultura": "#935116",
    "Outros": "#d9d9d9"
}

# Mapeamento CVP
CVP_DICT = {
    1: "1: Baixo Vigor",
    2: "2: Médio Vigor",
    3: "3: Alto Vigor"
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


def plot_sankey(df):
    print("Gerando Diagrama de Sankey...")
    
    # Criar mapeamentos nomeados para legibilidade
    df['stable_name'] = df['stable_20_'].map(lambda x: MAPBIOMAS_DICT.get(x, "Outros MB"))
    df['c2025_name'] = df['class_2025'].map(lambda x: MAPBIOMAS_DICT.get(x, "Outros MB"))
    
    # Fluxo 1: Stable -> Class 2025
    flow1 = df.groupby(['stable_name', 'c2025_name']).size().reset_index(name='count')
    flow1.columns = ['source', 'target', 'value']
    
    # Fluxo 2: Class 2025 -> Embrapa
    flow2 = df.groupby(['c2025_name', 'class_embrapa']).size().reset_index(name='count')
    flow2.columns = ['source', 'target', 'value']
    
    # Concatenar para Sankey
    # Para distinguir as colunas se houver nomes iguais (ex: Pastagem -> Pastagem), adicionamos sufixos
    flow1['source'] = flow1['source'] + " (Hist)"
    flow1['target'] = flow1['target'] + " (2025)"
    flow2['source'] = flow2['source'] + " (2025)"
    flow2['target'] = flow2['target'] + " (Embrapa)"
    
    links = pd.concat([flow1, flow2], ignore_index=True)
    
    # Remover nós muito pequenos para não poluir
    links = links[links['value'] > 50]
    
    all_nodes = list(pd.unique(links[['source', 'target']].values.ravel('K')))
    node_mapping = {node: i for i, node in enumerate(all_nodes)}
    
    links['source_idx'] = links['source'].map(node_mapping)
    links['target_idx'] = links['target'].map(node_mapping)
    
    # Definir cores para os nós
    node_colors = []
    for node in all_nodes:
        if "(Embrapa)" in node:
            clean_name = node.replace(" (Embrapa)", "")
            node_colors.append(CORES_TIPOLOGIA.get(clean_name, "#cccccc"))
        else:
            clean_name = node.replace(" (Hist)", "").replace(" (2025)", "")
            node_colors.append(CORES_MAPBIOMAS.get(clean_name, "#cccccc"))
            
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = all_nodes,
          color = node_colors
        ),
        link = dict(
          source = links['source_idx'],
          target = links['target_idx'],
          value = links['value'],
          color = "rgba(200, 200, 200, 0.4)"
        )
    )])

    fig.update_layout(title_text="Fluxo de Transição: MapBiomas Histórico -> 2025 -> Embrapa", font_size=10)
    fig.write_html(str(PASTA_GRAFICOS / "sankey_fluxo_classes.html"))
    # fig.write_image(str(PASTA_GRAFICOS / "sankey_fluxo_classes.png"), scale=2) # Pode exigir kaleido, HTML é mais seguro
    print("  [ok] sankey_fluxo_classes.html")


def plot_stacked_bar_100(df):
    print("Gerando Gráfico de Barras Empilhadas (Vigor vs Embrapa)...")
    
    df['cvp_name'] = df['class_cvp'].map(CVP_DICT)
    
    # Preparar dados
    crosstab = pd.crosstab(df['cvp_name'], df['class_embrapa'], normalize='index') * 100
    
    # Ordenar colunas pela frequência geral para melhor visualização
    ordem_embrapa = df['class_embrapa'].value_counts().index
    crosstab = crosstab.reindex(columns=ordem_embrapa)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(top=0.85, right=0.8)
    
    bottom = np.zeros(len(crosstab))
    
    for col in crosstab.columns:
        values = crosstab[col].values
        ax.bar(crosstab.index, values, bottom=bottom, label=col,
               color=CORES_TIPOLOGIA.get(col, "#ccc"), edgecolor="white", width=0.6)
        
        # Adicionar texto nas barras maiores que 5%
        for i, val in enumerate(values):
            if val > 5:
                ax.text(i, bottom[i] + val/2, f"{val:.1f}%", ha='center', va='center', 
                        color='black', fontsize=9, fontweight='bold')
        
        bottom += values
        
    ax.set_ylabel("Proporção (%)", fontsize=11)
    ax.set_title("Composição da Classe Embrapa por Vigor do Sentinel-2 (100%)", fontsize=13, fontweight='bold', pad=20)
    
    # Remover bordas
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])
    
    plt.legend(title="Classe Embrapa", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    caminho = PASTA_GRAFICOS / "barras_empilhadas_vigor_embrapa.png"
    fig.savefig(caminho, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  [ok] {caminho.name}")


def plot_boxplots_biofisica(df):
    print("Gerando Boxplots Múltiplos (Vigor vs Biofísica)...")
    
    df['cvp_name'] = df['class_cvp'].map(CVP_DICT)
    variaveis = ['capim_1', 'solo_1', 'lenhosa_co_1', 'ruderal_1']
    titulos = ['Capim (%)', 'Solo Exposto (%)', 'Lenhosas (%)', 'Ruderais (%)']
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.subplots_adjust(hspace=0.3, wspace=0.2, top=0.9)
    
    for ax, var, tit in zip(axes.flat, variaveis, titulos):
        sns.boxplot(data=df, x='cvp_name', y=var, ax=ax, 
                    order=["1: Baixo Vigor", "2: Médio Vigor", "3: Alto Vigor"],
                    palette=["#ff9999", "#ffcc99", "#99ff99"], showfliers=False)
        
        ax.set_title(tit, fontsize=12, fontweight='bold')
        ax.set_xlabel("")
        ax.set_ylabel("Fração (%)")
        estilo_limpo(ax)
        
    fig.suptitle("Distribuição Biofísica da Pastagem por Índice de Vigor (CVP)", fontsize=15, fontweight='bold')
    
    caminho = PASTA_GRAFICOS / "boxplots_biofisica_por_vigor.png"
    fig.savefig(caminho, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  [ok] {caminho.name}")


def plot_barras_horizontais_md3(df):
    print("Gerando Gráfico de Barras Horizontais (Embrapa vs Confiança MD3)...")
    
    # Concordância de classes no Top-3: quantos dos 3 matches têm a mesma tipologia do top-1 (3, 2 ou 1)
    df['concordancia_md3'] = 1 + (df['tipologia_c_2'] == df['tipologia_c_1']).astype(int) + (df['tipologia_c_3'] == df['tipologia_c_1']).astype(int)
    
    # Agregar por class_embrapa e concordancia_md3
    agg = df.groupby(['class_embrapa', 'concordancia_md3']).size().reset_index(name='count')
    
    # Ordem principal (da menor para a maior para barh)
    totais = agg.groupby('class_embrapa')['count'].sum().sort_values(ascending=True)
    
    # Cores fixas para cada nível de MD3
    cores_md3 = {
        3: "#1a9641", # Verde (Alta)
        2: "#fdae61", # Laranja/Amarelo (Média)
        1: "#d7191c"  # Vermelho (Baixa)
    }
    
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.subplots_adjust(right=0.75) # Espaço para legenda
    
    bottoms = np.zeros(len(totais))
    
    for md in [3, 2, 1]:
        valores = []
        for c in totais.index:
            v = agg[(agg['class_embrapa'] == c) & (agg['concordancia_md3'] == md)]['count'].sum()
            valores.append(v)
            
        ax.barh(totais.index, valores, left=bottoms, height=0.7, 
                color=cores_md3[md], edgecolor='white', linewidth=0.5, label=f"MD3 = {md}")
        
        # Adicionar texto das porcentagens no meio de cada segmento
        for i, val in enumerate(valores):
            total_classe = totais.values[i]
            # Mostrar apenas se o segmento for > 5% do valor MÁXIMO global (para caber fisicamente na tela)
            if val > totais.max() * 0.05:
                pct = (val / total_classe) * 100
                ax.text(bottoms[i] + val/2, i, f"{pct:.1f}%", 
                        va='center', ha='center', color='black' if md == 2 else 'white', 
                        fontweight='bold', fontsize=9)
        
        bottoms += np.array(valores)

    ax.set_xlabel("Número de Pontos MapBiomas", fontsize=11, labelpad=10)
    ax.set_title("Proporção do Nível de Confiança (MD3) por Classe Embrapa", fontsize=14, fontweight='bold', pad=15)
    
    # Estilo limpo ajustado para barras horizontais
    ax.set_facecolor("white")
    ax.figure.set_facecolor("white")
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(axis="y", length=0, labelsize=10, colors="#333333")
    ax.tick_params(axis="x", labelsize=10, colors="#333333")
    
    # Legenda (Movida para o meio/centro-esquerda)
    handles, labels = ax.get_legend_handles_labels()
    labels_mapped = {
        "MD3 = 3": "MD3 = 3 (Alta Confiança)",
        "MD3 = 2": "MD3 = 2 (Confiança Média)",
        "MD3 = 1": "MD3 = 1 (Baixa Confiança)"
    }
    ax.legend(handles, [labels_mapped[l] for l in labels], 
              title="Nível de Confiança", bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False)
    
    # Adicionar o total de pontos no final de cada barra
    for i, total in enumerate(totais.values):
        ax.text(total + (totais.max() * 0.01), i, f"n={total:,}", 
                va='center', ha='left', color='#555555', fontsize=9)
    
    caminho = PASTA_GRAFICOS / "barras_confianca_md3_embrapa.png"
    fig.savefig(caminho, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  [ok] {caminho.name}")


def plot_classes_mapbiomas_md3_limiar(df):
    print("Gerando Gráficos de Classes MapBiomas (Limiar 0.75 + Barras MD3 em Tons de Cinza)...")
    
    from matplotlib.patches import Patch
    
    NOMES_MAPBIOMAS = {
        15: "Pastagem",
        4: "Formação Florestal",
        21: "Mosaico de Usos",
        3: "Formação Savânica",
        39: "Soja",
        41: "Outras Lavouras Temp.",
        12: "Formação Campestre",
        9: "Silvicultura",
    }

    CORES_CLASSES_MB = {
        "Pastagem": "#ffd966",
        "Formação Florestal": "#1b6d26",
        "Mosaico de Usos": "#b88a3b",
        "Formação Savânica": "#539e44",
        "Soja": "#e59828",
        "Outras Lavouras Temp.": "#e8ba5d",
        "Formação Campestre": "#9ec76f",
        "Silvicultura": "#6b4423",
        "Demais classes": "#8c8c8c"
    }

    df_plot = df.copy()
    df_plot['classe_nome'] = df_plot['class_2025'].map(lambda x: NOMES_MAPBIOMAS.get(x, "Demais classes"))
    df_plot['atinge_75'] = df_plot['prod_escalar_1'] >= 0.75

    def _gerar_grafico_barras_duplas(df_subset, titulo, subtitulo, nome_arquivo, total_base=50000):
        contagens = df_subset['classe_nome'].value_counts()
        ordem_plot = list(reversed(contagens.index.tolist()))
        
        y = np.arange(len(ordem_plot))
        height = 0.36
        
        fig, ax = plt.subplots(figsize=(13, 7 + len(ordem_plot)*0.35))
        fig.subplots_adjust(right=0.70, left=0.24, top=0.88, bottom=0.10)
        
        # 1. Barra da Classe com corte de Limiar 0.75 (y + height/2)
        y_classe = y + height/2
        
        for i, c in enumerate(ordem_plot):
            sub = df_subset[df_subset['classe_nome'] == c]
            tot = len(sub)
            n_com_75 = (sub['atinge_75'] == True).sum()
            n_sem_75 = (sub['atinge_75'] == False).sum()
            cor = CORES_CLASSES_MB.get(c, "#8c8c8c")
            
            # Parte sem limiar (< 0.75) - sólida lisa
            if n_sem_75 > 0:
                ax.barh(y_classe[i], n_sem_75, height=height, color=cor, 
                        edgecolor="#333333", linewidth=0.6, zorder=3)
                
            # Parte com limiar (>= 0.75) - tracejada / hachurada
            if n_com_75 > 0:
                ax.barh(y_classe[i], n_com_75, left=n_sem_75, height=height, color=cor,
                        hatch="//", edgecolor="#333333", linewidth=0.6, zorder=3)
                
            # Rótulo com total e %
            pct = (tot / total_base) * 100
            ax.text(tot + (contagens.max() * 0.015), y_classe[i], 
                    f"{tot:,} ({pct:.2f}%)", va='center', ha='left',
                    fontsize=9, fontweight='bold', color="#222222")

        # 2. Barra Lateral de MD3 em Tons de Cinza (y - height/2)
        y_md3 = y - height/2
        
        for i, c in enumerate(ordem_plot):
            sub = df_subset[df_subset['classe_nome'] == c]
            tot = len(sub)
            n_md1 = (sub['md3'] == 1).sum()
            n_md2 = (sub['md3'] == 2).sum()
            n_md3 = (sub['md3'] == 3).sum()
            
            # MD3 = 1 (Cinza claro)
            ax.barh(y_md3[i], n_md1, height=height, color="#d9d9d9", 
                    edgecolor="white", linewidth=0.5, zorder=3)
            # MD3 = 2 (Cinza médio)
            ax.barh(y_md3[i], n_md2, left=n_md1, height=height, color="#969696", 
                    edgecolor="white", linewidth=0.5, zorder=3)
            # MD3 = 3 (Cinza escuro)
            ax.barh(y_md3[i], n_md3, left=n_md1 + n_md2, height=height, color="#525252", 
                    edgecolor="white", linewidth=0.5, zorder=3)
            
            # Rótulos internos se couberem
            if tot > 0:
                if n_md1 > contagens.max() * 0.06:
                    ax.text(n_md1/2, y_md3[i], f"{n_md1/tot*100:.0f}%", 
                            va='center', ha='center', fontsize=8, color="#222222", fontweight='bold')
                if n_md2 > contagens.max() * 0.06:
                    ax.text(n_md1 + n_md2/2, y_md3[i], f"{n_md2/tot*100:.0f}%", 
                            va='center', ha='center', fontsize=8, color="#ffffff", fontweight='bold')
                if n_md3 > contagens.max() * 0.06:
                    ax.text(n_md1 + n_md2 + n_md3/2, y_md3[i], f"{n_md3/tot*100:.0f}%", 
                            va='center', ha='center', fontsize=8, color="#ffffff", fontweight='bold')

        ax.set_yticks(y)
        ax.set_yticklabels(ordem_plot, fontsize=10, fontweight='bold')
        ax.set_xlabel("Número de Pontos MapBiomas na Base 50k", fontsize=11, labelpad=8)
        
        # Estilo limpo
        ax.set_facecolor("white")
        ax.figure.set_facecolor("white")
        ax.grid(axis="x", color="#e6e6e6", linewidth=0.9, zorder=0)
        ax.set_axisbelow(True)
        for spine in ["top", "right", "left"]:
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color("#cccccc")
        ax.tick_params(axis="both", length=0, labelsize=9.5, colors="#333333")
        
        # Legenda explicativa
        legend_elements = [
            Patch(facecolor="#aaaaaa", hatch="//", edgecolor="#333333", label="Atinge Limiar (≥ 0.75)"),
            Patch(facecolor="#aaaaaa", edgecolor="#333333", label="Abaixo do Limiar (< 0.75)"),
            Patch(facecolor="#525252", label="md3 = 3 (Alta Confiança)"),
            Patch(facecolor="#969696", label="md3 = 2 (Confiança Média)"),
            Patch(facecolor="#d9d9d9", label="md3 = 1 (Baixa Confiança)"),
        ]
        ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1.02, 0.5), 
                  title="Classificação & Confiança", frameon=False, fontsize=9, title_fontsize=10)
        
        fig.suptitle(titulo, fontsize=13, fontweight='bold', y=0.96)
        if subtitulo:
            ax.set_title(subtitulo, fontsize=9.5, color="#666666", pad=12)
            
        caminho = PASTA_GRAFICOS / nome_arquivo
        fig.savefig(caminho, dpi=200, bbox_inches='tight')
        plt.close(fig)
        print(f"  [ok] {caminho.name}")

    # 1. Não-Pastagem (5.057 pontos)
    df_nao_pasto = df_plot[df_plot['classe_nome'] != "Pastagem"].copy()
    _gerar_grafico_barras_duplas(
        df_nao_pasto,
        "As 5.057 Amostras Não-Pastagem (MapBiomas 2025)",
        "Barra superior: Classe MapBiomas (Tracejado = corte ≥ 0.75 | Lisa = < 0.75)  •  Barra inferior: Composição MD3 em tons de cinza",
        "classes_nao_pastagem_md3_limiar.png"
    )

    # 2. Todas as Classes (50.000 pontos)
    _gerar_grafico_barras_duplas(
        df_plot,
        "Distribuição Total de Classes MapBiomas (2025) na Base 50k",
        "Barra superior: Classe MapBiomas (Tracejado = corte ≥ 0.75 | Lisa = < 0.75)  •  Barra inferior: Composição MD3 em tons de cinza",
        "todas_classes_mapbiomas_md3_limiar.png"
    )


def main():
    print("=" * 70)
    print("GERANDO ANÁLISES CRUZADAS (MapBiomas x Embrapa)")
    print("=" * 70)
    
    df = pd.read_parquet(PARQUET_TOP3)
    print(f"Dados carregados: {len(df)} pontos.")
    
    plot_sankey(df)
    plot_stacked_bar_100(df)
    plot_boxplots_biofisica(df)
    plot_barras_horizontais_md3(df)
    plot_classes_mapbiomas_md3_limiar(df)
    
    print("\nTodas as análises cruzadas concluídas!")
    print(f"Salvas em: {PASTA_GRAFICOS}")

if __name__ == "__main__":
    main()
