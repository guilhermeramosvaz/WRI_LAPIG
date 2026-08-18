"""
Exporta a distribuição das classes e os 701 pontos de campo da Embrapa
a partir de produto_escalar_metricas/arquivos_base/embeddings_embrapa_year_colet.parquet
para assets/embrapa_referencia.json
"""

import json
from pathlib import Path
import duckdb

DIR_SCRIPT = Path(__file__).resolve().parent
DIR_DADOS = DIR_SCRIPT.parent
DIR_ROOT = DIR_DADOS.parent

EMBRAPA_PARQUET = DIR_DADOS / "arquivos_base" / "embeddings_embrapa_year_colet.parquet"
OUT_JSON = DIR_ROOT / "docs" / "assets" / "embrapa_referencia.json"

def exportar():
    if not EMBRAPA_PARQUET.exists():
        print(f"[ERRO] Arquivo Embrapa não encontrado: {EMBRAPA_PARQUET}")
        return

    con = duckdb.connect()
    
    # 1. Distribuição estática por classe
    query_dist = f"""
        WITH padronizado AS (
            SELECT 
                TARGET_FID AS target_fid,
                latitude,
                longitude,
                COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_) AS tipologia_raw,
                CASE 
                    WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%PRODUTIVO%' THEN 'PASTO PRODUTIVO'
                    WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%ERVA%' THEN 'PASTO COM ERVAS'
                    WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%LENHOSA%' THEN 'PASTO COM LENHOSAS'
                    WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%INTERMEDIARIO%' OR UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%INTERMEDIÁRIO%' THEN 'INTERMEDIARIO'
                    WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%DEGRAD%' OR UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%DEG BIOLOGICA%' THEN 'DEG BIOLOGICA'
                    WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%REG%' OR UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%REGENERAÇÃO%' THEN 'REG NATURAL'
                    ELSE 'MISCELANEA'
                END AS tipologia_classe
            FROM '{EMBRAPA_PARQUET.as_posix()}'
        )
        SELECT 
            tipologia_classe,
            COUNT(*) AS total,
            ROUND(COUNT(*) * 100.0 / 701, 1) AS percentual
        FROM padronizado
        GROUP BY tipologia_classe
        ORDER BY total DESC
    """
    
    df_dist = con.execute(query_dist).df()
    
    distribuicao = {}
    for row in df_dist.itertuples(index=False):
        distribuicao[row.tipologia_classe] = {
            'total': int(row.total),
            'percentual': float(row.percentual)
        }

    # 2. Lista dos 701 pontos de campo com Target_FID, coordenadas e tipologia
    query_pts = f"""
        SELECT 
            TARGET_FID AS fid,
            ROUND(latitude, 5) AS lat,
            ROUND(longitude, 5) AS lon,
            CASE 
                WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%PRODUTIVO%' THEN 'PASTO PRODUTIVO'
                WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%ERVA%' THEN 'PASTO COM ERVAS'
                WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%LENHOSA%' THEN 'PASTO COM LENHOSAS'
                WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%INTERMEDIARIO%' OR UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%INTERMEDIÁRIO%' THEN 'INTERMEDIARIO'
                WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%DEGRAD%' OR UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%DEG BIOLOGICA%' THEN 'DEG BIOLOGICA'
                WHEN UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%REG%' OR UPPER(COALESCE(NULLIF(TIPOLOGIAc, 'nao se aplica'), Tipologia_)) LIKE '%REGENERAÇÃO%' THEN 'REG NATURAL'
                ELSE 'MISCELANEA'
            END AS classe
        FROM '{EMBRAPA_PARQUET.as_posix()}'
        ORDER BY TARGET_FID
    """
    
    df_pts = con.execute(query_pts).df()
    pontos = []
    for row in df_pts.itertuples(index=False):
        pontos.append({
            'fid': int(row.fid) if row.fid is not None else -1,
            'lat': float(row.lat) if row.lat is not None else 0.0,
            'lon': float(row.lon) if row.lon is not None else 0.0,
            'classe': str(row.classe)
        })
        
    payload = {
        'total_amostras': len(pontos),
        'fonte': 'Embrapa Cerrado (701 pontos de referência de campo)',
        'distribuicao': distribuicao,
        'pontos': pontos
    }
    
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(payload, f, separators=(',', ':'), ensure_ascii=False)
        
    print(f"[OK] Exportado com sucesso: {OUT_JSON}")
    print(f"     Total de pontos Embrapa: {len(pontos)}")
    print(f"     Distribuição estática:")
    for k, v in distribuicao.items():
        print(f"       - {k}: {v['total']} ({v['percentual']}%)")

if __name__ == '__main__':
    exportar()
