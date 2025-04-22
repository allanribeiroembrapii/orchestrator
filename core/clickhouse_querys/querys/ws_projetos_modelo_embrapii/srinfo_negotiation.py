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


def srinfo_negotiation():
    """
    Dados de negociações de projetos. Retorna todos os dados relativos à negociação.
    """
    query = """
        SELECT DISTINCT
            main.id,
            main.code AS negotiation_code,
            main.convertion_rank AS negotiation_convertion_rank,
            main.status AS negotiation_status,
            main.notes AS negotiation_notes,
            main.structuring_project_identifier AS negotiation_structuring_project_identifier,
            unit.id AS unit_id,
            unit.name AS unit_name,
            unit.uf_state AS unit_uf,
            prospect.id AS prospect_id,
            prospect.prospect_date AS prospect_date,
            techproposal.id AS techproposal_id,
            techproposal.first_version_date AS techproposal_first_version_date,
            techproposal.objectives AS techproposal_objetives,
            techproposal.version AS techproposal_version,
            workplan.id AS workplan_id,
            workplan.issue_date AS workplan_issue_date,
            workplan.objectives AS workplan_objectives,
            workplan.duration AS workplan_duration,
            workplan.total_value AS workplan_total_value,
            workplan.version AS workplan_version,
            project.id AS project_id,
            project.code AS project_code,
            main.data_carga
        FROM db_bronze_srinfo.ue_negotiation AS main
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
                prosp.id,
                prosp.prospect_date,
                prosp.data_carga
            FROM db_bronze_srinfo.ue_prospect AS prosp
            INNER JOIN (
                SELECT
                    id,
                    MAX(data_carga) AS max_data_carga
                FROM db_bronze_srinfo.ue_prospect
                WHERE data_inativacao IS NULL
                GROUP BY id
            ) AS latest_prosp
            ON prosp.id = latest_prosp.id
                AND prosp.data_carga = latest_prosp.max_data_carga
            WHERE prosp.data_inativacao IS NULL
        ) AS prospect
            ON main.originating_prospect_id = prospect.id
        LEFT JOIN (
            SELECT
                tp.negotiation_related_id,
                tp.id,
                tp.first_version_date,
                tp.objectives,
                tp.version,
                tp.data_carga
            FROM db_bronze_srinfo.ue_technicalproposal AS tp
            INNER JOIN (
                SELECT
                    negotiation_related_id,
                    MAX(data_carga) AS max_data_carga
                FROM db_bronze_srinfo.ue_technicalproposal
                WHERE data_inativacao IS NULL
                GROUP BY negotiation_related_id
            ) AS latest_tp
            ON tp.negotiation_related_id = latest_tp.negotiation_related_id
                AND tp.data_carga = latest_tp.max_data_carga
            WHERE tp.data_inativacao IS NULL
        ) AS techproposal
            ON main.id = techproposal.negotiation_related_id
        LEFT JOIN (
            SELECT
                proj.id,
                proj.code,
                proj.data_carga
            FROM db_bronze_srinfo.project_project AS proj
            INNER JOIN (
                SELECT
                    id,
                    MAX(data_carga) AS max_data_carga
                FROM db_bronze_srinfo.project_project
                WHERE data_inativacao IS NULL
                GROUP BY id
            ) AS latest_proj
            ON proj.id = latest_proj.id
                AND proj.data_carga = latest_proj.max_data_carga
            WHERE proj.data_inativacao IS NULL
        ) AS project
            ON main.converted_project_id = project.id
        LEFT JOIN (
            SELECT
                wp.id,
                wp.issue_date,
                wp.objectives,
                wp.duration,
                wp.total_value,
                wp.version,
                wp.tech_proposal_related_id,
                wp.data_carga
            FROM db_bronze_srinfo.ue_workplan AS wp
            INNER JOIN (
                SELECT
                    tech_proposal_related_id,
                    MAX(data_carga) AS max_data_carga
                FROM db_bronze_srinfo.ue_workplan
                WHERE data_inativacao IS NULL
                GROUP BY tech_proposal_related_id
            ) AS latest_wp
            ON wp.tech_proposal_related_id = latest_wp.tech_proposal_related_id
                AND wp.data_carga = latest_wp.max_data_carga
            WHERE wp.data_inativacao IS NULL
        ) AS workplan
            ON techproposal.id = workplan.tech_proposal_related_id
        WHERE main.data_inativacao IS NULL
    """
    nome_arquivo = "negotiation"
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
    # df_raw['recognition'] = df_raw['recognition'].map(DIC_BOOL_YES_NO)
    # df_raw['convertion_status'] = df_raw['convertion_status'].map(DIC_BOOL_YES_NO)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
