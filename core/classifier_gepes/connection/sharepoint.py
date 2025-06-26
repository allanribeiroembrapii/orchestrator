import os
import inspect
from dotenv import load_dotenv
from .office365.download_files import get_file
from .office365.upload_files import upload_files

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_CLASSIFIER_GEPES")
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")
STEP_3_DATA_PROCESSED = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED))

# puxar planilhas do sharepoint
def get_files_from_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Baixar arquivos do SharePoint
    try:
        data_raw = os.path.join(ROOT, STEP_1_DATA_RAW)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "portfolio.xlsx", "DWPII/srinfo", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "agfin_projetos_modelo_tradicional_classificacao_financeira.xlsx", "dw_pii", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "[GEPES25-038] Agenda de Dados Financeiros - Base Ouro.xlsx", "General/Agenda de Dados Financeiros", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "CG_Classificação de Projetos.xlsx", "DWPII/srinfo", data_raw)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro ao baixar arquivos do SharePoint: {e}")
        raise



def sharepoint_post():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        upload_files(
            STEP_3_DATA_PROCESSED, "dw_pii", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
        )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")