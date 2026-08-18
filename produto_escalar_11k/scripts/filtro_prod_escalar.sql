COPY (
    SELECT *
    FROM read_parquet('/var/home/gui/Documentos/saida_11k/saida_11k/output/prod_escalar_embrapa_mapbiomas.parquet')
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY id_alvo
        ORDER BY prod_escalar DESC
    ) <= 3
) TO '/var/home/gui/Documentos/saida_11k/saida_11k/output/top3_prod_escalar_por_mapbiomas.parquet' (FORMAT PARQUET);
