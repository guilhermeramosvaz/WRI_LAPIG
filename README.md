# Caracterização e Mapeamento de Pastagens no Cerrado com Embeddings Espectrais (Sentinel-2)

Repositório institucional de dados, rotinas de processamento de alto desempenho (DuckDB / Python) e plataforma web interativa desenvolvida em cooperação técnica entre **LAPIG/UFG**, **WRI Brasil** e **Embrapa**.

---

## 📊 Síntese dos Dados e Séries Amostrais

A plataforma integra **438.200 amostras MapBiomas** processadas ao longo de uma série histórica de 7 anos (2019 a 2025), cruzadas via **produto escalar de 64 dimensões** com os **701 pontos de verdade de campo da Embrapa**:

| Série Amostral | Descrição e Estratificação | Amostras / Ano (2025) | Total Série Histórica (2019–2025) |
| :--- | :--- | :--- | :--- |
| **Série 50k** | Amostragem aleatória estratificada pela Condição de Vigor da Pastagem (CVP) | **50.000** | **350.000** |
| **Série 12k** | União filtrada por pastagem: MapBiomas Pastagem (Col. 11) + MapBiomas 85k | **12.395** | **88.200** |
| **Total Combinado** | Cobertura integrada sobre o bioma Cerrado | **62.395** | **438.200** |
| **Referência Embrapa** | Verdade de campo coletada in situ com 7 tipologias canônicas | **701** | **701** |

### Distribuição Exata da Série 12k por Ano:
* **2019**: 12.892 pontos
* **2020**: 12.792 pontos
* **2021**: 12.681 pontos
* **2022**: 12.548 pontos
* **2023**: 12.470 pontos
* **2024**: 12.422 pontos
* **2025**: 12.395 pontos

---

## 🌐 Plataforma Web Interativa

Construída sobre arquitetura estática modular (compatível com Jekyll e GitHub Pages) com renderização GPU no navegador via **Leaflet Canvas Markers** e gráficos dinâmicos via **Chart.js**:

* **Página Principal (`/`)**: Visão geral institucional, objetivos, números-chave e links de navegação.
* **Análise Md3 (`/analise-top3/`)**:
  * **Painel de Filtros Unificado**: Alternância instantânea entre a **Série 50k** e a **Série 12k**, seleção de ano (2019 a 2025), filtragem por vigor CVP (1, 2, 3), threshold de similaridade Md3 (0.00 a 0.95), busca textual e filtro de tipologias.
  * **Seleção Retangular Espacial (Box Selection)**: Ferramenta para selecionar dinamicamente qualquer região geográfica do Cerrado e atualizar imediatamente contadores, gráficos e tabela de amostras.
  * **Dual Charts Sincronizados**: Gráfico 1 (Distribuição amostral MapBiomas no recorte ativo) e Gráfico 2 (Distribuição fixa da verdade de campo Embrapa - 701 pontos).
  * **Tabela de Detalhamento**: Visualização dos 3 maiores produtos escalares, IDs de referência, coordenadas e tipologias associadas.
  * **Produtos Estáticos**: Downloads diretos de Relatórios, Apresentações, Assets GEE, Scripts e Tabelas nos formatos Parquet, CSV e JSON.
  * **SOM (Self-Organizing Maps)**: Seção dedicada para agrupamento por redes neurais não supervisionadas.

---

## 📁 Estrutura de Diretórios do Repositório

