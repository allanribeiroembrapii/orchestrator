import psycopg2
import pandas as pd

# Credenciais do banco Heroku
DB_HOST = 'cbhk6rs82poqi7.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com'
DB_NAME = 'dfotgpmc8offkr'
DB_USER = 'ufko09qfvgbn4g'
DB_PASS = 'p895a87e702cb837c9a1a83505f0c5eab91d65f4a870fcf303120f278a7dc4fe1'
DB_PORT = '5432'

# Tabelas que queremos baixar
tables = ['projetos', 'classificacoes_adicionais', 'logs', 'categorias', 'categoria_listas']
schema = 'gepes'

# Conectar ao banco de dados
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    port=DB_PORT,
    sslmode='require'  # obrigatório para Heroku
)

# Baixar os dados e salvar em arquivos
for table in tables:
    query = f'SELECT * FROM {schema}.{table};'
    df = pd.read_sql_query(query, conn)
    df.to_excel(f'{table}.xlsx', index=False)
    print(f'Tabela {table} salva como {table}.xlsx')

# Fechar conexão
conn.close()
print("Conexão encerrada.")
