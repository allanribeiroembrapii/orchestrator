import os
import sys
import pandas as pd
from dotenv import load_dotenv
from connection.query_clickhouse import query_clickhouse
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


def srinfo_event():
    query = """
        	SELECT DISTINCT
                main.id,
                main.title,
                main.publisher,
                main.publication_webpage,
                main.published_date,
                unit.id AS unit_id,
                unit.name AS unit_name,
                unit.uf_state AS unit_uf,
                main.data_carga    
            FROM db_bronze_srinfo.ue_communication AS main
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
            WHERE main.data_inativacao IS NULL
    """
    nome_arquivo = "ue_communication"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Substituir "main." nos nomes das colunas
    df_raw.columns = [col.replace("main.", "") for col in df_raw.columns]

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