```
WRI_LAPIG/
├── _includes/                     # Componentes modulares HTML
│   ├── map_viz.html               # Visualizador do mapa Leaflet, GPU canvas e painel de filtros
│   ├── Produtos_Estaticos.html    # Seção de downloads abertos, scripts e assets GEE
│   ├── SOM.html                   # Seção de Redes Neurais Auto-Organizáveis (SOM)
│   ├── navigation_cards.html      # Cards de navegação da página inicial
│   ├── stats.html                 # Seção de estatísticas e números-chave
│   ├── hero.html / footer.html    # Cabeçalho e rodapé institucionais
│   └── timeline.html              # Cronograma metodológico
├── _layouts/                      # Layouts base Jekyll (default.html)
├── analise-top3/                  # Página da Análise Md3 e Produtos Estáticos
│   └── index.html
├── assets/                        # Assets estáticos servidos pela aplicação
│   ├── css/style.css              # Design system completo, responsivo e temas
│   ├── js/main.js                 # Engine de filtros reativos, box selection e dual charts
│   ├── tabela_top3_50k_{ano}.json # Dados compactos da Série 50k (2019 a 2025)
│   ├── tabela_top3_12k_{ano}.json # Dados compactos da Série 12k (2019 a 2025)
│   ├── tabela_top3_50k_{ano}.csv  # CSVs completos da Série 50k para download
│   ├── tabela_top3_12k_{ano}.csv  # CSVs completos da Série 12k para download
│   └── embrapa_referencia.json    # Dados georreferenciados dos 701 pontos Embrapa
├── produto_escalar_scripts/       # Scripts Python/DuckDB para a Série 50k
│   ├── gerar_top3_pivotada_50k.py # Pipeline de produto escalar e Top-3 da Série 50k
│   ├── exportar_referencia_embrapa.py # Exportador da base de referência Embrapa
│   └── analise_top3_50k.py        # Análises estatísticas e histogramas
├── produto_escalar_11k/           # Pipeline e dados da Série 12k (Pastagem + 85k)
│   ├── arquivos_base/             # Parquets brutos de entrada
│   ├── scripts/                   # Scripts de processamento e consultas SQL DuckDB
│   │   └── gerar_top3_pivotada_11k.py # Gerador unificado multi-ano com correção de coordenadas
│   └── saida/                     # Parquets e CSVs gerados (2019 a 2025)
├── produto_escalar_metricas/      # Parquets de saída e matrizes da Série 50k
│   ├── arquivos_base/             # Embeddings de entrada e Embrapa
│   └── arquivos_saida/            # Tabelas Top-3 pivotadas 50k (.parquet)
├── procedimentos_manutencao/      # Manuais de manutenção e mapas de arquitetura
└── servidor_local.py              # Servidor HTTP local multi-página com parser Liquid/YAML
```

---

## 🚀 Como Executar o Servidor Local

Para visualizar a plataforma web localmente em tempo real:

```bash
python servidor_local.py
```

Abra no navegador: **`http://localhost:8000`** ou **`http://localhost:8000/analise-top3/`**.

---

## 🛠️ Como Reproduzir o Processamento de Dados

### 1. Gerar Tabelas Top-3 da Série 50k (2019–2025)
```bash
python produto_escalar_scripts/gerar_top3_pivotada_50k.py --year all
```

### 2. Gerar Tabelas Top-3 da Série 12k (2019–2025)
```bash
python produto_escalar_11k/scripts/gerar_top3_pivotada_11k.py --year all
```

### 3. Atualizar Dados de Referência Embrapa (701 Pontos)
```bash
python produto_escalar_scripts/exportar_referencia_embrapa.py
```

---

## 📜 Tipologias Canônicas de Pastagem (Embrapa)

As amostras de campo e as predições por similaridade espectral são classificadas em 7 categorias principais:
1. **PASTO PRODUTIVO** (`#22c55e`): Pastagem bem manejada com alta biomassa forrageira.
2. **PASTO COM ERVAS** (`#f59e0b`): Pastagem com infestação de espécies herbáceas ruderais.
3. **PASTO COM LENHOSAS** (`#84cc16`): Pastagem com presença de arbustos e invasoras lenhosas.
4. **INTERMEDIARIO** (`#eab308`): Pastagem em condição intermediária de vigor/cobertura.
5. **DEG BIOLOGICA** (`#ef4444`): Degradação biológica acentuada com presença de solo exposto.
6. **REG NATURAL** (`#10b981`): Áreas de pastagem em regeneração natural da vegetação nativa.
7. **MISCELANEA** (`#a855f7`): Outras feições territoriais e usos associados.

---

## 🤝 Instituições Parceiras
* **LAPIG / UFG** — Laboratório de Processamento de Imagens e Geoprocessamento (Universidade Federal de Goiás)
* **WRI Brasil** — World Resources Institute Brasil
* **Embrapa** — Empresa Brasileira de Pesquisa Agropecuária
