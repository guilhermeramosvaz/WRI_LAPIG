"""
gerar_matriz_similaridade_50k.py
================================
Gera a matriz de similaridade pivotada por ano a partir dos embeddings da base 50k
(com lat_alvo e lon_alvo) e dos 701 pontos Embrapa.
Utiliza cálculo direto via streaming DuckDB PIVOT.

Saídas: produto_escalar_metricas/arquivos_saida/matriz_similaridade_50k_{year}.parquet
  - Linhas: 50.000 pontos MapBiomas
  - Colunas: id, year, lat_alvo, lon_alvo, class_cvp, class_2025, stable_20_, mais os 701 TARGET_FIDs
  - Valores: produto escalar (similaridade cosseno)

Uso:
    python gerar_matriz_similaridade_50k.py                # Processa ano padrão (2025)
    python gerar_matriz_similaridade_50k.py --year 2024   # Processa ano específico
    python gerar_matriz_similaridade_50k.py --year all    # Processa todos os anos (2019 a 2025)
"""

import duckdb
import time
import argparse
from pathlib import Path

DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_ARQUIVOS_BASE = DIR_METRICAS / "arquivos_base"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_SAIDA.mkdir(parents=True, exist_ok=True)

PARQUET_EMBRAPA = DIR_ARQUIVOS_BASE / "embeddings_embrapa_year_colet.parquet"
DOT_PROD_SQL = " + ".join([f"e.A{i:02d} * m.A{i:02d}" for i in range(64)])

def processar_ano(ano: int, con: duckdb.DuckDBPyConnection):
    parquet_50k = DIR_ARQUIVOS_BASE / f"embeddings_samples_50k_cvp_s2_cerrado_{ano}.parquet"
    if not parquet_50k.exists():
        multi_candidatos = [
            DIR_ARQUIVOS_BASE / "embeddings_50k_localizado_via_join.parquet",
            DIR_ROOT / "data" / "embeddings_50k_localizado_via_join.parquet",
            DIR_ARQUIVOS_BASE / "embeddings_samples_50k_cvp_s2_cerrado_2019_2025_v1.parquet"
        ]
        multi_ano = next((p for p in multi_candidatos if p.exists()), None)
        if multi_ano:
            print(f"  [Info] Extraindo ano {ano} a partir de {multi_ano.name} ...")
            con.execute(f"""
                COPY (
                    SELECT * FROM '{multi_ano.as_posix()}' WHERE year = {ano} ORDER BY id
                ) TO '{parquet_50k.as_posix()}' (FORMAT PARQUET)
            """)
        else:
            print(f"  [Erro] Arquivo base para ano {ano} não encontrado: {parquet_50k}")
            return None

    out_matriz = DIR_SAIDA / f"matriz_similaridade_50k_{ano}.parquet"

    print("-" * 65)
    print(f"Gerando Matriz de Similaridade para o ano: {ano}")
    print(f"  Entrada 50k:     {parquet_50k.name}")
    print(f"  Entrada Embrapa: {PARQUET_EMBRAPA.name}")
    print(f"  Saída Matriz:    {out_matriz.name}")

    t0 = time.time()

    con.execute(f"""
        COPY (
            PIVOT (
                SELECT 
                    m.id,
                    {ano} AS year,
                    m.lat_alvo,
                    m.lon_alvo,
                    m.class_cvp,
                    m.class_2025,
                    m.stable_20_,
                    e.TARGET_FID,
                    ({DOT_PROD_SQL}) AS resultado_multiplicacao
                FROM '{PARQUET_EMBRAPA.as_posix()}' AS e
                CROSS JOIN '{parquet_50k.as_posix()}' AS m
            ) ON TARGET_FID
            USING max(resultado_multiplicacao)
            GROUP BY id, year, lat_alvo, lon_alvo, class_cvp, class_2025, stable_20_
            ORDER BY id
        ) TO '{out_matriz.as_posix()}' (FORMAT PARQUET)
    """)

    size_mb = out_matriz.stat().st_size / (1024 * 1024)
    elapsed = time.time() - t0
    print(f"  [OK] Matriz {ano} salva em {elapsed:.2f}s ({size_mb:.2f} MB)")
    return out_matriz

def main():
    parser = argparse.ArgumentParser(description="Gera matriz de similaridade 50k por ano.")
    parser.add_argument("--year", default="2025", help="Ano a processar (ex: 2025, 2024, ou 'all')")
    args = parser.parse_args()

    print("=" * 70)
    print("GERADOR DE MATRIZ DE SIMILARIDADE POR ANO (50k)")
    print("=" * 70)

    con = duckdb.connect()

    if args.year.lower() == "all":
        anos = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    else:
        try:
            anos = [int(args.year)]
        except ValueError:
            print(f"Erro: Ano inválido '{args.year}'")
            return

    t_total = time.time()
    for ano in anos:
        processar_ano(ano, con)

    print("\n" + "=" * 70)
    print(f"Processamento concluído com sucesso em {time.time() - t_total:.2f}s!")
    print("=" * 70)

if __name__ == "__main__":
    main()
