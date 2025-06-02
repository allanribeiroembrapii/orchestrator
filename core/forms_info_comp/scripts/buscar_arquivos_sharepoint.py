import os
from dotenv import load_dotenv
import inspect

# carregar .env
load_dotenv()
ROOT = os.getenv("ROOT")

# Definição dos caminhos
STEP1 = os.path.abspath(os.path.join(ROOT, "step_1_data_raw"))
STEP2 = os.path.abspath(os.path.join(ROOT, "step_2_stage_area"))
STEP3 = os.path.abspath(os.path.join(ROOT, "step_3_data_processed"))
BACKUP = os.path.abspath(os.path.join(ROOT, "backup"))

SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")


from office365_api.download_files import get_file, get_files
from scripts.apagar_arquivos_pasta import apagar_arquivos_pasta


def buscar_arquivos_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    apagar_arquivos_pasta(STEP1)
    apagar_arquivos_pasta(STEP2)
    apagar_arquivos_pasta(STEP3)
    apagar_arquivos_pasta(BACKUP)

    get_file(
        SHAREPOINT_SITE,
        SHAREPOINT_SITE_NAME,
        SHAREPOINT_DOC,
        "srinfo_partnership_fundsapproval.xlsx",
        "dw_pii",
        STEP1,
    )

    get_files(
        SHAREPOINT_SITE,
        SHAREPOINT_SITE_NAME,
        SHAREPOINT_DOC,
        "DWPII/info_comp",
        STEP1
    )

    print("🟢 " + inspect.currentframe().f_code.co_name)

# Executar função
if __name__ == "__main__":
    buscar_arquivos_sharepoint()
