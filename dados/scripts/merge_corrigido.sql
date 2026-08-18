-- 1. Ative a extensão espacial (se ainda não estiver ativa na sessão)
INSTALL spatial;
LOAD spatial;

-- Força a ordem das coordenadas para [Longitude, Latitude] para evitar inversão
SET geometry_always_xy = true;

-- 2. Execute a cópia mesclando os dados
COPY (
    SELECT 
        -- 1. Colunas onde as linhas foram preenchidas em partes diferentes (Mescladas com COALESCE)
        COALESCE(t1.IDs, t2.IDs) AS IDs,
        COALESCE(t1.tipo_amostra, t2.tipo_amostra) AS tipo_amostra,
        COALESCE(t1.tipo_integ, t2.tipo_integ) AS tipo_integ,
        COALESCE(t1."1_cult_ini", t2."1_cult_ini") AS "1_cult_ini",
        COALESCE(t1."1_cult_fim", t2."1_cult_fim") AS "1_cult_fim",
        COALESCE(t1."2_cult_ini", t2."2_cult_ini") AS "2_cult_ini",
        COALESCE(t1."2_cult_fim", t2."2_cult_fim") AS "2_cult_fim",
        COALESCE(t1.pasture_in, t2.pasture_in) AS pasture_in,
        COALESCE(t1.pasture_fi, t2.pasture_fi) AS pasture_fi,
        COALESCE(t1.geom, t2.geom) AS geom,

        -- 2. O atalho: pega todo o resto do primeiro arquivo (t1),
        -- ignorando as colunas já mescladas na mão acima e o fid
        -- (o fid original é excluído para não conflitar com o fid
        -- que o próprio driver GPKG gera na exportação)
        t1.* EXCLUDE (
            fid,
            IDs, tipo_amostra, tipo_integ, 
            "1_cult_ini", "1_cult_fim", 
            "2_cult_ini", "2_cult_fim", 
            pasture_in, pasture_fi, geom
        )

    -- Lê o primeiro arquivo
    FROM st_read('/var/home/gui/Documentos/ilpf/sem_sobreposicao_ordenado_4326_merged.gpkg') t1

    -- Faz a junção total (FULL OUTER JOIN) com o segundo arquivo com base no campo IDs
    -- CORREÇÃO AQUI: removida a aspa extra no final do caminho
    FULL OUTER JOIN st_read('/var/home/gui/Documentos/ilpf/sem_sobreposicao_ordenado_4326_v_poli.gpkg') t2 
      ON t1.IDs = t2.IDs

    -- 3. O ajuste que resolve o excesso de linhas:
    -- descarta as feições "fantasma" (sem ID em nenhum dos dois arquivos),
    -- que antes sobravam sem par no FULL OUTER JOIN (NULL nunca é igual a NULL)
    -- e viravam linhas extras e duplicadas na saída.
    WHERE COALESCE(t1.IDs, t2.IDs) IS NOT NULL

-- Exporta com o nome final limpo, usando o driver GDAL para GeoPackage
-- CORREÇÃO AQUI: FORMAT GDAL sem aspas
) TO '/var/home/gui/Documentos/ilpf/amostras_ilpf_inspecionadas_4326.gpkg' 
WITH (FORMAT GDAL, DRIVER 'GPKG');