# Guia de Configuração, Jekyll e Criação de Páginas

Este manual ensina como o site foi construído, como o **GitHub Pages (`github.io`)** interpreta os arquivos, como rodar localmente e o passo a passo para **adicionar novas páginas, seções e dados**.

---

## 1. Como Funciona a Arquitetura Jekyll

O site utiliza o **Jekyll**, o motor de sites estáticos oficial e nativo do GitHub Pages. A estrutura é modular e dividida em três pilares:

### A. Layouts (`_layouts/`)
* **`default.html`**: É a casca base de todo o site. Contém as tags `<head>`, importações de fontes (Google Fonts), Leaflet CSS/JS, Chart.js, a folha de estilo `style.css` e o arquivo de scripts `main.js`.
* **`page.html`**: É o layout padrão para **sub-páginas**. Ele herda de `default.html` (`layout: default`) e injeta automaticamente a barra de navegação (`nav.html`), o botão voltar (`back_button.html`), o cabeçalho com título da página e o rodapé (`footer.html`).

### B. Includes (`_includes/`)
São blocos HTML reutilizáveis. Em vez de escrever um arquivo gigantesco, cada seção do site é um include separado:
* `hero.html` → Seção de destaque inicial
* `stats.html` → Métricas e números
* `problem.html` → Contexto e justificativa
* `methodology.html` → Pipeline de processamento
* `classes.html` → Tipologias de pastagem Embrapa
* `map_viz.html` → Mapa interativo Md3
* `map_compare.html` → Split-map de comparação de cenários
* `Produtos_Estaticos.html` → Seção de downloads abertos
* `SOM.html` → Seção de mapas auto-organizáveis
* `deliverables.html` → Cards de produtos
* `timeline.html` → Cronograma de etapas
* `navigation_cards.html` → Cards de navegação para as sub-páginas
* `nav.html` → Menu global
* `footer.html` → Rodapé global
* `back_button.html` → Botão de retorno para a Home

### C. Páginas (`index.html`, `analise-top3/index.html`, etc.)
Cada página é um arquivo `.html` que define no topo um bloco de metadados chamado **Frontmatter YAML**:
{% raw %}
```yaml
---
layout: page
title: Nome da Minha Página
page_eyebrow: Categoria da Página
page_desc: Descrição breve do conteúdo apresentado nesta página.
---

{% include meu_conteudo.html %}
```
{% endraw %}

---

## 2. Como o GitHub Pages (`github.io`) Reconhece o Site

Quando você envia o código para o GitHub (`git push origin main`), o GitHub Pages executa o Jekyll automaticamente:

1. **Geração de URLs Limpas**:
   * O arquivo `index.html` na raiz se torna: `https://usuario.github.io/WRI_LAPIG/`
   * A pasta `analise-top3/index.html` se torna: `https://usuario.github.io/WRI_LAPIG/analise-top3/`
   * A pasta `comparacao/index.html` se torna: `https://usuario.github.io/WRI_LAPIG/comparacao/`

2. **O Filtro `relative_url`**:
   * Como o site no GitHub Pages roda sob o subcaminho do repositório (ex: `/WRI_LAPIG/`), todos os links, imagens e estilos utilizam o filtro Liquid:
     {% raw %}
     ```html
     {{ '/analise-top3/' | relative_url }}
     {{ '/assets/css/style.css' | relative_url }}
     ```
     {% endraw %}
   * O Jekyll substitui isso automaticamente para `/WRI_LAPIG/analise-top3/` no GitHub, e para `/analise-top3/` localmente.

3. **Integração com o JavaScript (`main.js`)**:
   * No `_layouts/default.html`, injetamos a variável:
     {% raw %}
     ```html
     <script>
       window.siteBaseUrl = "{{ '' | relative_url }}";
     </script>
     ```
     {% endraw %}
   * No `assets/js/main.js`, as requisições `fetch` para carregar arquivos JSON usam essa variável base:
     ```javascript
     const baseUrl = window.siteBaseUrl || '';
     const url = `${baseUrl}/assets/tabela_top3_50k_${year}.json`;
     ```
   * Isso garante que os mapas encontrem os dados JSON tanto na Home quanto dentro de sub-pastas como `/analise-top3/`.

---

## 3. Configuração do `_config.yml`

O arquivo [`_config.yml`](file:///C:/Users/windows/Documents/github/WRI_LAPIG/_config.yml) na raiz do projeto controla as propriedades globais:

```yaml
title: Pasture Mapping — WRI Brasil & LAPIG/UFG
description: Mapping, Analysis, and Spectral Similarity Platform for Cerrado Pastures (2019–2025)
baseurl: "/WRI_LAPIG"
url: "https://guilhermeramosvaz.github.io"
```

---

## 4. Passo a Passo: Como Adicionar uma Nova Sub-página

Para criar uma nova página independente (ex: `/nova-metodologia/`):

### Passo 1: Criar a pasta e o arquivo `index.html`
Crie uma pasta com o nome da rota e um `index.html` dentro dela (ex: `nova-metodologia/index.html`):
{% raw %}
```html
---
layout: page
title: Nova Metodologia de Mapeamento
page_eyebrow: Metodologia e Modelagem
page_desc: Detalhamento da nova metodologia de classificação aplicada ao projeto.
---

{% include nova_secao.html %}
```
{% endraw %}

### Passo 2: (Opcional) Criar o Include com o Conteúdo
Crie o arquivo `_includes/nova_secao.html` contendo o HTML da sua seção.

### Passo 3: Adicionar o Link no Menu de Navegação
Edite `_includes/nav.html` e adicione o item:
{% raw %}
```html
<li><a href="{{ '/nova-metodologia/' | relative_url }}">Nova Metodologia</a></li>
```
{% endraw %}

### Passo 4: (Opcional) Adicionar um Card na Home
Em `_includes/navigation_cards.html`, adicione um card de acesso:
{% raw %}
```html
<a class="card fade-up" href="{{ '/nova-metodologia/' | relative_url }}">
  <div class="card__eyebrow">Metodologia</div>
  <div class="card__title">Nova Metodologia</div>
  <p class="card__desc">Descrição resumida do que o usuário encontrará na página.</p>
  <span class="card__arrow">Acessar página →</span>
</a>
```
{% endraw %}

---

## 5. Como Executar e Testar Localmente

Você pode visualizar e testar o site em tempo real sem precisar instalar Ruby ou Jekyll:

1. Abra o terminal na pasta do projeto:
   ```bash
   python servidor_local.py
   ```
2. O servidor iniciará em `http://localhost:8000`.
3. Todas as alterações feitas nos arquivos `.html`, `_includes/`, `_layouts/`, `style.css` ou `main.js` são atualizadas imediatamente ao recarregar a página no navegador (**F5**).

---

## 6. Publicando Alterações no GitHub Pages

Após testar localmente:
```bash
git add .
git commit -m "Fix jekyll build config"
git push origin main
```
O GitHub Pages atualizará o site automaticamente em cerca de 1 a 2 minutos.
