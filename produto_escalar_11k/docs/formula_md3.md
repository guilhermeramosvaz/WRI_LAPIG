# Campo `md3` — Métrica de Concordância dos 3 Melhores Matches

## Contexto

Para cada ponto do MapBiomas (`id_alvo`), calculamos o **produto escalar** entre seu embedding e o embedding de cada uma das 701 amostras de campo da Embrapa (`TARGET_FID`). Dos 701 resultados, selecionamos os **3 maiores valores** de produto escalar — ou seja, as 3 amostras Embrapa mais similares àquele ponto.

Cada uma dessas 3 amostras possui uma classe de tipologia (`Tipologia_`), atribuída em campo. A partir dessas 3 classes, derivamos dois campos:

| Campo | Descrição |
|---|---|
| `class_embrapa` | A classe `Tipologia_` da amostra com **maior** produto escalar (top-1) |
| `md3` | Grau de **concordância** entre as classes dos 3 melhores matches |

---

## Fórmula do `md3`

O `md3` mede quantas das 3 amostras mais similares atribuem a **mesma classe** que o top-1. A fórmula é:

$$
\text{md3} = 1 + \mathbb{1}[\text{Tipologia\_2} = \text{Tipologia\_1}] + \mathbb{1}[\text{Tipologia\_3} = \text{Tipologia\_1}]
$$

Onde $\mathbb{1}[\cdot]$ é a **função indicadora** (vale 1 se a condição é verdadeira, 0 caso contrário).

Em SQL (DuckDB):

```sql
1
+ CASE WHEN tipologia_2 = tipologia_1 THEN 1 ELSE 0 END
+ CASE WHEN tipologia_3 = tipologia_1 THEN 1 ELSE 0 END
AS md3
```

---

## Interpretação dos Valores

| Valor | Significado | Interpretação |
|:---:|---|---|
| **md3 = 3** | `Tipologia_1 = Tipologia_2 = Tipologia_3` | **Alta confiança.** Todos os 3 melhores matches concordam na mesma classe. |
| **md3 = 2** | Apenas **um** entre `Tipologia_2` e `Tipologia_3` é igual a `Tipologia_1` | **Confiança moderada.** 2 de 3 matches concordam. |
| **md3 = 1** | Nem `Tipologia_2` nem `Tipologia_3` são iguais a `Tipologia_1` | **Baixa confiança.** Somente o match mais similar atribui aquela classe; os outros dois divergem. |

---

## Exemplo Prático

Considere um ponto MapBiomas cujos 3 melhores matches Embrapa são:

| Ranking | TARGET_FID | Produto Escalar | Tipologia_ |
|:---:|:---:|:---:|---|
| 1º (top-1) | 342 | 0.97 | PASTO PRODUTIVO |
| 2º (top-2) | 118 | 0.95 | PASTO PRODUTIVO |
| 3º (top-3) | 507 | 0.93 | PASTO COM ERVAS |

Cálculo:

- `class_embrapa` = `PASTO PRODUTIVO` (classe do top-1)
- `Tipologia_2 = Tipologia_1`? → `PASTO PRODUTIVO = PASTO PRODUTIVO` → **Sim** → +1
- `Tipologia_3 = Tipologia_1`? → `PASTO COM ERVAS = PASTO PRODUTIVO` → **Não** → +0
- **`md3 = 1 + 1 + 0 = 2`** (confiança moderada)

---

## Uso

O campo `md3` serve como um **indicador de confiança** na classificação atribuída por similaridade. Pontos com `md3 = 3` podem ser considerados mais confiáveis para treinamento ou validação, enquanto pontos com `md3 = 1` merecem revisão ou maior cautela na interpretação.
