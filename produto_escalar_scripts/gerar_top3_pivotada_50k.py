"""
gerar_top3_pivotada_50k.py
==========================
Gera a tabela Top-3 pivotada a partir dos embeddings anuais da base 50k
(com coordenadas lat_alvo e lon_alvo) e dos 701 pontos de referência da Embrapa.
Utiliza cálculo direto de produto escalar via streaming (DuckDB).

Saídas por ano:
  1. produto_escalar_metricas/arquivos_saida/tabela_top3_pivotada_50k_{year}.parquet (~3.3 MB)
  2. assets/tabela_top3_50k_{year}.csv (para download e análises tabulares)
  3. assets/tabela_top3_50k_{year}.json (para mapas e tabelas interativas)

Uso:
    python gerar_top3_pivotada_50k.py                # Processa ano padrão (2025)
    python gerar_top3_pivotada_50k.py --year 2024   # Processa ano específico
    python gerar_top3_pivotada_50k.py --year all    # Processa todos os anos (2019 a 2025)
"""

import duckdb
import time
import argparse
import json
from pathlib import Path

DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_ARQUIVOS_BASE = DIR_METRICAS / "arquivos_base"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_ASSETS = DIR_ROOT / "assets"

DIR_SAIDA.mkdir(parents=True, exist_ok=True)
DIR_ASSETS.mkdir(parents=True, exist_ok=True)

PARQUET_EMBRAPA = DIR_ARQUIVOS_BASE / "embeddings_embrapa_year_colet.parquet"

# Expressão SQL do produto escalar (64 dimensões)
DOT_PROD_SQL = " + ".join([f"e.A{i:02d} * m.A{i:02d}" for i in range(64)])

