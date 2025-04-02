from dotenv import load_dotenv
import os
import sys
from connection.query_clickhouse import query_clickhouse
import pandas as pd
from querys.dictionarys import DIC_BOOL_YES_NO

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def srinfo_prospect():
    query = """
        SELECT DISTINCT
                main.id,
                main.initiative,
                main.interaction_type,
                main.prospect_date,
                main.company_person,
                main.company_contact,
                main.company_contact_position,
                main.reports,
                main.notes,
                main.recognition,
                main.convertion_status,
                unit.id AS unit_id,
                unit.name AS unit_name,
                unit.uf_state AS unit_uf,
                company.id AS company_id,
                company.name AS company_name,
                company.cnpj AS company_cnpj,
                main.data_carga    
            FROM db_bronze_srinfo.ue_prospect AS main
            LEFT JOIN (
                SELECT
                    ue.id,
                    ue.name,
                    ue.uf_state,
                    ue.data_carga
                FROM db_bronze_srinfo.ue_unit AS ue
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.ue_unit
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_ue
                ON ue.id = latest_ue.id
                    AND ue.data_carga = latest_ue.max_data_carga
                WHERE ue.data_inativacao IS NULL
            ) AS unit
                ON main.ue_id = unit.id
            LEFT JOIN (
                SELECT
                    comp.id,
                    comp.name,
                    comp.cnpj,
                    comp.data_carga
                FROM db_bronze_srinfo.company_company AS comp
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.company_company
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_comp
                ON comp.id = latest_comp.id
                    AND comp.data_carga = latest_comp.max_data_carga
                WHERE comp.data_inativacao IS NULL
            ) AS company
                ON main.company_id = company.id
            WHERE main.data_inativacao IS NULL
    """
    nome_arquivo = "ue_prospect"
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
    df_raw['recognition'] = df_raw['recognition'].map(DIC_BOOL_YES_NO)
    df_raw['convertion_status'] = df_raw['convertion_status'].map(DIC_BOOL_YES_NO)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
