"""
separar_embeddings_por_ano.py
==============================
Separa o arquivo multi-ano embeddings_50k_localizado_via_join.parquet
(com campos lat_alvo e lon_alvo) em arquivos anuais individuais (2019 a 2025)
de 50.000 pontos cada.

Saídas: produto_escalar_metricas/arquivos_base/embeddings_samples_50k_cvp_s2_cerrado_{year}.parquet (~26 MB cada)

Uso:
    python separar_embeddings_por_ano.py
"""

import duckdb
import time
from pathlib import Path

DIR_ROOT = Path(__file__).resolve().parent.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_ARQUIVOS_BASE = DIR_METRICAS / "arquivos_base"
DIR_ARQUIVOS_BASE.mkdir(parents=True, exist_ok=True)

# Candidatos de arquivo multi-ano com prioridade para o arquivo com lat_alvo/lon_alvo
CANDIDATOS_MULTI_ANO = [
    DIR_ARQUIVOS_BASE / "embeddings_50k_localizado_via_join.parquet",
    DIR_ROOT / "data" / "embeddings_50k_localizado_via_join.parquet",
    DIR_ARQUIVOS_BASE / "embeddings_samples_50k_cvp_s2_cerrado_2019_2025_v1.parquet"
]

def obter_parquet_multi_ano():
    for p in CANDIDATOS_MULTI_ANO:
        if p.exists():
            return p
    return None

def separar_anos():
    print("=" * 70)
    print("SEPARANDO EMBEDDINGS 50K POR ANO (COM LAT_ALVO E LON_ALVO)")
    print("=" * 70)
    
    parquet_multi_ano = obter_parquet_multi_ano()
    if not parquet_multi_ano:
        print(f"Erro: Nenhum arquivo base multi-ano encontrado em:")
        for p in CANDIDATOS_MULTI_ANO:
            print(f"  - {p}")
        return
        
    con = duckdb.connect()
    
    # Identificar anos disponíveis
    anos_rows = con.execute(f"""
        SELECT DISTINCT year, count(*) 
        FROM '{parquet_multi_ano.as_posix()}' 
        GROUP BY year 
        ORDER BY year
    """).fetchall()
    
    print(f"\nArquivo multi-ano de origem: {parquet_multi_ano.name}")
    print(f"Anos identificados:")
    for ano, cnt in anos_rows:
        print(f"  - {ano}: {cnt:,} pontos")
        
    t_total = time.time()
    for ano, cnt in anos_rows:
        out_file = DIR_ARQUIVOS_BASE / f"embeddings_samples_50k_cvp_s2_cerrado_{ano}.parquet"
        t0 = time.time()
        print(f"\nExportando {ano} ({cnt:,} registros) -> {out_file.name} ...")
        
        con.execute(f"""
            COPY (
                SELECT * 
                FROM '{parquet_multi_ano.as_posix()}' 
                WHERE year = {ano}
                ORDER BY id
            ) TO '{out_file.as_posix()}' (FORMAT PARQUET)
        """)
        
        size_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"  Concluído em {time.time() - t0:.2f}s ({size_mb:.2f} MB)")
        
    print("\n" + "=" * 70)
    print(f"Todos os {len(anos_rows)} anos separados com sucesso em {time.time() - t_total:.2f}s!")
    print("=" * 70)

if __name__ == "__main__":
    separar_anos()
