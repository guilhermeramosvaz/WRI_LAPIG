"""
filtro_dados_matriz.py
======================
Filtra a matriz de similaridade mantendo apenas valores >= LIMIAR.
Valores abaixo do limiar são substituídos por NaN.
Se limiar = 0, não aplica filtro (sem limiar).

Uso:
    python filtro_dados_matriz.py               # default: limiar = 0.75
    python filtro_dados_matriz.py --limiar 0     # sem limiar
    python filtro_dados_matriz.py --limiar 0.75
"""

import argparse
import pandas as pd
from pathlib import Path

# ----------------------------------------------------------------
# Argumentos de linha de comando
# ----------------------------------------------------------------
parser = argparse.ArgumentParser(description="Filtra matriz de similaridade por limiar.")
parser.add_argument("--limiar", type=float, default=0.75,
                    help="Limiar mínimo de similaridade (default: 0.75). Use 0 para sem limiar.")
parser.add_argument("--year", default="2025",
                    help="Ano da matriz a processar (default: 2025).")
args = parser.parse_args()

LIMIAR = args.limiar
ANO = args.year
SEM_LIMIAR = (LIMIAR <= 0)
LIMIAR_LABEL = "sem_limiar" if SEM_LIMIAR else str(int(LIMIAR * 100))

# ----------------------------------------------------------------
# Caminhos
# ----------------------------------------------------------------
DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_SAIDA_LIMIAR = DIR_SAIDA / LIMIAR_LABEL
DIR_SAIDA_LIMIAR.mkdir(parents=True, exist_ok=True)

caminho_entrada = DIR_SAIDA / f"matriz_similaridade_50k_{ANO}.parquet"
if not caminho_entrada.exists():
    alt_m = DIR_SAIDA / "matriz_similaridade_50k.parquet"
    if alt_m.exists():
        caminho_entrada = alt_m
    else:
        alt_m2 = DIR_METRICAS / "matriz_similaridade_50k.parquet"
        if alt_m2.exists():
            caminho_entrada = alt_m2

caminho_saida = DIR_SAIDA_LIMIAR / f"matriz_similaridade_50k_mais_{LIMIAR_LABEL}.parquet"

# ----------------------------------------------------------------
# Processamento
# ----------------------------------------------------------------
if SEM_LIMIAR:
    print(f"Copiando matriz SEM filtro de limiar ...")
else:
    print(f"Filtrando matriz com limiar >= {LIMIAR} ...")
print(f"  Entrada: {caminho_entrada}")
print(f"  Saída:   {caminho_saida}")

# 1. Carregar o arquivo Parquet
df = pd.read_parquet(caminho_entrada)

# 2. Proteger as colunas de identificação e metadados
colunas_protegidas = ['id', 'class_cvp', 'class_2025', 'stable_20_']

# Isolar apenas as "demais colunas" onde o filtro será aplicado
colunas_alvo = [col for col in df.columns if col not in colunas_protegidas]

# 3. Aplicar a exclusão (apenas se tiver limiar)
if not SEM_LIMIAR:
    # Apagar apenas os valores < LIMIAR (eles viram NaN/Nulos),
    # mas mantém as linhas e metadados intactos.
    df[colunas_alvo] = df[colunas_alvo].where(df[colunas_alvo] >= LIMIAR)

# 4. Salvar o resultado
df.to_parquet(caminho_saida, index=False)

print(f"Arquivo salvo com sucesso: {caminho_saida.name}")
print(f"  Linhas: {len(df):,}")
print(f"  Colunas TARGET_FID: {len(colunas_alvo):,}")