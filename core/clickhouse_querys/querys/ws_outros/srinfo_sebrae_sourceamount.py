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


def srinfo_sebrae_sourceamount():
    query = """
        		SELECT
                    ue_negotiation.code AS codigo_negociacao,
                    main.value AS valor,
                    source.alias AS fonte,
                    company.cnpj
                    FROM db_bronze_srinfo.partnership_sourceamount AS main
                -- JUNTANDO COM project_source --
                    LEFT JOIN (
                            SELECT
                                source.id,
                                source.alias
                            FROM db_bronze_srinfo.project_source AS source
                            INNER JOIN (
                                SELECT
                                    id,
                                    MAX(data_carga) AS max_data_carga
                                FROM db_bronze_srinfo.project_source
                                WHERE data_inativacao IS NULL
                                GROUP BY id
                            ) AS latest_source
                            ON source.id = latest_source.id
                                AND source.data_carga = latest_source.max_data_carga
                            WHERE source.data_inativacao IS NULL
                        ) AS source
                            ON main.source_id = source.id
                -- JUNTANDO COM funds_approval --
                    LEFT JOIN (
                            SELECT
                                fundsapproval.id,
                                fundsapproval.partnership_info_id,
                            FROM db_bronze_srinfo.partnership_fundsapproval AS fundsapproval
                            INNER JOIN (
                                SELECT
                                    id,
                                    MAX(data_carga) AS max_data_carga
                                FROM db_bronze_srinfo.partnership_fundsapproval
                                WHERE data_inativacao IS NULL
                                GROUP BY id
                            ) AS latest_fundsapproval
                            ON fundsapproval.id = latest_fundsapproval.id
                                AND fundsapproval.data_carga = latest_fundsapproval.max_data_carga
                            WHERE fundsapproval.data_inativacao IS NULL
                        ) AS fundsapproval
                            ON main.funds_approval_id = fundsapproval.id
                -- JUNTANDO COM ue_partnershipinfo --
                    LEFT JOIN (
                            SELECT
                                ue_partnership.id,
                                ue_partnership.negotiation_id,
                                ue_partnership.partnership_id
                            FROM db_bronze_srinfo.ue_partnershipinfo AS ue_partnership
                            INNER JOIN (
                                SELECT
                                    id,
                                    MAX(data_carga) AS max_data_carga
                                FROM db_bronze_srinfo.ue_partnershipinfo
                                WHERE data_inativacao IS NULL
                                GROUP BY id
                            ) AS latest_ue_partnership
                            ON ue_partnership.id = latest_ue_partnership.id
                                AND ue_partnership.data_carga = latest_ue_partnership.max_data_carga
                            WHERE ue_partnership.data_inativacao IS NULL
                        ) AS ue_partnership
                            ON fundsapproval.partnership_info_id = ue_partnership.id
                -- JUNTANDO COM partnership_partnership --
                    LEFT JOIN (
                            SELECT
                                partnership.id,
                                partnership.model
                            FROM db_bronze_srinfo.partnership_partnership AS partnership
                            INNER JOIN (
                                SELECT
                                    id,
                                    MAX(data_carga) AS max_data_carga
                                FROM db_bronze_srinfo.partnership_partnership
                                WHERE data_inativacao IS NULL
                                GROUP BY id
                            ) AS latest_partnership
                            ON partnership.id = latest_partnership.id
                                AND partnership.data_carga = latest_partnership.max_data_carga
                            WHERE partnership.data_inativacao IS NULL
                        ) AS partnership
                            ON ue_partnership.partnership_id = partnership.id
                -- JUNTANDO COM ue_negotiation --
                    LEFT JOIN (
                            SELECT
                                ue_negotiation.id,
                                ue_negotiation.code
                            FROM db_bronze_srinfo.ue_negotiation AS ue_negotiation
                            INNER JOIN (
                                SELECT
                                    id,
                                    MAX(data_carga) AS max_data_carga
                                FROM db_bronze_srinfo.ue_negotiation
                                WHERE data_inativacao IS NULL
                                GROUP BY id
                            ) AS latest_ue_negotiation
                            ON ue_negotiation.id = latest_ue_negotiation.id
                                AND ue_negotiation.data_carga = latest_ue_negotiation.max_data_carga
                            WHERE ue_negotiation.data_inativacao IS NULL
                        ) AS ue_negotiation
                            ON ue_partnership.negotiation_id = ue_negotiation.id
                -- JUNTANDO COM company_company --
                    LEFT JOIN (
                            SELECT
                                company.id,
                                company.cnpj
                            FROM db_bronze_srinfo.company_company AS company
                            INNER JOIN (
                                SELECT
                                    id,
                                    MAX(data_carga) AS max_data_carga
                                FROM db_bronze_srinfo.company_company
                                WHERE data_inativacao IS NULL
                                GROUP BY id
                            ) AS latest_company
                            ON company.id = latest_company.id
                                AND company.data_carga = latest_company.max_data_carga
                            WHERE company.data_inativacao IS NULL
                        ) AS company
                            ON main.company_id = company.id
                WHERE main.data_inativacao IS NULL
                AND partnership.model IN (2, 10, 9, 19, 20)
    """
    nome_arquivo = "sebrae_sourceamount"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)