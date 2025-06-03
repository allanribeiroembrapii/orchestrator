import os
import inspect
from dotenv import load_dotenv
from .office365.download_files import get_file
from .office365.upload_files import upload_files

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_BMAISP")
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
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "portfolio.xlsx", "DWPII/srinfo", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "classificacao_projeto.xlsx", "DWPII/srinfo", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "informacoes_empresas.xlsx", "DWPII/srinfo", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "projetos_empresas.xlsx", "DWPII/srinfo", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "cnae_ibge.xlsx", "DWPII/lookup_tables", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "bmaisp_embrapii.xlsx", "DWPII/brasil_mais_produtivo", data_raw)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "naobmaisp_portfolio.xlsx", "DWPII/brasil_mais_produtivo", data_raw)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro ao baixar arquivos do SharePoint: {e}")
        raise



def sharepoint_post():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        upload_files(
            "data\\step_3_data_processed", "DWPII/brasil_mais_produtivo", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
        )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")