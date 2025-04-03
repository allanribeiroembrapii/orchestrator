from dotenv import load_dotenv
import os
import sys
from connection.query_clickhouse import query_clickhouse
import pandas as pd

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def srinfo_company_company():
    """
    Dados de negociações de projetos. Retorna todos os dados relativos à negociação.
    """
    query = """
        SELECT DISTINCT
            company.*
        FROM db_bronze_srinfo.project_project_companies AS pc
        LEFT JOIN (
            -- Seleciona as empresas com a data_carga mais recente e data_inativacao NULL
            SELECT 
                company.*
            FROM db_bronze_srinfo.company_company AS company
            INNER JOIN (
                SELECT id, MAX(data_carga) AS max_data_carga
                FROM db_bronze_srinfo.company_company
                WHERE data_inativacao IS NULL
                GROUP BY id
            ) AS latest_company
            ON company.id = latest_company.id
            AND company.data_carga = latest_company.max_data_carga
            WHERE company.data_inativacao IS NULL
        ) AS company
        ON pc.company_id = company.id
    """
    nome_arquivo = "company_company"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # # Substituir "main." nos nomes das colunas
    # df_raw.columns = [col.replace("main.", "") for col in df_raw.columns]

    # Dicionários
    # df_raw['recognition'] = df_raw['recognition'].map(DIC_BOOL_YES_NO)
    # df_raw['convertion_status'] = df_raw['convertion_status'].map(DIC_BOOL_YES_NO)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
