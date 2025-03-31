from dotenv import load_dotenv
import os
import sys
from connection.query_clickhouse import query_clickhouse
import pandas as pd
from querys.dictionarys import DIC_IS_MANDATORY, DIC_TRL

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def srinfo_project_contract():
    query = """
            SELECT DISTINCT
                main.id,
                prj.code AS code_project,
                pfm.alias AS financing_modality,
                main.is_mandatory,
                main.contract_date,
                main.start_date,
                main.finish_date,
                main.defined_maturity_level,
                main.final_maturity_level,
                main.embrapii_amount,
                main.company_amount,
                main.ue_amount,
                main.total_amount,
                main.data_carga    
            FROM db_bronze_srinfo.project_contract AS main
            LEFT JOIN db_bronze_srinfo.project_project as prj
            ON main.project_related_id = prj.id
            LEFT JOIN db_bronze_srinfo.project_financingmodality AS pfm
            ON main.financing_modality_id = pfm.id
            WHERE main.data_inativacao IS NULL
    """
    nome_arquivo = "project_contract"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Substituir "main." nos nomes das colunas
    df_raw.columns = [col.replace("main.", "") for col in df_raw.columns]

    # Dicionários
    df_raw['is_mandatory'] = df_raw['is_mandatory'].map(DIC_IS_MANDATORY)
    df_raw['defined_maturity_level'] = df_raw['defined_maturity_level'].map(DIC_TRL)
    df_raw['final_maturity_level'] = df_raw['final_maturity_level'].map(DIC_TRL)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
