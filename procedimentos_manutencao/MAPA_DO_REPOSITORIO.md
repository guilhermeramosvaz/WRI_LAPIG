# Repository Structure Map — lapig-wribrasil

This document provides a reference map for locating all files, code pipelines, datasets, and web platform components in the repository.

---

## 📁 Directory Tree Overview

```
lapig-wribrasil/
├── _config.yml                     ← Central Jekyll configuration (title, baseurl: "/lapig-wribrasil", exclude list)
├── index.html                      ← Homepage (Overview, stats, problem, methodology, deliverables)
├── servidor_local.py               ← Local Python server with real-time Liquid/YAML parsing
├── README.md                       ← Main repository presentation and documentation
│
├── 🌐 WEB PAGES & COMPONENTS (Jekyll / GitHub Pages)
│   ├── analise-top3/
│   │   └── index.html              ← Page: Md3 Analysis, interactive map, static deliverables & SOM
│   ├── comparacao/
│   │   └── index.html              ← Page: Raster Scenario Comparison (split-map)
│   ├── _layouts/
│   │   ├── default.html            ← Base layout (HTML5, head, Leaflet, Chart.js, main.js)
│   │   └── page.html               ← Sub-page layout (nav, header, back button, footer)
│   ├── _includes/
│   │   ├── nav.html                ← Global navigation bar
│   │   ├── back_button.html        ← Reusable "← Back to Overview" button
│   │   ├── footer.html             ← Unified institutional footer
│   │   ├── hero.html               ← Hero header section
│   │   ├── stats.html              ← Key statistics panel (62,395 annual points · 438k total)
│   │   ├── problem.html            ← Context & rationale cards
│   │   ├── methodology.html        ← Methodological workflow & processing pipeline
│   │   ├── deliverables.html       ← Key products & deliverables cards
│   │   ├── timeline.html           ← Project stages timeline
│   │   ├── navigation_cards.html   ← Navigation cards linking to sub-pages
│   │   ├── classes.html            ← Grid of 7 Embrapa pasture typologies
│   │   ├── map_viz.html            ← Interactive Leaflet map container & filter panel (50k & 12k Series)
│   │   ├── Produtos_Estaticos.html ← Static downloads, reports, scripts & open data tables
│   │   ├── SOM.html                ← Self-Organizing Maps (SOM) section
│   │   └── map_compare.html        ← Side-by-side comparison split-map
│   └── assets/
│       ├── css/
│       │   └── style.css           ← Unified stylesheet (design system, cards, dark/light accents)
│       ├── js/
│       │   └── main.js             ← Interactive engine (reactive filters, GPU canvas, box selection, dual charts)
│       ├── tabela_top3_50k_*.json  ← Compact JSON datasets for 50k Series (2019–2025)
│       ├── tabela_top3_12k_*.json  ← Compact JSON datasets for 12k Series (2019–2025)
│       ├── tabela_top3_50k_*.csv   ← Full CSV tables for 50k Series
│       ├── tabela_top3_12k_*.csv   ← Full CSV tables for 12k Series
│       └── embrapa_referencia.json ← Georeferenced dataset for Embrapa's 701 field reference points
│
├── 🐍 50K SERIES PROCESSING PIPELINE (`produto_escalar_scripts/`)
│   ├── gerar_top3_pivotada_50k.py  ← 50k-Series pipeline (dot product, Top-3 ranking, Md3 metric, exports)
│   ├── exportar_referencia_embrapa.py ← Consolidation of 701 ground-truth points
│   ├── analise_top3_50k.py         ← Statistical analysis and histograms
│   ├── separar_embeddings_por_ano.py ← Temporal partition of input embeddings
│   └── rodar_analises.py           ← Workflow orchestrator
│
├── 🌾 12K SERIES PROCESSING PIPELINE (`produto_escalar_11k/`)
│   ├── arquivos_base/              ← Raw input embeddings (Pasture Col11 + 85k)
│   ├── scripts/
│   │   └── gerar_top3_pivotada_11k.py ← 12k-Series pipeline with coordinate correction
│   ├── docs/                       ← Documentation, QGIS styles and methodological notes
│   └── saida/                      ← Generated Parquets and CSVs for 12k Series (2019–2025)
│
├── 📊 50K SERIES DATA & METRICS (`produto_escalar_metricas/`)
│   ├── arquivos_base/              ← Input embeddings and Embrapa data
│   ├── arquivos_saida/             ← Output Parquets for 50k Series (2019–2025)
│   ├── grade/                      ← Brazilian cartographic grids (.shp, .parquet)
│   └── visual/                     ← QGIS projects and geospatial layers
│
└── 📘 MAINTENANCE & GUIDELINES (`procedimentos_manutencao/`)
    ├── GUIA_CONFIGURACAO_E_PAGINAS.md ← Comprehensive manual for Jekyll, GitHub Pages & troubleshooting
    ├── GUIA_MANUTENCAO.md             ← Quick maintenance reference
    └── MAPA_DO_REPOSITORIO.md         ← This reference map
```

---

## 🎯 Resource Navigation Index

| Objective | File / Location |
| :--- | :--- |
| **Edit Homepage Sections** | `_includes/hero.html`, `_includes/stats.html`, `_includes/timeline.html` |
| **Modify Md3 Map, Filters or Charts** | `_includes/map_viz.html` and `assets/js/main.js` |
| **Update Download Links or Scripts** | `_includes/Produtos_Estaticos.html` |
| **Adjust Visual Styling & CSS** | `assets/css/style.css` |
| **Recompute 50k Series Pipeline** | `produto_escalar_scripts/gerar_top3_pivotada_50k.py` |
| **Recompute 12k Series Pipeline** | `produto_escalar_11k/scripts/gerar_top3_pivotada_11k.py` |
| **Inspect Embrapa Ground Truth Data** | `assets/embrapa_referencia.json` |
| **Jekyll & GitHub Pages Troubleshooting** | `procedimentos_manutencao/GUIA_CONFIGURACAO_E_PAGINAS.md` |
