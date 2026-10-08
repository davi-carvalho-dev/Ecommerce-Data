# 🛒 Ecommerce Data — Pipeline de Dados de Vendas

Projeto de **engenharia e análise de dados** que simula o fluxo completo de dados de um e-commerce: da geração de uma base bruta e "suja", passando pela limpeza com **Pandas**, até a carga em um banco **SQLite** e a extração de métricas de negócio com **SQL**.

O objetivo é praticar, em um único script, as etapas de um processo **ETL** (*Extract, Transform, Load*) e as consultas analíticas mais comuns no dia a dia de quem trabalha com dados.

---

## 📌 Sumário

- [Tecnologias](#-tecnologias)
- [Visão geral do fluxo](#-visão-geral-do-fluxo)
- [Etapa 1 — Dados brutos](#etapa-1--criação-dos-dados-brutos)
- [Etapa 2 — Tratamento com Pandas](#etapa-2--exploração-e-tratamento-pandas)
- [Etapa 3 — Banco de dados e SQL](#etapa-3--banco-de-dados-e-consultas-analíticas-sql)
- [Como executar](#-como-executar)
- [Arquivos gerados](#-arquivos-gerados)
- [Conceitos praticados](#-conceitos-praticados)
- [Próximos passos](#-próximos-passos)

---

## 🧰 Tecnologias

| Ferramenta | Uso no projeto |
|---|---|
| **Python ** | Linguagem principal |
| **Pandas** | Leitura, exploração e limpeza dos dados |
| **SQLite3** (biblioteca padrão do Python) | Banco de dados relacional local |
| **SQL** | Consultas analíticas (`GROUP BY`, `SUM`, `AVG`, `COUNT`, `INNER JOIN`) |

---

## 🔄 Visão geral do fluxo

```
┌──────────────────┐     ┌──────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Dados brutos    │ ──▶ │  Tratamento (Pandas) │ ──▶ │  Carga (SQLite)  │ ──▶ │  Análises (SQL)  │
│  CSV com erros   │     │  nulos, datas,       │     │  tb_vendas       │     │  categoria,      │
│                  │     │  duplicatas          │     │  tb_clientes     │     │  ticket, JOIN    │
└──────────────────┘     └──────────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## Etapa 1 — Criação dos dados brutos

O script cria uma pequena base de **9 pedidos** propositalmente com problemas reais de qualidade de dados, para que a etapa de limpeza tenha o que resolver:

| Problema inserido | Onde aparece |
|---|---|
| **Valor nulo** em categoria | Pedido 8 (`categoria = None`) |
| **Valor nulo** em quantidade | Pedido 5 (`quantidade = None`) |
| **Formato de data inconsistente** | Pedido 3 (`17/01/2024` em vez de `2024-01-17`) |
| **Registro duplicado** | Pedidos 6 e 7 (mesmo cliente, data, produto e valor) |

Esses dados são salvos em `vendas_ecommerce_bruto.csv`, simulando a extração de um sistema de origem.

**Colunas da base de vendas:**

| Coluna | Descrição |
|---|---|
| `id_pedido` | Identificador do pedido |
| `data_venda` | Data em que a venda ocorreu |
| `cliente_id` | Código do cliente (chave para a tabela de clientes) |
| `categoria` | Categoria do produto (Eletrônicos, Vestiário, Casa) |
| `preco_unitario` | Preço de uma unidade |
| `quantidade` | Quantidade de unidades compradas |

---

## Etapa 2 — Exploração e tratamento (Pandas)

### 🔍 Exploração inicial

Antes de alterar qualquer dado, o script inspeciona a base:

- `head()` → mostra as primeiras linhas;
- `info()` → mostra tipos de dados e contagem de valores não nulos;
- `isna().sum()` → conta quantos valores nulos existem em cada coluna.

### 🧹 Limpeza

| Problema | Solução aplicada | Por quê |
|---|---|---|
| Categoria nula | Preenchida com `'Outros'` | Não perder o pedido nas análises por categoria |
| Quantidade nula | Preenchida com `1` | Assume-se que todo pedido tem pelo menos 1 item |
| Datas em formatos diferentes | `pd.to_datetime(..., format='mixed')` | Padroniza tudo para o formato `AAAA-MM-DD` |
| Pedido duplicado | `drop_duplicates()` usando as colunas de negócio | Evita contar a mesma venda duas vezes |

> 💡 A verificação de duplicatas **ignora o `id_pedido`**, porque os pedidos 6 e 7 têm IDs diferentes mas representam a mesma venda. Comparar só as colunas de negócio (data, cliente, categoria, preço, quantidade) é o que permite identificar a duplicidade.

### ➕ Nova coluna

É criada a coluna **`faturamento_total`**, que representa o valor de cada pedido:

```
faturamento_total = preco_unitario × quantidade
```

A base limpa é salva em `vendas_ecommerce_limpo.csv` (separador `;`, que abre corretamente no Excel em português).

---

## Etapa 3 — Banco de dados e consultas analíticas (SQL)

Os dados tratados são carregados em um banco **SQLite** (`ecommerce.db`) com duas tabelas:

| Tabela | Conteúdo |
|---|---|
| `tb_vendas` | Pedidos já limpos (resultado da Etapa 2) |
| `tb_clientes` | Cadastro dos clientes: `cliente_id`, `nome_cliente`, `estado` |

As duas tabelas se relacionam pela coluna **`cliente_id`**.

### 📊 Métrica 1 — Faturamento e pedidos por categoria

```sql
SELECT
    categoria,
    SUM(faturamento_total) AS faturamento_categoria,
    COUNT(id_pedido)       AS total_pedidos
FROM tb_vendas
GROUP BY categoria
ORDER BY faturamento_categoria DESC;
```

Responde: **quais categorias mais vendem?** Agrupa os pedidos por categoria, soma o faturamento e conta os pedidos, ordenando da que mais fatura para a que menos fatura.

### 📊 Métrica 2 — Ticket médio por cliente

```sql
SELECT
    cliente_id,
    AVG(faturamento_total) AS ticket_medio,
    SUM(faturamento_total) AS total_gasto,
    COUNT(*)               AS qtd_compras
FROM tb_vendas
GROUP BY cliente_id;
```

Responde: **quanto cada cliente gasta, em média, por compra?** O ticket médio é um indicador clássico de e-commerce para entender o comportamento de consumo.

### 📊 Métrica 3 — Relatório cruzado de vendas e clientes

```sql
SELECT
    vendas.id_pedido,
    clientes.nome_cliente,
    clientes.estado,
    vendas.categoria,
    vendas.faturamento_total
FROM tb_vendas AS vendas
INNER JOIN tb_clientes AS clientes
    ON vendas.cliente_id = clientes.cliente_id;
```

Responde: **quem comprou o quê, e de onde?** O `INNER JOIN` junta a tabela de vendas com a de clientes, trazendo nome e estado para cada pedido — base para análises regionais.

---

## ▶️ Como executar

**Pré-requisitos:** Python 3.8+ instalado.

```bash
# 1. Clone o repositório
git clone https://github.com/davi-carvalho-dev/Ecommerce-Data.git
cd Ecommerce-Data

# 2. Instale a dependência
pip install pandas

# 3. Execute o script
python main.py
```

O script imprime no terminal cada etapa: a base bruta, os nulos encontrados, as duplicatas removidas, a tabela limpa e o resultado das três consultas SQL.

---

## 📁 Arquivos gerados

Ao rodar o script, são criados na pasta do projeto:

| Arquivo | Descrição |
|---|---|
| `vendas_ecommerce_bruto.csv` | Base original, com os erros |
| `vendas_ecommerce_limpo.csv` | Base tratada |
| `ecommerce.db` | Banco SQLite com `tb_vendas` e `tb_clientes` |

> Esses arquivos estão no `.gitignore`, pois são gerados automaticamente a cada execução.

---

## 🎯 Conceitos praticados

- **ETL**: extração, transformação e carga de dados
- **Qualidade de dados**: tratamento de nulos, padronização de datas e remoção de duplicatas
- **Pandas**: `read_csv`, `fillna`, `to_datetime`, `drop_duplicates`, `to_sql`, `read_sql_query`
- **Modelagem relacional**: tabela fato (vendas) + tabela dimensão (clientes) ligadas por chave
- **SQL analítico**: agregações (`SUM`, `AVG`, `COUNT`), `GROUP BY`, `ORDER BY` e `INNER JOIN`
- **Métricas de negócio**: faturamento por categoria e ticket médio

---

## 🚀 Próximos passos

- [ ] Adicionar um `requirements.txt`
- [ ] Criar gráficos das métricas com Matplotlib ou Seaborn
- [ ] Adicionar uma análise de faturamento por estado (`GROUP BY estado` após o JOIN)
- [ ] Ler os dados de uma fonte maior (ex.: dataset público de e-commerce do Kaggle)
- [ ] Separar o script em funções/módulos (`extract`, `transform`, `load`)

---

## 👤 Autor

**Davi Carvalho** — estudante de Análise e Desenvolvimento de Sistemas

[![GitHub](https://img.shields.io/badge/GitHub-davi--carvalho--dev-181717?logo=github)](https://github.com/davi-carvalho-dev)
