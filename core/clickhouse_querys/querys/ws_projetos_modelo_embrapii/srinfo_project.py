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


def srinfo_project():
    query = """
            SELECT DISTINCT
                main.id AS proj_id,
                main.code AS proj_code,
                main.title AS proj_title,
                main.project_type AS proj_project_type,
                main.workpackages AS proj_workpackages,
                main.notes AS proj_notes,
                main.purpose AS proj_purpose,
                main.students AS proj_students,
                main.public_description AS proj_public_description,
                main.public_title AS proj_public_title,
                main.project_context AS proj_project_context,
                main.project_reference AS proj_project_reference,
                contract.contract_date AS ct_contract_date,
                contract.start_date AS ct_start_date,
                contract.finish_date AS ct_finish_date,
                contract.is_mandatory AS ct_is_mandatory,
                contract.embrapii_amount AS ct_embrapii_amount,
                contract.company_amount AS ct_company_amount,
                contract.ue_amount AS ct_ue_amount,
                contract.total_amount AS ct_total_amount,
                contract.defined_maturity_level AS ct_defined_maturity_level,
                contract.final_maturity_level AS ct_final_maturity_level,
                contract.financing_modality_id AS ct_financing_modality_id,
                financing_modality.alias AS fm_name,  
                unit.id AS unit_id,
                unit.name AS unit_name,
                unit.uf_state AS unit_uf,
                main.data_carga    
            FROM db_bronze_srinfo.project_project AS main
            LEFT JOIN (
                SELECT
                    proj_ue.unit_id,
                    proj_ue.project_id,
                    proj_ue.data_carga
                FROM db_bronze_srinfo.project_project_ue AS proj_ue
                INNER JOIN (
                    SELECT
                        project_id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.project_project_ue
                    WHERE data_inativacao IS NULL
                    GROUP BY project_id
                ) AS latest_project_ue
                ON proj_ue.project_id = latest_project_ue.project_id
                    AND proj_ue.data_carga = latest_project_ue.max_data_carga
                WHERE proj_ue.data_inativacao IS NULL
            ) AS proj_proj_unit
                ON main.id = proj_proj_unit.project_id
            LEFT JOIN db_bronze_srinfo.ue_unit AS unit
                ON proj_proj_unit.unit_id = unit.id
            LEFT JOIN (
                SELECT
                    ct.contract_date,
                    ct.start_date,
                    ct.finish_date,
                    ct.defined_maturity_level,
                    ct.is_mandatory,
                    ct.embrapii_amount,
                    ct.company_amount,
                    ct.ue_amount,
                    ct.total_amount,
                    ct.project_related_id,
                    ct.financing_modality_id,
                    ct.final_maturity_level,
                    ct.data_carga
                FROM db_bronze_srinfo.project_contract AS ct
                INNER JOIN (
                    SELECT
                        project_related_id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.project_contract
                    WHERE data_inativacao IS NULL
                    GROUP BY project_related_id
                ) AS latest_ct
                ON ct.project_related_id = latest_ct.project_related_id
                    AND ct.data_carga = latest_ct.max_data_carga
                WHERE ct.data_inativacao IS NULL
            ) AS contract
                ON main.id = contract.project_related_id
            LEFT JOIN (
                SELECT
                    fm.id,
                    fm.alias,
                    fm.description,
                    fm.data_carga
                FROM db_bronze_srinfo.project_financingmodality AS fm
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.project_financingmodality
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_fm
                ON fm.id = latest_fm.id
                    AND fm.data_carga = latest_fm.max_data_carga
                WHERE fm.data_inativacao IS NULL
            ) AS financing_modality
                ON contract.financing_modality_id = financing_modality.id
            WHERE main.data_inativacao IS NULL
    """
    nome_arquivo = "project"
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
    df_raw['ct_is_mandatory'] = df_raw['ct_is_mandatory'].map(DIC_IS_MANDATORY)
    df_raw['ct_defined_maturity_level'] = df_raw['ct_defined_maturity_level'].map(DIC_TRL)
    df_raw['ct_final_maturity_level'] = df_raw['ct_final_maturity_level'].map(DIC_TRL)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
