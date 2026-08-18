--CALCULAR EMBEDDINGS PARA O PRIMEIRO DADO OBTIDO DO MAPBIOMAS
select * from 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\embeddings_avg_mapbiomas_pastagem_2019_2025.parquet' limit 10;

--CALCULAR EMBEDDINGS PARA MAPBIOMAS 85K
select * from 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\embeddings_avg_mapbiomas85k_2019_2025.parquet' limit 100;

--CONTAGEM DE ELEMENTOS
SELECT COUNT(*) AS total_elementos
FROM 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\arquivos_base\mapbiomas_cerrado_pastagem_embeddings_2.parquet';

--EMBEDDINGS MAPBIOMAS FILTER

INSTALL spatial;
LOAD spatial;

COPY (
    SELECT 
        ID_REVISAO AS id,
        year,
        CLASS_2024 AS class_2025,
        A00, A01, A02, A03, A04, A05, A06, A07, A08, A09,
        A10, A11, A12, A13, A14, A15, A16, A17, A18, A19,
        A20, A21, A22, A23, A24, A25, A26, A27, A28, A29,
        A30, A31, A32, A33, A34, A35, A36, A37, A38, A39,
        A40, A41, A42, A43, A44, A45, A46, A47, A48, A49,
        A50, A51, A52, A53, A54, A55, A56, A57, A58, A59,
        A60, A61, A62, A63,
        LAT AS lat,
        LON As lon,
        ".geo"
    FROM 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/embeddings_avg_mapbiomas85k_2019_2025.parquet'
    WHERE year = 2024 
      AND CLASS_2024 = 'PASTAGEM'
) TO 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/arquivos_base/mapbiomas_cerrado_pastagem_embeddings_2.parquet' (FORMAT 'parquet');

--SALVAR E NOMEAR IDs UNICOS
COPY (
    SELECT 
        ROW_NUMBER() OVER () AS id_alvo,
        * 
    FROM (
        SELECT * FROM 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/arquivos_base/mapbiomas_cerrado_pastagem_embeddings_1.parquet'
        UNION ALL
        SELECT * FROM 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/arquivos_base/mapbiomas_cerrado_pastagem_embeddings_2.parquet'
    )
) TO 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/arquivos_base_organizados/mapbiomas_cerrado_pastagem_embeddings_all.parquet' (FORMAT 'parquet');

--ADICIONAR CAMPO DE ANO DE VISITA

COPY (
    SELECT 
        *,
        EXTRACT(YEAR FROM epoch_ms(CAST(data_colet AS BIGINT))) AS year_colet
    FROM 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/embeddings_avg_training_embrapa_2019_2025_v4.csv'
) TO 'C:/Users/windows/Documents/cenargen_trabalho_mult/cenargen_trabalho_mult/saida_11k/embeddings_avg_training_embrapa_2019_2025_v5.parquet' (FORMAT 'parquet');

--INSPECT FEATURE

select * from 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\embeddings_avg_training_embrapa_2019_2025_v5.parquet' limit 1;


--FILTER EMBRAPA DATA
COPY (
    SELECT 
        TARGET_FID,
        Tipologia_,
        TIPOLOGIAc,
        new_class,
        newclassV2,
        year_colet,
        capim,
        lenhosa_co,
        ruderal,
        solo,
        altitude,
        Origem,
        A00, A01, A02, A03, A04, A05, A06, A07, A08, A09,
        A10, A11, A12, A13, A14, A15, A16, A17, A18, A19,
        A20, A21, A22, A23, A24, A25, A26, A27, A28, A29,
        A30, A31, A32, A33, A34, A35, A36, A37, A38, A39,
        A40, A41, A42, A43, A44, A45, A46, A47, A48, A49,
        A50, A51, A52, A53, A54, A55, A56, A57, A58, A59,
        A60, A61, A62, A63,
        latitude AS lat_ref,
        longitude AS lon_ref,
        ".geo"
    FROM 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\embeddings_avg_training_embrapa_2019_2025_v5.parquet'
    WHERE year = year_colet 
) TO 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\arquivos_base_organizados\embeddings_training_embrapa_2025.parquet' (FORMAT 'parquet');

--INSPECT DATA
select * from 'C:\Users\windows\Documents\cenargen_trabalho_mult\cenargen_trabalho_mult\saida_11k\arquivos_base_organizados\embeddings_training_embrapa_2025.parquet' limit 701;