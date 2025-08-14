import pandas as pd
from dotenv import load_dotenv
import os
import inspect
import win32com.client as win32

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_SAP_REPASSE")
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")
AGFIN_REFERENCIA = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, '[GEPES25-038] Agenda de Dados Financeiros - Base Ouro.xlsx'))
SAP_RAW = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'sap_raw.xlsx'))
SAP_PRO = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, 'agfin_sap_repasses.xlsx'))

def classificar_repasses():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Ler os DataFrames
    df_agfin_referencia = pd.read_excel(AGFIN_REFERENCIA, sheet_name='referencia_sap_repasses')
    df_sap_raw = pd.read_excel(SAP_RAW)

    # Criar coluna 'concatenado' no df_sap_raw com junção simples dos textos
    colunas_para_concatenar = [
        'modalidade', 'tpcontrato', 'parceria', 
        'contrato', 'contratomin', 'foco', 'focoabrev', 'focoabrvcontrato'
    ]
    df_sap_raw['concatenado'] = df_sap_raw[colunas_para_concatenar].astype(str).agg(''.join, axis=1)

    # Criar a versão "sap_pro" fazendo merge tipo PROCV
    df_agfin_referencia['concatenado'] = df_agfin_referencia['concatenado'].astype(str)
    df_sap_raw['concatenado'] = df_sap_raw['concatenado'].astype(str)

    df_sap_pro = pd.merge(
        df_sap_raw,
        df_agfin_referencia[[
            'concatenado',
            'id_parceiro',
            'parceiro',
            'ncf_aporte_embrapii_macro_contrato',
            'ncf_aporte_embrapii_contrato',
            'ncf_aporte_embrapii_eixo',
            'ncf_aporte_embrapii_eixo_regra'
        ]],
        on='concatenado',
        how='left'
    )

    # Renomear colunas
    df_sap_pro = df_sap_pro.rename(columns={
        'id_parceiro': 'ncf_id_parceiro',
        'parceiro': 'ncf_parceiro'
    })

    # Remover a coluna 'concatenado'
    df_sap_pro.drop(columns='concatenado', inplace=True)

    # Exportar para Excel
    df_sap_pro.to_excel(SAP_PRO, index=False)
    print("🟢 " + inspect.currentframe().f_code.co_name)

