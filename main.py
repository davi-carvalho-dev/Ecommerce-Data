import pandas as pd 
import sqlite3 

# ============================================================================== 
# ETAPA 1: CRIAÇÃO E CARGA DOS DADOS BRUTOS (PYTHON) 
# ============================================================================== 

dados_brutos = { 'id_pedido': [1, 2, 3, 4, 5, 6, 7, 8, 9],
'data_venda': ['2024-01-15', '2024-01-16', '17/01/2024', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-20', '2024-01-21', '2024-01-22'], 
'cliente_id': ['C101', 'C102', 'C103', 'C104', 'C105', 'C106', 'C106', 'C107', 'C108'], 
'categoria': ['Eletrônicos', 'Vestiário', 'Eletrônicos', 'Casa', 'Vestiário', 'Eletrônicos', 'Eletrônicos', None, 'Casa'], 
'preco_unitario': [1500.0, 80.0, 350.0, 120.0, 200.0, 800.0, 800.0, 50.0, 300.0], 
'quantidade': [1, 2, 1, 3, None, 1, 1, 4, 2] 
} 

# Gerando e salvando o CSV bruto 
df_gerador = pd.DataFrame(dados_brutos) 
df_gerador.to_csv('vendas_ecommerce_bruto.csv', index=False) 
print("--- 1. Arquivo 'vendas_ecommerce_bruto.csv' criado no computador! ---") 


# ============================================================================== 
#  ETAPA 2: EXPLORAÇÃO E TRATAMENTO DE DADOS (PANDAS) 
# ============================================================================== 

df_ecommerce = pd.read_csv('vendas_ecommerce_bruto.csv') 
print("\n--- 2. Primeiras linhas da tabela bruta (head) ---") 
print(df_ecommerce.head()) 
print("\n--- 3. Informações técnicas da tabela bruta (info) ---") 
print(df_ecommerce.info()) 
print("\n--- 4. Quantidade de nulos por coluna ---") 
print(df_ecommerce.isna().sum()) 

# Tratamento de valores nulos 
df_ecommerce['categoria'] = df_ecommerce['categoria'].fillna('Outros') 
df_ecommerce['quantidade'] = df_ecommerce['quantidade'].fillna(1.0) 

# Padronização da data 
df_ecommerce['data\_venda'] = pd.to_datetime(df_ecommerce['data_venda'], format='mixed')

#Identificação e remoção de duplicatas
colunas_checar = ['data_venda', 'cliente_id', 'categoria', 'preco_unitario', 'quantidade']
print(f"\nDuplicatas encontradas:{df_ecommerce.duplicated(subset=colunas_checar).sum()}")

df_ecommerce = df_ecommerce.drop_duplicates(subset=colunas_checar).reset_index(drop=True)

#Cálculo da coluna de faturamento
df_ecommerce['preco_unitario']= pd.to_numeric(df_ecommerce['preco_unitario'],errors='coerce')
df_ecommerce['quantidade']= pd.to_numeric(df_ecommerce['quantidade'],errors='coerce')
df_ecommerce['faturamento_total']= pd.to_numeric(df_ecommerce['preco_unitario'],errors='coerce')


#Salva a base tratada em CSV

df_ecommerce.to_csv('vendas_ecommerce_limpo.csv', index=False, sep=';')
print("\n--- 5\. Tabela Limpa e Tratada (Pandas) ---") 
print(df_ecommerce)

# ======================================================= 
# ETAPA 3: BANCO DE DADOS E CONSULTAS ANALÍTICAS (SQL) 
# ======================================================= 
# 1. Conexão ao banco SQLite 

conexao = sqlite3.connect('ecommerce.db')

#2. Ingestão da tabela de vendas tratada
df_ecommerce.to_sql('tb_vendas', conexao, if_exists='replace', index=False)

# 3. Criação e Ingestão da tabela cadastral de clientes 
dados_clientes = { 'cliente_id': ['C101', 'C102', 'C103', 'C104', 'C105', 'C106', 'C107', 'C108'], 
'nome_cliente': ['Ana Silva', 'Bruno Lima', 'Carla Souza', 'Diego Alves', 'Elena Dias', 'Fábio Costa', 'Gisele Rocha', 'Heitor Mello'], 
'estado': ['SP', 'RJ', 'MG', 'SP', 'RJ', 'SP', 'SC', 'PR']
}

df_clientes = pd.DataFrame(dados_clientes)
df_clientes.to_sql('tb_clientes', conexao, if_exists='replace', index=False)

print("\n===================================") 
print(" CONSULTAS SQL DO PROJETO ") 
print("=====================================")

# CONSULTA 1: Faturamento por Categoria (GROUP BY) 
query_categoria = ''' 
SELECT 
    categoria, 
    SUM(faturamento_total) AS faturamento_categoria, 
    COUNT(id_pedido) AS total_pedidos 
FROM tb_vendas 
GROUP BY categoria 
ORDER BY faturamento_categoria DESC; 
'''
res_categoria = pd.read_sql_query(query_categoria, conexao)
print("\n--- Métrica 1: Faturamento e Pedidos por Categoria ---")
print(res_categoria)

#CONSULTA 2 :Ticket Médio por Cliente(GROUP BY)

query_cliente = '''
SELECT
    cliente_id,
    AVG(faturamento_total) AS ticket_medio,
    SUM(faturamento_total) AS total_gasto,
    COUNT(*) AS qtd_compass
FROM tb_vendas
GROUP BY cliente_id;
'''
res_cliente = pd.read_sql_query(query_cliente, conexao)
print("\n-- Métrica 2: Ticket Médio por Cliente ---")
print(res_cliente)

#CONSULTA 3: Cruzamento de Vendas e Clientes (INNER JOIN)
query_join= '''
 SELECT
    vendas.id_pedido,
    clientes.nome_cliente,
    clientes.estado,
    vendas.categoria,
    vendas.faturamento_total
FROM tb_vendas AS vendas
INNER JOIN tb_clientes AS clientes
ON vendas.cliente_id = clientes.cliente_id;
'''

res_join = pd.read_sql_query(query_join, conexao)
print("\n--- Métrica 3: Relatório Cruzado de Vendas e Clientes (JOIN) ---") 
print(res_join)

#Fechamento a conexão com o banco
conexao.close()
print("\n Conexão com o banco 'ecommerce.db' encerrada com sucesso! ---")