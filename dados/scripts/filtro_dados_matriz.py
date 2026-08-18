"""
filtro_dados_matriz.py
======================
Filtra a matriz de similaridade mantendo apenas valores >= LIMIAR.
Valores abaixo do limiar são substituídos por NaN.

Uso:
    python filtro_dados_matriz.py               # default: limiar = 0.95
    python filtro_dados_matriz.py --limiar 0.75
"""

import argparse
import pandas as pd
from pathlib import Path

# ----------------------------------------------------------------
# Argumentos de linha de comando
# ----------------------------------------------------------------
parser = argparse.ArgumentParser(description="Filtra matriz de similaridade por limiar.")
parser.add_argument("--limiar", type=float, default=0.95,
                    help="Limiar mínimo de similaridade (default: 0.95)")
args = parser.parse_args()

LIMIAR = args.limiar
LIMIAR_INT = int(LIMIAR * 100)  # 95 ou 75

# ----------------------------------------------------------------
# Caminhos (relativos ao projeto)
# ----------------------------------------------------------------
DIR_BASE = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_BASE / "saida"
DIR_SAIDA_LIMIAR = DIR_SAIDA / str(LIMIAR_INT)
DIR_SAIDA_LIMIAR.mkdir(parents=True, exist_ok=True)

caminho_entrada = DIR_SAIDA / "matriz_similaridade_2024.parquet"
caminho_saida = DIR_SAIDA_LIMIAR / f"matriz_similaridade_2024_mais_{LIMIAR_INT}.csv"

# ----------------------------------------------------------------
# Processamento
# ----------------------------------------------------------------
print(f"Filtrando matriz com limiar >= {LIMIAR} ...")
print(f"  Entrada: {caminho_entrada}")
print(f"  Saída:   {caminho_saida}")

# 1. Carregar o arquivo Parquet
df = pd.read_parquet(caminho_entrada)

# 2. Proteger as colunas de identificação e coordenadas
colunas_protegidas = ['id_mapbiomas', 'latitude_alvo', 'longitude_alvo']

# Isolar apenas as "demais colunas" onde o filtro será aplicado
colunas_alvo = [col for col in df.columns if col not in colunas_protegidas]

# 3. Aplicar a exclusão
# Apagar apenas os valores < LIMIAR (eles viram NaN/Nulos),
# mas mantém as linhas e coordenadas intactas.
df[colunas_alvo] = df[colunas_alvo].where(df[colunas_alvo] >= LIMIAR)

# 4. Salvar o resultado no novo arquivo
df.to_csv(caminho_saida, index=False)

print(f"Arquivo salvo com sucesso: {caminho_saida.name}")