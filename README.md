# Characterization and Mapping of Cerrado Pastures with Spectral Embeddings (Sentinel-2)

Institutional repository containing data, high-performance analytical pipelines (DuckDB / Python), and an interactive web platform developed through technical cooperation between **LAPIG/UFG**, **WRI Brasil**, and **Embrapa**.

---

## 📊 Summary of Datasets & Sample Series

The platform integrates **438,200 MapBiomas samples** across a 7-year historical series (2019 to 2025), matched via **64-dimensional dot product** against Embrapa's **701 in situ ground-truth reference points**:

| Sample Series | Description & Stratification | Samples / Year (2025) | Historical Series Total (2019–2025) |
| :--- | :--- | :--- | :--- |
| **50k Series** | Stratified random sampling based on Pasture Vigor Condition (CVP) | **50,000** | **350,000** |
| **12k Series** | Pasture-filtered union: MapBiomas Pasture (Col. 11) + MapBiomas 85k | **12,395** | **88,200** |
| **Combined Total** | Comprehensive spatial coverage across the Cerrado biome | **62,395** | **438,200** |
| **Embrapa Reference** | In situ ground-truth reference points classified into 7 canonical typologies | **701** | **701** |

### Annual Breakdown of the 12k Series:
* **2019**: 12,892 points
* **2020**: 12,792 points
* **2021**: 12,681 points
* **2022**: 12,548 points
* **2023**: 12,470 points
* **2024**: 12,422 points
* **2025**: 12,395 points

---

## 🌐 Interactive Web Platform

Built upon a lightweight, modular static architecture (compatible with Jekyll and GitHub Pages) featuring browser GPU acceleration via **Leaflet Canvas Markers** and dynamic charts via **Chart.js**:

