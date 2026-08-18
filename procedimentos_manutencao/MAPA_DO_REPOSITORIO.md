# Mapa da Estrutura do Repositório — WRI_LAPIG

Este documento serve como mapa de referência rápida para localização de todos os arquivos, códigos, dados e páginas do projeto.

---

## 📁 Visão Geral da Árvore de Diretórios

```
WRI_LAPIG/
├── _config.yml                     ← Configurações centrais do Jekyll (título, baseurl)
├── index.html                      ← Página principal (Home)
├── servidor_local.py               ← Servidor local Python para visualização em tempo real (F5)
├── README.md                       ← Apresentação do repositório
│
├── 🌐 PÁGINAS DO SITE (Jekyll / GitHub Pages)
│   ├── analise-top3/
│   │   └── index.html              ← Página: Análise Md3, visualizador dual, produtos estáticos e SOM
│   ├── comparacao/
│   │   └── index.html              ← Página: Comparação de Cenários (split-map raster)
│   ├── _layouts/
│   │   ├── default.html            ← Layout base (head dinâmico, Leaflet, Chart.js, main.js)
│   │   └── page.html               ← Layout de sub-páginas (nav, cabeçalho, botão voltar, footer)
│   ├── _includes/
│   │   ├── nav.html                ← Barra de navegação global
│   │   ├── back_button.html        ← Botão reutilizável "← Voltar para o Início"
│   │   ├── footer.html             ← Rodapé unificado
│   │   ├── hero.html               ← Seção de abertura da Home
│   │   ├── stats.html              ← Painel de estatísticas da Home
│   │   ├── problem.html            ← Seção de contexto e cards da Home
│   │   ├── methodology.html        ← Pipeline metodológico da Home
│   │   ├── deliverables.html       ← Cards de produtos da Home
│   │   ├── timeline.html           ← Cronograma de etapas da Home
│   │   ├── navigation_cards.html   ← Cards com links para as sub-páginas
│   │   ├── classes.html            ← Grid de tipologias de pastagem Embrapa
│   │   ├── map_viz.html            ← Container e painel do mapa Md3 (Série 50k & Série 12k)
│   │   ├── Produtos_Estaticos.html ← Seção de downloads abertos, scripts e assets GEE
│   │   ├── SOM.html                ← Seção de Redes Neurais Auto-Organizáveis (SOM)
│   │   └── map_compare.html        ← Container e painel de comparação lado a lado
│   └── assets/
│       ├── css/
│       │   └── style.css           ← Folha de estilos unificada (design system, cards, tema)
│       ├── js/
│       │   └── main.js             ← Lógica interativa dos mapas, multi-filtro, box-selection e gráficos
│       ├── tabela_top3_50k_*.json  ← Séries JSON compactas da Série 50k (2019 a 2025)
│       ├── tabela_top3_12k_*.json  ← Séries JSON compactas da Série 12k (2019 a 2025)
│       ├── tabela_top3_50k_*.csv   ← Tabelas CSV completas da Série 50k
│       ├── tabela_top3_12k_*.csv   ← Tabelas CSV completas da Série 12k
│       └── embrapa_referencia.json ← Base georreferenciada dos 701 pontos de campo Embrapa
│
├── 🐍 SCRIPTS DE PROCESSAMENTO SÉRIE 50k (`produto_escalar_scripts/`)
│   ├── gerar_top3_pivotada_50k.py  ← Pipeline da Série 50k (produto escalar, Top-3, Md3 e exportações)
│   ├── exportar_referencia_embrapa.py ← Exportador e consolidador dos 701 pontos de campo
│   ├── analise_top3_50k.py         ← Análises estatísticas e distribuições
│   ├── separar_embeddings_por_ano.py ← Divisão temporal dos embeddings de entrada
│   └── rodar_analises.py           ← Orquestrador de execuções
│
├── 🌾 SCRIPTS E DADOS DA SÉRIE 12k (`produto_escalar_11k/`)
│   ├── arquivos_base/              ← Embeddings brutos (Pastagem Col11 + 85k)
│   ├── scripts/
│   │   └── gerar_top3_pivotada_11k.py ← Pipeline da Série 12k com correção de coordenadas
│   ├── docs/                       ← Apresentações, QGIS styles e notas metodológicas
│   └── saida/                      ← Tabelas pivotadas da Série 12k em Parquet e CSV
│
├── 📊 DADOS E MÉTRICAS SÉRIE 50k (`produto_escalar_metricas/`)
│   ├── arquivos_base/              ← Embeddings Sentinel-2 brutos e dados de campo
│   ├── arquivos_saida/             ← Parquets gerados da Série 50k (2019 a 2025)
│   ├── grade/                      ← Grades cartográficas do Brasil (.shp, .parquet)
│   └── visual/                     ← Projetos QGIS, geopackages e camadas visuais
│
└── 📘 DOCUMENTAÇÃO E PROCEDIMENTOS (`procedimentos_manutencao/`)
    ├── GUIA_CONFIGURACAO_E_PAGINAS.md  ← Manual completo de configuração Jekyll e GitHub Pages
    └── MAPA_DO_REPOSITORIO.md          ← Este mapa de referência
```

---

## 🎯 Onde Encontrar Cada Recurso

| Objetivo | Localização |
| :--- | :--- |
| **Editar textos ou seções da Home** | `_includes/hero.html`, `_includes/stats.html`, `_includes/timeline.html` |
| **Modificar os filtros ou mapa Md3** | `_includes/map_viz.html` e `assets/js/main.js` |
| **Atualizar links de download ou scripts** | `_includes/Produtos_Estaticos.html` |
| **Alterar estilos visuais e layout** | `assets/css/style.css` |
| **Reprocessar Série 50k** | `produto_escalar_scripts/gerar_top3_pivotada_50k.py` |
| **Reprocessar Série 12k** | `produto_escalar_11k/scripts/gerar_top3_pivotada_11k.py` |
| **Consultar dados de campo Embrapa** | `assets/embrapa_referencia.json` |
