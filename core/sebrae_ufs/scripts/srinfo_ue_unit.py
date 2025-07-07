import os
import sys
import pandas as pd
from dotenv import load_dotenv
from scripts.query_clickhouse import query_clickhouse

load_dotenv()

ROOT = os.getenv('ROOT_SEBRAE_UFS')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')
STEP1 = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))

def srinfo_ue_unit():
    query = """
        		SELECT DISTINCT
                    *
                FROM s3(cred_s3, url = s3m_srinfo('ue_unit', today()))
    """
    nome_arquivo = "unit"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(STEP1 ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Salvar em formato Excel
    print(f"Salvando arquivo {nome_arquivo} em formato Excel")
    path_file_processed = os.path.abspath(os.path.join(STEP1, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
    path_file_processed = os.path.abspath(os.path.join(STEP3, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)