def processar_ano(ano: int, con: duckdb.DuckDBPyConnection):
    parquet_50k = DIR_ARQUIVOS_BASE / f"embeddings_samples_50k_cvp_s2_cerrado_{ano}.parquet"
    if not parquet_50k.exists():
        # Fallback para extrair do multi-ano se necessário
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

    out_parquet = DIR_SAIDA / f"tabela_top3_pivotada_50k_{ano}.parquet"
    out_csv_assets = DIR_ASSETS / f"tabela_top3_50k_{ano}.csv"
    out_json_assets = DIR_ASSETS / f"tabela_top3_50k_{ano}.json"

    print("-" * 65)
    print(f"Processando Top-3 para o ano: {ano}")
    print(f"  Entrada 50k:     {parquet_50k.name}")
    print(f"  Entrada Embrapa: {PARQUET_EMBRAPA.name}")
    print(f"  Saída Parquet:   {out_parquet.name}")
    print(f"  Saída Assets:    {out_csv_assets.name}, {out_json_assets.name}")

    t0 = time.time()

    # Query completa: Produto Escalar -> Rank Top 3 -> Pivot -> MD3 & Metadados (incluindo lat_alvo e lon_alvo)
    query_base = f"""
        WITH prod AS (
            SELECT 
                m.id,
                m.year,
                e.TARGET_FID,
                ({DOT_PROD_SQL}) AS resultado_multiplicacao,
                e.Origem,
                e.TIPOLOGIAc,
                e.Tipologia_,
                e.altitude,
                e.capim,
                e.lenhosa_co,
                e.ruderal,
                e.solo,
                e.latitude AS lat_ref,
                e.longitude AS lon_ref,
                m.lat_alvo,
                m.lon_alvo,
                m.class_cvp,
                m.class_2025,
                m.stable_20_
            FROM '{PARQUET_EMBRAPA.as_posix()}' AS e
            CROSS JOIN '{parquet_50k.as_posix()}' AS m
        ),
        ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY id
                    ORDER BY resultado_multiplicacao DESC
                ) AS rn
            FROM prod
        ),
        pivoted AS (
            SELECT
                id,
                MAX(CASE WHEN rn = 1 THEN lat_alvo END) AS lat_alvo,
                MAX(CASE WHEN rn = 1 THEN lon_alvo END) AS lon_alvo,
                MAX(CASE WHEN rn = 1 THEN CAST(lat_alvo AS VARCHAR) || ', ' || CAST(lon_alvo AS VARCHAR) END) AS loc_alvo,
                MAX(CASE WHEN rn = 1 THEN class_cvp END) AS class_cvp,
                MAX(CASE WHEN rn = 1 THEN class_2025 END) AS class_2025,
                MAX(CASE WHEN rn = 1 THEN stable_20_ END) AS stable_20_,

                MAX(CASE WHEN rn = 1 THEN TARGET_FID END) AS target_fid_1,
                MAX(CASE WHEN rn = 1 THEN resultado_multiplicacao END) AS prod_escalar_1,
                MAX(CASE WHEN rn = 1 THEN Origem END) AS origem_1,
                MAX(CASE WHEN rn = 1 THEN COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_) END) AS tipologia_c_1,
                MAX(CASE WHEN rn = 1 THEN Tipologia_ END) AS tipologia_1,
                MAX(CASE WHEN rn = 1 THEN capim END) AS capim_1,
                MAX(CASE WHEN rn = 1 THEN lenhosa_co END) AS lenhosa_co_1,
                MAX(CASE WHEN rn = 1 THEN ruderal END) AS ruderal_1,
                MAX(CASE WHEN rn = 1 THEN solo END) AS solo_1,
                MAX(CASE WHEN rn = 1 THEN altitude END) AS altitude_1,
                MAX(CASE WHEN rn = 1 THEN CAST(lat_ref AS VARCHAR) || ', ' || CAST(lon_ref AS VARCHAR) END) AS loc_1,
                MAX(CASE WHEN rn = 1 THEN class_cvp END) AS class_cvp_1,
                MAX(CASE WHEN rn = 1 THEN class_2025 END) AS class_2025_1,
                MAX(CASE WHEN rn = 1 THEN stable_20_ END) AS stable_20_1,

                MAX(CASE WHEN rn = 2 THEN TARGET_FID END) AS target_fid_2,
                MAX(CASE WHEN rn = 2 THEN resultado_multiplicacao END) AS prod_escalar_2,
                MAX(CASE WHEN rn = 2 THEN Origem END) AS origem_2,
                MAX(CASE WHEN rn = 2 THEN COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_) END) AS tipologia_c_2,
                MAX(CASE WHEN rn = 2 THEN Tipologia_ END) AS tipologia_2,
                MAX(CASE WHEN rn = 2 THEN capim END) AS capim_2,
                MAX(CASE WHEN rn = 2 THEN lenhosa_co END) AS lenhosa_co_2,
                MAX(CASE WHEN rn = 2 THEN ruderal END) AS ruderal_2,
                MAX(CASE WHEN rn = 2 THEN solo END) AS solo_2,
                MAX(CASE WHEN rn = 2 THEN altitude END) AS altitude_2,
                MAX(CASE WHEN rn = 2 THEN CAST(lat_ref AS VARCHAR) || ', ' || CAST(lon_ref AS VARCHAR) END) AS loc_2,
                MAX(CASE WHEN rn = 2 THEN class_cvp END) AS class_cvp_2,
                MAX(CASE WHEN rn = 2 THEN class_2025 END) AS class_2025_2,
                MAX(CASE WHEN rn = 2 THEN stable_20_ END) AS stable_20_2,

                MAX(CASE WHEN rn = 3 THEN TARGET_FID END) AS target_fid_3,
                MAX(CASE WHEN rn = 3 THEN resultado_multiplicacao END) AS prod_escalar_3,
                MAX(CASE WHEN rn = 3 THEN Origem END) AS origem_3,
                MAX(CASE WHEN rn = 3 THEN COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_) END) AS tipologia_c_3,
                MAX(CASE WHEN rn = 3 THEN Tipologia_ END) AS tipologia_3,
                MAX(CASE WHEN rn = 3 THEN capim END) AS capim_3,
                MAX(CASE WHEN rn = 3 THEN lenhosa_co END) AS lenhosa_co_3,
                MAX(CASE WHEN rn = 3 THEN ruderal END) AS ruderal_3,
                MAX(CASE WHEN rn = 3 THEN solo END) AS solo_3,
                MAX(CASE WHEN rn = 3 THEN altitude END) AS altitude_3,
                MAX(CASE WHEN rn = 3 THEN CAST(lat_ref AS VARCHAR) || ', ' || CAST(lon_ref AS VARCHAR) END) AS loc_3,
                MAX(CASE WHEN rn = 3 THEN class_cvp END) AS class_cvp_3,
                MAX(CASE WHEN rn = 3 THEN class_2025 END) AS class_2025_3,
                MAX(CASE WHEN rn = 3 THEN stable_20_ END) AS stable_20_3
            FROM ranked
            WHERE rn <= 3
            GROUP BY id
        )
        SELECT 
            {ano} AS year,
            *,
            tipologia_c_1 AS class_embrapa,
            (prod_escalar_1 + prod_escalar_2 + prod_escalar_3) / 3.0 AS md3
        FROM pivoted
        ORDER BY id
    """

    # 1. Exportar Parquet
    con.execute(f"COPY ({query_base}) TO '{out_parquet.as_posix()}' (FORMAT PARQUET)")
    size_parquet = out_parquet.stat().st_size / (1024 * 1024)

    # 2. Exportar CSV único para assets/
    con.execute(f"COPY (SELECT * FROM '{out_parquet.as_posix()}') TO '{out_csv_assets.as_posix()}' (HEADER, DELIMITER ',')")
    size_csv = out_csv_assets.stat().st_size / (1024 * 1024)

    # 3. Exportar JSON compacto em assets/ (versão ultra-leve e de alta performance para a web)
    tip_map = {
        'PASTO PRODUTIVO': 0, 'PRODUTIVO': 0,
        'PASTO COM ERVAS': 1,
        'PASTO COM LENHOSAS': 2,
        'INTERMEDIARIO': 3,
        'DEG BIOLOGICA': 4,
        'REG NATURAL': 5,
        'MISCELANEA': 6,
        'Outros': 7
    }
    tip_list = [
        'PASTO PRODUTIVO', 'PASTO COM ERVAS', 'PASTO COM LENHOSAS',
        'INTERMEDIARIO', 'DEG BIOLOGICA', 'REG NATURAL', 'MISCELANEA', 'Outros'
    ]

    web_df = con.execute(f"""
        SELECT 
            id,
            ROUND(lat_alvo, 4) AS lat,
            ROUND(lon_alvo, 4) AS lon,
            tipologia_c_1 AS tip1,
            ROUND(prod_escalar_1, 3) AS p1,
            target_fid_1 AS fid1,
            ROUND(md3, 3) AS md3,
            loc_1,
            class_cvp AS cvp,
            target_fid_2 AS fid2,
            ROUND(prod_escalar_2, 3) AS p2,
            tipologia_c_2 AS tip2,
            loc_2,
            target_fid_3 AS fid3,
            ROUND(prod_escalar_3, 3) AS p3,
            tipologia_c_3 AS tip3,
            loc_3
        FROM '{out_parquet.as_posix()}'
    """).df()

    rows = []
    for row in web_df.itertuples(index=False):
        t1 = tip_map.get(str(row.tip1).strip().upper() if row.tip1 else 'Outros', 7)
        t2 = tip_map.get(str(row.tip2).strip().upper() if row.tip2 else 'Outros', 7)
        t3 = tip_map.get(str(row.tip3).strip().upper() if row.tip3 else 'Outros', 7)
        rows.append([
            int(row.id),
            float(row.lat) if row.lat is not None else 0.0,
            float(row.lon) if row.lon is not None else 0.0,
            t1,
            float(row.p1) if row.p1 is not None else 0.0,
            int(row.fid1) if row.fid1 is not None else -1,
            float(row.md3) if row.md3 is not None else 0.0,
            str(row.loc_1) if row.loc_1 is not None else '',
            int(row.cvp) if row.cvp is not None else 1,
            int(row.fid2) if row.fid2 is not None else -1,
            float(row.p2) if row.p2 is not None else 0.0,
            t2,
            str(row.loc_2) if row.loc_2 is not None else '',
            int(row.fid3) if row.fid3 is not None else -1,
            float(row.p3) if row.p3 is not None else 0.0,
            t3,
            str(row.loc_3) if row.loc_3 is not None else ''
        ])

    compact_payload = {
        'year': int(ano),
        'total': len(rows),
        'tipologias': tip_list,
        'cols': ['id', 'lat', 'lon', 't1', 'p1', 'fid1', 'md3', 'loc1', 'cvp', 'fid2', 'p2', 't2', 'loc2', 'fid3', 'p3', 't3', 'loc3'],
        'data': rows
    }

    with open(out_json_assets, 'w', encoding='utf-8') as f:
        json.dump(compact_payload, f, separators=(',', ':'))

    size_json = out_json_assets.stat().st_size / (1024 * 1024)

    elapsed = time.time() - t0
    print(f"  [OK] Concluído em {elapsed:.2f}s:")
    print(f"       - Parquet: {size_parquet:.2f} MB")
    print(f"       - CSV:     {size_csv:.2f} MB")
    print(f"       - JSON:    {size_json:.2f} MB (Compacto/Otimizado)")

    return out_parquet

def main():
    parser = argparse.ArgumentParser(description="Gera tabela Top-3 pivotada 50k por ano.")
    parser.add_argument("--year", default="2025", help="Ano a processar (ex: 2025, 2024, ou 'all')")
    args = parser.parse_args()

    print("=" * 70)
    print("GERADOR DE TABELA TOP-3 PIVOTADA POR ANO (50k COM LAT_ALVO E LON_ALVO)")
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
