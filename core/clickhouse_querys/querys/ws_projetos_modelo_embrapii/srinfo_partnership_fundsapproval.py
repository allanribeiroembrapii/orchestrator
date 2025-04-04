from dotenv import load_dotenv
import os
import sys
from connection.query_clickhouse import query_clickhouse
import pandas as pd
from querys.dictionarys import DIC_FUNDSAPPROVAL_STATUS

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def srinfo_partnership_fundsapproval():
    """
    Dados de solicitação de reserva de recursos
    """
    query = """
        SELECT
            main.id AS fundsapp_id,
            main.created_at AS fundsapp_created_at,
            main.updated_at AS fundsapp_updated_at,
            main.status AS fundsapp_status,
            main.notes AS fundsapp_notes,
            main.ticket_transfer AS fundsapp_ticket_transfer,
            main.ticket_ue AS fundsapp_ticket_monitoring,
            main.expiration AS fundsapp_expiration,
            main.reserved_at AS fundsapp_reserved_at,
            main.transfer_conclusion AS fundsapp_transfer_conclusion,
            partnership_call.name AS partnership_call_name,
            partnership.name AS partnership_name,
            modality.alias AS modality_alias,
            negotiation.code AS negotiation_code,
            negotiation.status AS negotiation_status,
            unit.name AS unit_name,
            proj.code AS proj_code,
            proj.status AS proj_status,
            contr.contract_date AS ct_contract_date,
            tp.objectives AS techproposal_objectives,
            main.data_carga AS data_carga,
            -- COMPANY_AMOUNT --
            CASE
                WHEN partnership.model IN (2, 10, 9, 19, 20)
                THEN COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) IN (7, 6, 5, 1)
                    THEN sourceamount.value ELSE NULL END), 0)
                ELSE COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) IN (7, 6, 5, 1, 4)
                    THEN sourceamount.value ELSE NULL END), 0)
            END AS company_amount,
            -- PARTNERSHIP_AMOUNT --
            CASE
                WHEN CAST(COALESCE(partnership.model, '0') AS Int) IN (2, 10, 9, 19, 20)
                THEN COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) = 4
                    THEN sourceamount.value ELSE NULL END), 0)
                WHEN CAST(COALESCE(partnership.model, '0') AS Int) IN (5, 11, 12, 13, 14, 15, 16, 17, 18)
                THEN COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) = 9
                    THEN sourceamount.value ELSE NULL END), 0)
                ELSE COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) = 2
                    THEN sourceamount.value ELSE NULL END), 0)
            END AS partnership_amount,
            -- EMBRAPII_AMOUNT --
            CASE
                WHEN CAST(COALESCE(partnership.model, '0') AS Int) IN (5, 11, 12, 13, 14, 15, 16, 17, 18)
                THEN COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) = 9
                    THEN sourceamount.value ELSE NULL END), 0)
                WHEN CAST(COALESCE(partnership.model, '0') AS Int) IN (2, 10, 9, 19, 20)
                THEN COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) IN (9, 2)
                    THEN sourceamount.value ELSE NULL END), 0)
                ELSE COALESCE(SUM(CASE
                    WHEN CAST(COALESCE(source.source, '0') AS Int) = 2
                    THEN sourceamount.value ELSE NULL END), 0)
            END AS embrapii_amount,
            -- UE_AMOUNT --
            COALESCE(SUM(CASE 
                WHEN CAST(COALESCE(source.source, '0') AS Int) = 3 
                THEN sourceamount.value ELSE NULL END), 0)
            AS ue_amount
        FROM db_bronze_srinfo.partnership_fundsapproval AS main 
        -- JUNTANDO COM ue_partnershipinfo --
        LEFT JOIN (
                SELECT
                    ue_partnership.id,
                    ue_partnership.call_id,
                    ue_partnership.financing_modality_id,
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
            ) AS ue_partnershipinfo
                ON main.partnership_info_id = ue_partnershipinfo.id
        -- JUNTANDO COM partnership_call --
        LEFT JOIN (
                SELECT
                    partnership_call.id,
                    partnership_call.name,
                    partnership_call.partnership_id,
                FROM db_bronze_srinfo.partnership_call AS partnership_call
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.partnership_call
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_partnership_call
                ON partnership_call.id = latest_partnership_call.id
                    AND partnership_call.data_carga = latest_partnership_call.max_data_carga
                WHERE partnership_call.data_inativacao IS NULL
            ) AS partnership_call
                ON ue_partnershipinfo.call_id = partnership_call.id
        -- JUNTANDO COM partnership_partnership --
        LEFT JOIN (
                SELECT
                    partnership.id,
                    partnership.name,
                    partnership.partner_id,
                    partnership.model,
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
                ON ue_partnershipinfo.partnership_id = partnership.id
        -- JUNTANDO COM partnership_sourceamount --
        LEFT JOIN (
                SELECT
                    sourceamount.id,
                    sourceamount.value,
                    sourceamount.funds_approval_id,
                    sourceamount.source_id,
                FROM db_bronze_srinfo.partnership_sourceamount AS sourceamount
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.partnership_sourceamount
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_sourceamount
                ON sourceamount.id = latest_sourceamount.id
                    AND sourceamount.data_carga = latest_sourceamount.max_data_carga
                WHERE sourceamount.data_inativacao IS NULL
            ) AS sourceamount
                ON main.id = sourceamount.funds_approval_id
        -- JUNTANDO COM partnership_source --
        LEFT JOIN (
                SELECT
                    source.id,
                    source.source,
                    source.alias,
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
                ON sourceamount.source_id = source.id
        -- JUNTANDO COM project_financingmodality --
        LEFT JOIN (
                SELECT
                    modality.id,
                    modality.model,
                    modality.alias,
                FROM db_bronze_srinfo.project_financingmodality AS modality
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.project_financingmodality
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_modality
                ON modality.id = latest_modality.id
                    AND modality.data_carga = latest_modality.max_data_carga
                WHERE modality.data_inativacao IS NULL
            ) AS modality
                ON ue_partnershipinfo.financing_modality_id = modality.id
        -- JUNTANDO COM ue_negotiation --
        LEFT JOIN (
                SELECT
                    negotiation.id,
                    negotiation.code,
                    negotiation.status,
                    negotiation.converted_project_id,
                    negotiation.originating_prospect_id,
                    negotiation.ue_id,
                FROM db_bronze_srinfo.ue_negotiation AS negotiation
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.ue_negotiation
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_negotiation
                ON negotiation.id = latest_negotiation.id
                    AND negotiation.data_carga = latest_negotiation.max_data_carga
                WHERE negotiation.data_inativacao IS NULL
            ) AS negotiation
                ON ue_partnershipinfo.negotiation_id = negotiation.id
        -- JUNTANDO COM ue_unit --
        LEFT JOIN (
                SELECT
                    unit.id,
                    unit.name,
                    unit.uf_state,
                    unit.city,
                    unit.action_plan_signature,
                FROM db_bronze_srinfo.ue_unit AS unit
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.ue_unit
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_unit
                ON unit.id = latest_unit.id
                    AND unit.data_carga = latest_unit.max_data_carga
                WHERE unit.data_inativacao IS NULL
            ) AS unit
                ON negotiation.ue_id = unit.id
        -- JUNTANDO COM project_project --
        LEFT JOIN (
                SELECT
                    proj.id,
                    proj.code,
                    proj.status,
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
            ) AS proj
                ON negotiation.converted_project_id = proj.id
        -- JUNTANDO COM project_contract -- 
        LEFT JOIN (
                SELECT
                    contr.id,
                    contr.project_related_id,
                    contr.contract_date,
                    contr.financing_modality_id,
                    contr.embrapii_amount,
                    contr.company_amount,
                    contr.ue_amount,
                    contr.total_amount,
                FROM db_bronze_srinfo.project_contract AS contr
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.project_contract
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_contr
                ON contr.id = latest_contr.id
                    AND contr.data_carga = latest_contr.max_data_carga
                WHERE contr.data_inativacao IS NULL
            ) AS contr
                ON proj.id = contr.project_related_id
        -- JUNTANDO COM ue_technicalproposal --
        LEFT JOIN (
                SELECT
                    tp.id,
                    tp.negotiation_related_id,
                    tp.objectives,
                FROM db_bronze_srinfo.ue_technicalproposal AS tp
                INNER JOIN (
                    SELECT
                        id,
                        MAX(data_carga) AS max_data_carga
                    FROM db_bronze_srinfo.ue_technicalproposal
                    WHERE data_inativacao IS NULL
                    GROUP BY id
                ) AS latest_tp
                ON tp.id = latest_tp.id
                    AND tp.data_carga = latest_tp.max_data_carga
                WHERE tp.data_inativacao IS NULL
            ) AS tp
                ON negotiation.id = tp.negotiation_related_id
        WHERE main.data_inativacao IS NULL
        GROUP BY
            fundsapp_id,
            fundsapp_created_at,
            fundsapp_updated_at,
            fundsapp_status,
            fundsapp_notes,
            fundsapp_ticket_transfer,
            fundsapp_ticket_monitoring,
            fundsapp_expiration,
            fundsapp_reserved_at,
            fundsapp_transfer_conclusion,
            partnership_call_name,
            partnership_name,
            partnership.model,
            modality_alias,
            negotiation_code,
            negotiation_status,
            unit_name,
            proj_code,
            proj_status,
            ct_contract_date,
            techproposal_objectives,
            data_carga
    """
    nome_arquivo = "partnership_fundsapproval"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Dicionários
    df_raw['fundsapp_status'] = df_raw['fundsapp_status'].map(DIC_FUNDSAPPROVAL_STATUS)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
