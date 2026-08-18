# Fluxograma do Pipeline de Processamento (Top-3 Pivotado & Md3)

Este documento descreve o fluxo completo de dados e processamento SQL (DuckDB) utilizado para calcular a similaridade espectral por produto escalar de 64 dimensões e gerar as tabelas Top-3 pivotadas das séries **50k** e **12k** (2019–2025).

---

## Diagrama Geral do Pipeline (Mermaid)

```mermaid
flowchart TD
    subgraph ETAPA_1["1. Bases de Entrada (dados/arquivos_base/)"]
        E["embeddings_embrapa_year_colet.parquet\n(701 pontos de campo Embrapa | Vetores A00..A63)"]
        S50["embeddings_samples_50k_cvp_s2_cerrado_{ano}.parquet\n(50.386 amostras anuais particionadas)"]
        S12["MapBiomas Pastagem Col11 + MapBiomas 85k\n(12.009 amostras anuais filtradas por pastagem)"]
    end

    subgraph ETAPA_2["2. Processamento por Ano (dados/scripts/)"]
        P50["gerar_top3_pivotada_50k.py\n(Cross Join 50k x 701 = ~35,3M combinações/ano)"]
        P12["gerar_top3_pivotada_11k.py\n(Cross Join 12k x 701 = ~8,4M combinações/ano)"]
    end

    subgraph ETAPA_3["3. Produto Escalar de 64 Dimensões"]
        DOT["Produto Escalar: sum(e.A_i * s.A_i) para i=00..63\nRankeamento: ROW_NUMBER() OVER (PARTITION BY id_alvo ORDER BY prod_escalar DESC) <= 3"]
    end

    subgraph ETAPA_4["4. Pivotamento e Métricas Top-3"]
        PIV["Pivotamento em Colunas:\n• target_fid_1..3, prod_escalar_1..3, tipologia_1..3\n• loc_1..3 ('lat_ref, lon_ref')\n• class_embrapa = tipologia_1"]
        MD3["Cálculo das Métricas:\n• Md3 Espectral: (p1 + p2 + p3) / 3.0\n• Concordância Categórica: 1 + (t2==t1) + (t3==t1)"]
    end

    subgraph ETAPA_5["5. Exportação e Publicação"]
        PQ["dados/arquivos_saida/\ntabela_top3_pivotada_{serie}_{ano}.parquet (ZSTD)"]
        CSV["docs/assets/\ntabela_top3_{serie}_{ano}.csv (Download Público)"]
        JSON["docs/assets/\ntabela_top3_{serie}_{ano}.json (Payload Compacto Web)"]
    end

    E & S50 --> P50
    E & S12 --> P12
    P50 & P12 --> DOT
    DOT --> PIV
    PIV --> MD3
    MD3 --> PQ & CSV & JSON
```

---

## Detalhamento das Etapas

1. **Particionamento Temporal**:
   - Os embeddings anuais de 2019 a 2025 são mantidos em arquivos particionados leves (~25 MB cada), permitindo processamento em paralelo com baixo consumo de memória RAM.

2. **Cálculo do Produto Escalar de 64 Dimensões**:
   - Como os vetores de embeddings do modelo de fundação possuem norma unitária, o produto escalar euclidiano $\sum_{i=0}^{63} (A_i^{\text{embrapa}} \times A_i^{\text{amostra}})$ é equivalente à similaridade de cosseno.

3. **Seleção dos Top-3 Matches e Pivotamento**:
   - Para cada pixel-alvo, selecionam-se as 3 amostras de campo mais similares. A tabela é pivotada de formato longo para formato largo com atributos detalhados de cada um dos 3 vizinhos mais próximos.

4. **Geração de Saídas Otimizadas**:
   - **Parquet (ZSTD)**: Armazenamento analítico de alta eficiência para cientistas de dados e QGIS.
   - **CSV**: Compatibilidade universal com planilhas e softwares legados.
   - **JSON Compacto**: Estrutura colunar matricial minimizada para renderização ultrarrápida no Leaflet e Chart.js na plataforma web.
