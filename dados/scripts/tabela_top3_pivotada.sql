-- Tabela pivotada: cada id_alvo vira uma linha com os 3 maiores prod_escalar como colunas
-- loc_1, loc_2, loc_3 formatados para abrir no Google Earth (lat, lon)
COPY (
    WITH ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY id_alvo
                ORDER BY prod_escalar DESC
            ) AS rn
        FROM read_parquet('/var/home/gui/Documentos/saida_11k/saida_11k/output/top3_prod_escalar_por_mapbiomas.parquet')
    ),
    pivoted AS (
        SELECT
            id_alvo,
            -- Dados do MapBiomas (id_alvo)
            MAX(CASE WHEN rn = 1 THEN lat_alvo END) AS lat_alvo,
            MAX(CASE WHEN rn = 1 THEN lon_alvo END) AS lon_alvo,
            MAX(CASE WHEN rn = 1 THEN class_2025 END) AS class_2025,

            -- === TOP 1 (maior prod_escalar) ===
            MAX(CASE WHEN rn = 1 THEN TARGET_FID END) AS target_fid_1,
            MAX(CASE WHEN rn = 1 THEN prod_escalar END) AS prod_escalar_1,
            MAX(CASE WHEN rn = 1 THEN id END) AS id_1,
            MAX(CASE WHEN rn = 1 THEN Origem END) AS origem_1,
            MAX(CASE WHEN rn = 1 THEN TIPOLOGIAc END) AS tipologia_c_1,
            MAX(CASE WHEN rn = 1 THEN Tipologia_ END) AS tipologia_1,
            MAX(CASE WHEN rn = 1 THEN new_class END) AS new_class_1,
            MAX(CASE WHEN rn = 1 THEN newclassV2 END) AS newclassv2_1,
            MAX(CASE WHEN rn = 1 THEN capim END) AS capim_1,
            MAX(CASE WHEN rn = 1 THEN lenhosa_co END) AS lenhosa_co_1,
            MAX(CASE WHEN rn = 1 THEN ruderal END) AS ruderal_1,
            MAX(CASE WHEN rn = 1 THEN solo END) AS solo_1,
            MAX(CASE WHEN rn = 1 THEN altitude END) AS altitude_1,
            MAX(CASE WHEN rn = 1 THEN year_colet END) AS year_colet_1,
            MAX(CASE WHEN rn = 1 THEN CAST(lat_ref AS VARCHAR) || ', ' || CAST(lon_ref AS VARCHAR) END) AS loc_1,

            -- === TOP 2 ===
            MAX(CASE WHEN rn = 2 THEN TARGET_FID END) AS target_fid_2,
            MAX(CASE WHEN rn = 2 THEN prod_escalar END) AS prod_escalar_2,
            MAX(CASE WHEN rn = 2 THEN id END) AS id_2,
            MAX(CASE WHEN rn = 2 THEN Origem END) AS origem_2,
            MAX(CASE WHEN rn = 2 THEN TIPOLOGIAc END) AS tipologia_c_2,
            MAX(CASE WHEN rn = 2 THEN Tipologia_ END) AS tipologia_2,
            MAX(CASE WHEN rn = 2 THEN new_class END) AS new_class_2,
            MAX(CASE WHEN rn = 2 THEN newclassV2 END) AS newclassv2_2,
            MAX(CASE WHEN rn = 2 THEN capim END) AS capim_2,
            MAX(CASE WHEN rn = 2 THEN lenhosa_co END) AS lenhosa_co_2,
            MAX(CASE WHEN rn = 2 THEN ruderal END) AS ruderal_2,
            MAX(CASE WHEN rn = 2 THEN solo END) AS solo_2,
            MAX(CASE WHEN rn = 2 THEN altitude END) AS altitude_2,
            MAX(CASE WHEN rn = 2 THEN year_colet END) AS year_colet_2,
            MAX(CASE WHEN rn = 2 THEN CAST(lat_ref AS VARCHAR) || ', ' || CAST(lon_ref AS VARCHAR) END) AS loc_2,

            -- === TOP 3 ===
            MAX(CASE WHEN rn = 3 THEN TARGET_FID END) AS target_fid_3,
            MAX(CASE WHEN rn = 3 THEN prod_escalar END) AS prod_escalar_3,
            MAX(CASE WHEN rn = 3 THEN id END) AS id_3,
            MAX(CASE WHEN rn = 3 THEN Origem END) AS origem_3,
            MAX(CASE WHEN rn = 3 THEN TIPOLOGIAc END) AS tipologia_c_3,
            MAX(CASE WHEN rn = 3 THEN Tipologia_ END) AS tipologia_3,
            MAX(CASE WHEN rn = 3 THEN new_class END) AS new_class_3,
            MAX(CASE WHEN rn = 3 THEN newclassV2 END) AS newclassv3_3,
            MAX(CASE WHEN rn = 3 THEN capim END) AS capim_3,
            MAX(CASE WHEN rn = 3 THEN lenhosa_co END) AS lenhosa_co_3,
            MAX(CASE WHEN rn = 3 THEN ruderal END) AS ruderal_3,
            MAX(CASE WHEN rn = 3 THEN solo END) AS solo_3,
            MAX(CASE WHEN rn = 3 THEN altitude END) AS altitude_3,
            MAX(CASE WHEN rn = 3 THEN year_colet END) AS year_colet_3,
            MAX(CASE WHEN rn = 3 THEN CAST(lat_ref AS VARCHAR) || ', ' || CAST(lon_ref AS VARCHAR) END) AS loc_3

        FROM ranked
        GROUP BY id_alvo
    )
    SELECT
        *,
        -- class_embrapa: classe do ponto Embrapa com maior similaridade (top 1)
        tipologia_1 AS class_embrapa,
        -- md3: quantos dos 3 tops concordam com tipologia_1
        --   3 = todos iguais, 2 = um dos dois concorda, 1 = nenhum concorda
        1
        + CASE WHEN tipologia_2 = tipologia_1 THEN 1 ELSE 0 END
        + CASE WHEN tipologia_3 = tipologia_1 THEN 1 ELSE 0 END
        AS md3
    FROM pivoted
    ORDER BY id_alvo
) TO '/var/home/gui/Documentos/saida_11k/saida_11k/output/tabela_top3_pivotada.parquet' (FORMAT PARQUET);
