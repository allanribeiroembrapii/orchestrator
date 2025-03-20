import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import shutil
import importlib.util

# Verificar se sqlalchemy está disponível
sqlalchemy_available = importlib.util.find_spec("sqlalchemy") is not None

# Importar sqlalchemy apenas se estiver disponível
if sqlalchemy_available:
    from sqlalchemy import create_engine, MetaData
    # Verificar se sqlalchemy_schemadisplay está disponível
    sqlalchemy_schemadisplay_available = importlib.util.find_spec("sqlalchemy_schemadisplay") is not None
    if sqlalchemy_schemadisplay_available:
        from sqlalchemy_schemadisplay import create_schema_graph

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
ROOT = os.getenv('ROOT')

# Caminho do diretório contendo as planilhas
DWPII_UP = os.path.abspath(os.path.join(ROOT, 'DWPII_up'))

# Caminho do banco de dados SQLite
db_copy = os.path.join(ROOT, 'DWPII_copy', 'db_srinfo.db')
db_up = os.path.join(ROOT, 'DWPII_up', 'db_srinfo.db')
der_path = os.path.join(ROOT, 'DWPII_up', 'der_srinfo.png')

def gerar_db_sqlite():

    shutil.copy(db_copy, db_up)

    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(db_up)
    cursor = conn.cursor()

    # Iterar sobre os arquivos no diretório
    for filename in os.listdir(DWPII_UP):

        if filename == "classificacao_projeto.xlsx":
            continue

        if filename == "classificacao_tematica_projetos.xlsx":
            continue

        if filename.endswith(".xlsx"):
            filepath = os.path.join(DWPII_UP, filename)
            # Ler a planilha
            df = pd.read_excel(filepath)
            # Nome da tabela no banco de dados será o nome do arquivo sem a extensão
            table_name = os.path.splitext(filename)[0]
            # Sanitizar nomes de colunas
            df.columns = [col.encode('ascii', 'ignore').decode('ascii') for col in df.columns]
            # Limpar dados da tabela antes de inserir novos dados
            clear_table(table_name, cursor, conn)
            # Inserir os dados no banco de dados
            df.to_sql(table_name, conn, if_exists='append', index=False)
            
    # Fechar a conexão com o banco de dados
    conn.close()

    # gerar_der()


def gerar_der():
    """
    Gera um diagrama ER do banco de dados SQLite.
    Requer sqlalchemy e sqlalchemy_schemadisplay.
    """
    # Verificar se as dependências estão disponíveis
    if not sqlalchemy_available:
        print("Aviso: sqlalchemy não está disponível. Não é possível gerar o diagrama ER.")
        return
    
    if not 'sqlalchemy_schemadisplay_available' in globals() or not sqlalchemy_schemadisplay_available:
        print("Aviso: sqlalchemy_schemadisplay não está disponível. Não é possível gerar o diagrama ER.")
        return
    
    try:
        # Conectar ao banco de dados SQLite usando SQLAlchemy
        engine = create_engine(f'sqlite:///{db_up}')
        metadata = MetaData()
        metadata.reflect(bind=engine)

        # Criar o diagrama ER
        graph = create_schema_graph(metadata=metadata, engine=engine)
        graph.write_png(der_path)
        print(f"Diagrama ER gerado com sucesso em: {der_path}")
    except Exception as e:
        print(f"Erro ao gerar diagrama ER: {str(e)}")


# Função para limpar dados da tabela
def clear_table(table_name, cursor, conn):
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
