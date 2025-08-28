import os
import inspect
from dotenv import load_dotenv
from .office365.download_files import get_file
from .office365.upload_files import upload_files
from core.classificacao_financeira.connection.connect_sharepoint import SharepointClient

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_CLASSIFICACAO_FINANCEIRA")
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

        sp = SharepointClient()

        pasta_srinfo = "DWPII/srinfo"
        pasta_dw_pii = "dw_pii"
        pasta_general = "General/Agenda de Dados Financeiros"

        lista_arquivos = {
            pasta_srinfo: {
                "portfolio",
            },
            pasta_dw_pii: {
                "agfin_projetos_modelo_tradicional_classificacao_financeira",
                "portfolio2",
            },
            pasta_general: {
                "[GEPES25-038] Agenda de Dados Financeiros - Base Ouro",
            }
        }

        for pasta, nomes in lista_arquivos.items():
            for nome in nomes:
                filename = f"{nome}.xlsx"
                remote_path = f"{pasta}/{filename}"
                local_file = os.path.join(data_raw, filename)
                print(f"⬇️  Baixando: {remote_path} -> {local_file}")
                sp.download_file(remote_path, local_file)


        # get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "portfolio.xlsx", "DWPII/srinfo", data_raw)
        # get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "agfin_projetos_modelo_tradicional_classificacao_financeira.xlsx", "dw_pii", data_raw)
        # get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "portfolio2.xlsx", "dw_pii", data_raw)
        # get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "[GEPES25-038] Agenda de Dados Financeiros - Base Ouro.xlsx", "General/Agenda de Dados Financeiros", data_raw)
        # get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "CG_Classificação de Projetos.xlsx", "DWPII/srinfo", data_raw)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro ao baixar arquivos do SharePoint: {e}")
        raise



def sharepoint_post():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        sp = SharepointClient()

        # Listar arquivos na pasta
        for nome_arquivo in os.listdir(STEP_3_DATA_PROCESSED):
            caminho_do_arquivo = os.path.join(STEP_3_DATA_PROCESSED, nome_arquivo)
            if os.path.isfile(caminho_do_arquivo):
                sp.upload_file_to_folder(caminho_do_arquivo, 'dw_pii')

        # upload_files(
        #     STEP_3_DATA_PROCESSED, "dw_pii", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
        # )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")