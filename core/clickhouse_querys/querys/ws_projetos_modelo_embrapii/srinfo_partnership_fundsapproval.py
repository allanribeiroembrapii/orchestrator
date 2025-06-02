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
            main.id fundsapp_id,
            main.created_at fundsapp_created_at,
            main.updated_at fundsapp_updated_at,
            main.status fundsapp_status,
            main.notes fundsapp_notes,
            main.ticket_transfer fundsapp_ticket_transfer,
            main.ticket_ue fundsapp_ticket_monitoring,
            main.expiration fundsapp_expiration,
            main.reserved_at fundsapp_reserved_at,
            main.transfer_conclusion fundsapp_transfer_conclusion,
            partnership_call.name partnership_call_name,
            partnership.name partnership_name,
            modality.alias modality_alias,
            negotiation.code negotiation_code,
            negotiation.status negotiation_status,
            unit.name unit_name,
            proj.code proj_code,
            proj.status proj_status,
            contr.contract_date ct_contract_date,
            tp.objectives techproposal_objectives,
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
        FROM s3(cred_s3, url = s3m_srinfo('partnership_fundsapproval', today())) main 
        -- JUNTANDO COM ue_partnershipinfo --
        LEFT JOIN (
                SELECT
                    id,
                    call_id,
                    financing_modality_id,
                    negotiation_id,
                    partnership_id
                FROM s3(cred_s3, url = s3m_srinfo('ue_partnershipinfo', today()))
            ) ue_partnership
                ON main.partnership_info_id = ue_partnership.id
        -- JUNTANDO COM partnership_call --
        LEFT JOIN (
                SELECT
                    id,
                    name,
                    partnership_id,
                FROM s3(cred_s3, url = s3m_srinfo('partnership_call', today()))
            ) partnership_call
                ON ue_partnership.call_id = partnership_call.id
        -- JUNTANDO COM partnership_partnership --
        LEFT JOIN (
                SELECT
                    id,
                    name,
                    partner_id,
                    model,
                FROM s3(cred_s3, url = s3m_srinfo('partnership_partnership', today()))
            ) partnership
                ON ue_partnership.partnership_id = partnership.id
        -- JUNTANDO COM partnership_sourceamount --
        LEFT JOIN (
                SELECT
                    id,
                    value,
                    funds_approval_id,
                    source_id,
                FROM s3(cred_s3, url = s3m_srinfo('partnership_sourceamount', today()))
            ) sourceamount
                ON main.id = sourceamount.funds_approval_id
        -- JUNTANDO COM partnership_source --
        LEFT JOIN (
                SELECT
                    id,
                    source,
                    alias,
                FROM s3(cred_s3, url = s3m_srinfo('project_source', today()))
            ) source
                ON sourceamount.source_id = source.id
        -- JUNTANDO COM project_financingmodality --
        LEFT JOIN (
                SELECT
                    id,
                    model,
                    alias,
                FROM s3(cred_s3, url = s3m_srinfo('project_financingmodality', today()))
            ) modality
                ON ue_partnership.financing_modality_id = modality.id
        -- JUNTANDO COM ue_negotiation --
        LEFT JOIN (
                SELECT
                    id,
                    code,
                    status,
                    converted_project_id,
                    originating_prospect_id,
                    ue_id,
                FROM s3(cred_s3, url = s3m_srinfo('ue_negotiation', today()))
            ) negotiation
                ON ue_partnership.negotiation_id = negotiation.id
        -- JUNTANDO COM ue_unit --
        LEFT JOIN (
                SELECT
                    id,
                    name,
                    uf_state,
                    city,
                    action_plan_signature,
                FROM s3(cred_s3, url = s3m_srinfo('ue_unit', today()))
            ) unit
                ON negotiation.ue_id = unit.id
        -- JUNTANDO COM project_project --
        LEFT JOIN (
                SELECT
                    id,
                    code,
                    status,
                FROM s3(cred_s3, url = s3m_srinfo('project_project', today()))
            ) proj
                ON negotiation.converted_project_id = proj.id
        -- JUNTANDO COM project_contract -- 
        LEFT JOIN (
                SELECT
                    id,
                    project_related_id,
                    contract_date,
                    financing_modality_id,
                    embrapii_amount,
                    company_amount,
                    ue_amount,
                    total_amount,
                FROM s3(cred_s3, url = s3m_srinfo('project_contract', today()))
            ) contr
                ON proj.id = contr.project_related_id
        -- JUNTANDO COM ue_technicalproposal --
        LEFT JOIN (
                SELECT
                    id,
                    negotiation_related_id,
                    objectives,
                FROM s3(cred_s3, url = s3m_srinfo('ue_technicalproposal', today()))
            ) tp
                ON negotiation.id = tp.negotiation_related_id
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
            techproposal_objectives
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