* **Home Page (`/`)**: Institutional overview, objectives, key figures, and section navigation.
* **Md3 Analysis (`/analise-top3/`)**:
  * **Unified Filter Panel**: Instant switching between the **50k Series** and the **12k Series**, year selection (2019 to 2025), pasture vigor filtering (CVP 1, 2, 3), Md3 similarity thresholds (0.00 to 0.95), full-text search, and typology checkboxes.
  * **Spatial Bounding Box Selection**: Tool to interactively select any custom geographic bounding box across the Cerrado, automatically updating counters, charts, and sample inspection tables.
  * **Synchronized Dual Charts**: Chart 1 (Dynamic MapBiomas sample distribution in the active view) and Chart 2 (Fixed distribution of Embrapa's 701 ground-truth points).
  * **Detailed Table**: Inspection of Top-3 dot products, reference FIDs, target coordinates, and assigned typologies.
  * **Static Deliverables**: Direct downloads of technical Reports, Presentation decks, GEE Assets, Python scripts, and Open Data tables in Parquet, CSV, and JSON formats.
  * **SOM (Self-Organizing Maps)**: Section dedicated to unsupervised topological neural network clustering.

---

## 📁 Repository Directory Structure

```
WRI_LAPIG/
├── _includes/                     # Modular HTML components
│   ├── map_viz.html               # Leaflet map viewer, GPU canvas & unified filter panel
│   ├── Produtos_Estaticos.html    # Static deliverables, scripts & GEE assets
│   ├── SOM.html                   # Self-Organizing Maps (SOM) section
│   ├── navigation_cards.html      # Homepage navigation cards
│   ├── stats.html                 # Key metrics & statistics counters
│   ├── hero.html / footer.html    # Institutional header & footer
│   └── timeline.html              # Methodological timeline
├── _layouts/                      # Jekyll base layouts (default.html, page.html)
├── analise-top3/                  # Md3 Analysis & Static Deliverables page
│   └── index.html
├── assets/                        # Static web assets
│   ├── css/style.css              # Design system, theme & responsive layout
│   ├── js/main.js                 # Reactive filters engine, bounding box & dual charts
│   ├── tabela_top3_50k_{year}.json# Compact JSONs for the 50k Series (2019 to 2025)
│   ├── tabela_top3_12k_{year}.json# Compact JSONs for the 12k Series (2019 to 2025)
│   ├── tabela_top3_50k_{year}.csv # Full CSVs for the 50k Series
│   ├── tabela_top3_12k_{year}.csv # Full CSVs for the 12k Series
│   └── embrapa_referencia.json    # Georeferenced data of Embrapa's 701 field points
├── produto_escalar_scripts/       # Python/DuckDB pipelines for the 50k Series
│   ├── gerar_top3_pivotada_50k.py # Dot-product & Top-3 generator for the 50k Series
│   ├── exportar_referencia_embrapa.py # Exporter for Embrapa ground-truth points
│   └── analise_top3_50k.py        # Statistical metrics & distributions
├── produto_escalar_11k/           # Pipeline & data for the 12k Series (Pasture + 85k)
│   ├── arquivos_base/             # Raw input Parquets
│   ├── scripts/                   # DuckDB SQL and processing scripts
│   │   └── gerar_top3_pivotada_11k.py # Multi-year generator with coordinate correction
│   └── saida/                     # Output Parquets and CSVs (2019 to 2025)
├── produto_escalar_metricas/      # Output Parquets and matrices for the 50k Series
│   ├── arquivos_base/             # Sentinel-2 input embeddings and Embrapa data
│   └── arquivos_saida/            # Pivoted Top-3 Parquets
├── procedimentos_manutencao/      # Maintenance manuals and architecture maps
└── servidor_local.py              # Local multi-page HTTP server with Liquid/YAML parsing
```

---

## 🚀 How to Run the Local Server

To preview the web platform locally in real time:

```bash
python servidor_local.py
```

Open in your browser: **`http://localhost:8000`** or **`http://localhost:8000/analise-top3/`**.

---

## 🛠️ Reproducing Data Pipelines

### 1. Generate Top-3 Tables for the 50k Series (2019–2025)
```bash
python produto_escalar_scripts/gerar_top3_pivotada_50k.py --year all
```

### 2. Generate Top-3 Tables for the 12k Series (2019–2025)
```bash
python produto_escalar_11k/scripts/gerar_top3_pivotada_11k.py --year all
```

### 3. Update Embrapa Reference Dataset (701 Points)
```bash
python produto_escalar_scripts/exportar_referencia_embrapa.py
```

---

## 🌿 Canonical Pasture Typologies (Embrapa)

Ground-truth samples and spectral similarity predictions are categorized into 7 primary classes:
1. **Productive Pasture** (`#faea40`): Well-managed pasture with high forage biomass.
2. **Pasture with Weeds** (`#d8ff6c`): Infestation of herbaceous/ruderal invasive plants.
3. **Pasture with Shrubs / Woody Species** (`#66c600`): Significant presence of shrub and tree canopy layers.
4. **Intermediate Pasture** (`#f4b346`): Moderate vegetative vigor with mixed grass and soil coverage.
5. **Biological Degradation** (`#813209`): Severe degradation with prominent bare soil.
6. **Natural Regeneration** (`#0e5f0e`): Areas undergoing natural recovery of native Cerrado vegetation.
7. **Miscellaneous** (`#ec2b10`): Atypical, transitional, or mixed land-use features.

---

## 🤝 Partner Institutions
* **LAPIG / UFG** — Image Processing and Geoprocessing Laboratory (Federal University of Goiás)
* **WRI Brasil** — World Resources Institute Brasil
* **Embrapa** — Brazilian Agricultural Research Corporation

---

## 📄 License

This work, including all code, datasets, documentation, and web assets, is licensed under a **[Creative Commons Attribution 4.0 International License (CC BY 4.0)](file:///C:/Users/windows/Documents/github/WRI_LAPIG/LICENSE)**.
