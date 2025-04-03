import os
import sys
import inspect
from dotenv import load_dotenv
from .office365.download_files import get_file

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT")
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")


# puxar planilhas do sharepoint
def get_files_from_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    

    # Baixar arquivos do SharePoint
    try:
        data_raw = os.path.join(ROOT, STEP_1_DATA_RAW)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "srinfo_project.xlsx", "dw_pii", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "srinfo_negotiation.xlsx", "dw_pii", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "srinfo_unit.xlsx", "dw_pii", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "srinfo_ue_prospect.xlsx", "dw_pii", data_raw)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro ao baixar arquivos do SharePoint: {e}")
        raise

