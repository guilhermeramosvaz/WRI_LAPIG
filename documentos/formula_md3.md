# Especificação das Métricas de Concordância: `Md3` e `score_concordancia`

## 1. Contexto e Conceito

Para cada ponto amostral no Cerrado (`id_alvo`), calculamos o **produto escalar de 64 dimensões** entre seu embedding Sentinel-2 e os embeddings de cada um dos 701 pontos de verdade de campo da Embrapa (`TARGET_FID`).

Dos 701 resultados, selecionamos os **3 maiores valores** de produto escalar — representando as 3 amostras de campo com maior similaridade espectral àquele ponto:
* **Top-1**: Maior produto escalar ($p_1$), classe associada ($t_1$) e ponto de campo ($fid_1$).
* **Top-2**: Segundo maior produto escalar ($p_2$), classe associada ($t_2$) e ponto de campo ($fid_2$).
* **Top-3**: Terceiro maior produto escalar ($p_3$), classe associada ($t_3$) e ponto de campo ($fid_3$).

A partir desse trio, derivamos duas métricas complementares:
1. **Md3 Espectral (Contínuo)**: Média aritmética dos 3 maiores produtos escalares.
2. **Score de Concordância Categórica (Discreto 1..3)**: Nível de concordância entre as tipologias de campo dos 3 vizinhos mais próximos.

---

## 2. Fórmulas Matemáticas

### A. Métrica Espectral: `Md3`
O `Md3` reflete a intensidade média de similaridade espectral das 3 amostras de campo mais próximas no espaço latente de 64 dimensões:

$$
\text{Md3} = \frac{p_1 + p_2 + p_3}{3}
$$

Em SQL (DuckDB):
```sql
ROUND((prod_escalar_1 + prod_escalar_2 + prod_escalar_3) / 3.0, 4) AS md3
```

* **Interpretação**:
  * $\text{Md3} \ge 0.85$: Similaridade espectral altíssima com a verdade de campo.
  * $0.70 \le \text{Md3} < 0.85$: Boa representatividade espectral.
  * $\text{Md3} < 0.70$: Assinatura espectral atípica ou com baixa proximidade aos pontos de campo cadastrados.

---

### B. Métrica Categórica: `score_concordancia`
Mede se as 3 amostras mais similares pertencem à mesma classe tipológica atribuída pelo top-1:

$$
\text{score\_concordancia} = 1 + \mathbb{1}[t_2 = t_1] + \mathbb{1}[t_3 = t_1]
$$

Onde $\mathbb{1}[\cdot]$ é a função indicadora (vale 1 se a condição for verdadeira, 0 caso contrário).

Em SQL (DuckDB):
```sql
(1 
 + CASE WHEN tipologia_c_2 = tipologia_c_1 THEN 1 ELSE 0 END 
 + CASE WHEN tipologia_c_3 = tipologia_c_1 THEN 1 ELSE 0 END
) AS score_concordancia
```

---

## 3. Matriz de Interpretação da Concordância Categórica

| Score | Concordância | Nível de Certeza | Descrição |
| :---: | :---: | :---: | :--- |
| **3** | $t_1 = t_2 = t_3$ | **Alta Confiança** | Todos os 3 vizinhos espectrais mais próximos pertencem exatamente à mesma tipologia. |
| **2** | $t_2 = t_1 \lor t_3 = t_1$ | **Confiança Moderada** | 2 dos 3 vizinhos espectrais concordam na mesma tipologia. |
| **1** | $t_2 \ne t_1 \land t_3 \ne t_1$ | **Baixa Confiança** | Apenas o top-1 possui essa tipologia; o 2º e o 3º vizinhos pertencem a outras classes. |

---

## 4. Exemplo Numérico

Considere uma amostra onde os 3 melhores matches são:

| Ranking | TARGET_FID | Produto Escalar | Tipologia Padronizada |
| :---: | :---: | :---: | :--- |
| **1º (Top-1)** | 342 | 0.942 | `PASTO PRODUTIVO` |
| **2º (Top-2)** | 118 | 0.920 | `PASTO PRODUTIVO` |
| **3º (Top-3)** | 507 | 0.886 | `PASTO COM ERVAS` |

* **Classe Atribuída**: `PASTO PRODUTIVO`
* **Md3 Espectral**: $\frac{0.942 + 0.920 + 0.886}{3} = \mathbf{0.9160}$
* **Score de Concordância**: $1 + 1 (\text{Top-2}) + 0 (\text{Top-3}) = \mathbf{2}$
