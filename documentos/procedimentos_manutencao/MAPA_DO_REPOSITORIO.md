# Repository Structure Map — lapig-wribrasil

This document provides a reference map for locating all files, code pipelines, datasets, and web platform components in the repository.

---

## 📁 Directory Tree Overview

```
lapig-wribrasil/
├── README.md                       ← Main repository presentation and documentation
├── LICENSE                         ← Repository license
├── servidor_local.py               ← Local Python server with real-time Liquid/YAML parsing
│
├── 🌐 docs/                        ← Jekyll Site & GitHub Pages Root
│   ├── _config.yml                 ← Jekyll configuration (title, baseurl: "/lapig-wribrasil")
│   ├── index.html                  ← Homepage (Overview, stats, problem, methodology, deliverables)
│   ├── analise-top3/
│   │   └── index.html              ← Page: Md3 Analysis, interactive map, static deliverables & SOM
│   ├── comparacao/
│   │   └── index.html              ← Page: Raster Scenario Comparison (split-map)
│   ├── _layouts/                   ← Base layouts (default.html, page.html)
│   ├── _includes/                  ← Modular UI sections (nav, hero, stats, map_viz, etc.)
│   ├── material_suplementar/       ← Downloadable PDFs (Technical Report & Presentation)
│   └── assets/
│       ├── css/style.css           ← Unified stylesheet (design system, cards, dark/light accents)
│       ├── js/main.js              ← Interactive engine (filters, GPU canvas, box selection, dual charts)
│       ├── tabela_top3_50k_*.json  ← Compact JSON datasets for 50k Series (2019–2025)
│       ├── tabela_top3_12k_*.json  ← Compact JSON datasets for 12k Series (2019–2025)
│       ├── tabela_top3_50k_*.csv   ← Full CSV tables for 50k Series
│       ├── tabela_top3_12k_*.csv   ← Full CSV tables for 12k Series
│       └── embrapa_referencia.json ← Georeferenced dataset for Embrapa's 701 field points
│
├── 📊 dados/                       ← Data and Processing Routines
│   ├── arquivos_base/              ← Input embeddings (annual partitions and Embrapa 701)
│   ├── arquivos_saida/             ← Processed parquet files (50k and 12k Top-3 series)
│   └── scripts/                    ← Python/SQL pipelines:
│       ├── gerar_top3_pivotada_50k.py    ← 50k-Series Top-3 pipeline & export
│       ├── gerar_top3_pivotada_11k.py    ← 12k-Series Top-3 pipeline & export
│       ├── exportar_referencia_embrapa.py← Embrapa 701 points extraction
│       ├── analise_top3_50k.py           ← Statistical analysis routines
│       └── separar_embeddings_por_ano.py ← Temporal partition script
│
└── 📑 documentos/                  ← Technical Documentation & Supplementary Assets
    ├── fluxograma_processamento.md ← Pipeline methodological flowcharts
    ├── formula_md3.md              ← Mathematical specification of Md3 metric
    ├── qgis_cores.qml              ← QGIS color style layer
    ├── campo_md3.pptx              ← Presentation support material
    └── procedimentos_manutencao/   ← Technical maintenance and configuration guides
        ├── GUIA_CONFIGURACAO_E_PAGINAS.md
        ├── GUIA_MANUTENCAO.md
        └── MAPA_DO_REPOSITORIO.md
```

---

## 🎯 Resource Navigation Index

| Objective | File / Location |
| :--- | :--- |
| **Edit Homepage Sections** | `docs/_includes/hero.html`, `docs/_includes/stats.html`, `docs/_includes/timeline.html` |
| **Modify Md3 Map, Filters or Charts** | `docs/_includes/map_viz.html` and `docs/assets/js/main.js` |
| **Update Download Links or Scripts** | `docs/_includes/Produtos_Estaticos.html` |
| **Adjust Visual Styling & CSS** | `docs/assets/css/style.css` |
| **Recompute 50k Series Pipeline** | `dados/scripts/gerar_top3_pivotada_50k.py` |
| **Recompute 12k Series Pipeline** | `dados/scripts/gerar_top3_pivotada_11k.py` |
| **Inspect Embrapa Ground Truth Data** | `docs/assets/embrapa_referencia.json` |
| **Jekyll & GitHub Pages Troubleshooting** | `documentos/procedimentos_manutencao/GUIA_CONFIGURACAO_E_PAGINAS.md` |
