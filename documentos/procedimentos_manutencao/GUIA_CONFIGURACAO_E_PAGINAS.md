# Guia de Configuração, Jekyll e Criação de Páginas — lapig-wribrasil

Este manual ensina como a plataforma web foi construída, como o **GitHub Pages (`github.io`)** interpreta a pasta `docs/`, como rodar localmente e o passo a passo para **adicionar novas páginas, seções e dados**, além de como evitar erros de compilação no Jekyll.

---

## 1. Arquitetura do Site (`docs/`)

Todo o código-fonte da plataforma web reside na pasta `docs/`, que funciona como a raiz do Jekyll para o GitHub Pages:

```
docs/
├── _config.yml                 ← Configurações centrais do Jekyll (título, baseurl: "/lapig-wribrasil")
├── index.html                  ← Página inicial (Overview, estatísticas, contexto, metodologia)
├── analise-top3/
│   └── index.html              ← Sub-página: Análise Md3, mapa Leaflet, entregáveis e SOM
├── comparacao/
│   └── index.html              ← Sub-página: Comparação de Cenários (Split-map)
├── _layouts/
│   ├── default.html            ← Layout base (head, CSS, Leaflet, Chart.js, main.js)
│   └── page.html               ← Layout de sub-páginas (nav, título, botão voltar, footer)
├── _includes/                  ← Blocos HTML modulares e reutilizáveis
│   ├── nav.html                ← Barra de navegação global
│   ├── hero.html               ← Cabeçalho principal
│   ├── stats.html              ← Painel de métricas (62.395 amostras/ano)
│   ├── map_viz.html            ← Container do mapa interativo e filtros
│   ├── Produtos_Estaticos.html ← Seção de downloads e dados abertos
│   ├── SOM.html                ← Seção de mapas auto-organizáveis
│   ├── footer.html             ← Rodapé unificado
│   └── back_button.html        ← Botão de retorno para a Home
├── material_suplementar/       ← PDFs disponíveis para download público
│   ├── Report_Product_1_WRI_LAPIG_20260817_EN.pdf
│   └── Scaling_Ground_Truth_wribrasil.pdf
└── assets/
    ├── css/style.css           ← Folha de estilo unificada e responsiva
    ├── js/main.js              ← Mecanismo interativo (filtros reativos, renderização em canvas, gráficos)
    ├── tabela_top3_50k_*.json  ← Datasets compactos da Série 50k (2019–2025)
    ├── tabela_top3_12k_*.json  ← Datasets compactos da Série 12k (2019–2025)
    ├── tabela_top3_50k_*.csv   ← Tabelas completas em CSV
    └── embrapa_referencia.json ← Georreferenciamento dos 701 pontos de campo Embrapa
```

---

## 2. Como Configurar o GitHub Pages no Repositório

Para servir o site no endereço oficial do GitHub Pages:

1. No repositório GitHub (`lapig-ufg/lapig-wribrasil`):
2. Acesse **Settings** → **Pages** (na barra lateral esquerda).
3. Na seção **Build and deployment**:
   * **Source**: Escolha `Deploy from a branch`
   * **Branch**: Selecione `main`
   * **Folder**: Selecione **/docs**
   * Clique em **Save**.
4. Em cerca de 1 a 2 minutos o site estará online no link oficial:  
   👉 **`https://lapig-ufg.github.io/lapig-wribrasil/`**

---

## 3. O Filtro `relative_url` e URLs Dinâmicas

Como o repositório roda sob o subdomínio e subcaminho `/lapig-wribrasil/`, todas as rotas internas, imagens e estilos utilizam o filtro Liquid `relative_url`:

{% raw %}
```html
<!-- Links de Páginas -->
<a href="{{ '/analise-top3/' | relative_url }}">Análise Top-3</a>

<!-- Folhas de Estilo e Imagens -->
<link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">
<img src="{{ '/assets/figures/wri_brasil_logo.svg' | relative_url }}" alt="Logo">
```
{% endraw %}

No JavaScript (`docs/assets/js/main.js`), as chamadas `fetch` utilizam a variável injetada pelo Jekyll no `_layouts/default.html`:
```javascript
const baseUrl = window.siteBaseUrl || '';
const url = `${baseUrl}/assets/tabela_top3_${currentDataset}_${year}.json`;
```

---

## 4. Passo a Passo: Como Criar uma Nova Sub-página

Se precisar adicionar uma nova página (ex: `/nova-analise/`):

### Passo 1: Criar a pasta e o `index.html` em `docs/`
Crie `docs/nova-analise/index.html`:
{% raw %}
```html
---
layout: page
title: Nova Análise Geoespacial
page_eyebrow: Análises Complementares
page_desc: Descrição detalhada dos novos resultados e processamentos.
---

{% include nova_secao.html %}
```
{% endraw %}

### Passo 2: Criar o bloco em `docs/_includes/`
Crie `docs/_includes/nova_secao.html` com a estrutura HTML da nova seção.

### Passo 3: Adicionar no Menu de Navegação
Edite `docs/_includes/nav.html` e adicione o link:
{% raw %}
```html
<li><a href="{{ '/nova-analise/' | relative_url }}">Nova Análise</a></li>
```
{% endraw %}

---

## 5. Como Executar e Testar Localmente

Para rodar e testar tudo no seu computador sem precisar instalar Ruby ou Jekyll:

1. Execute o script na raiz do projeto:
   ```bash
   python servidor_local.py
   ```
2. Abra no navegador:
   * **Home:** `http://localhost:8000/`
   * **Análise Top-3:** `http://localhost:8000/analise-top3/`
   * **Comparação:** `http://localhost:8000/comparacao/`
3. Qualquer alteração nos arquivos HTML, CSS ou JS é refletida imediatamente ao recarregar a página (**F5**).

---

## 6. Boas Práticas e Prevenção de Erros de Build

* **Exemplos Liquid em Markdown**: Se escrever tags de template (como `{% include %}`) em manuais ou arquivos `.md`, sempre envolva com `{% raw %}` e `{% endraw %}` para não quebrar o motor do Jekyll.
* **Isolamento de Pastas**: Mantendo todo o site dentro de `docs/`, arquivos pesados ou rotinas de cálculo em `dados/` e `documentos/` ficam completamente separados e protegidos de falhas de compilação web.
