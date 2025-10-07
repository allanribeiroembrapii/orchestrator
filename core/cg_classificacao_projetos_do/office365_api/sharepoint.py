import os
import inspect
from dotenv import load_dotenv
from .download_files import get_file
from .upload_files import upload_files
from core.classificacao_financeira.connection.connect_sharepoint import SharepointClient

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_CG_CLASSIFICACAO_PROJETOS_DO")
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
STEP_1_DATA_RAW = os.path.join(ROOT, "step_1_data_raw")
STEP_3_DATA_PROCESSED = os.path.join(ROOT, "step_3_data_processed")

# puxar planilhas do sharepoint
def get_files_from_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Baixar arquivos do SharePoint
    try:
        data_raw =  STEP_1_DATA_RAW

        sp = SharepointClient()

        pasta_srinfo = "DWPII/srinfo"
        pasta_unidades = "DWPII/unidades_embrapii"

        lista_arquivos = {
            pasta_srinfo: {
                "portfolio",
                "classificacao_projeto",
                "CG_Classificação de Projetos",
                "negociacoes_negociacoes"
            },
            pasta_unidades: {
                "ue_fonte_recurso_prioritario"
            }
        }

        for pasta, nomes in lista_arquivos.items():
            for nome in nomes:
                filename = f"{nome}.xlsx"
                remote_path = f"{pasta}/{filename}"
                local_file = os.path.join(data_raw, filename)
                print(f"⬇️  Baixando: {remote_path} -> {local_file}")
                sp.download_file(remote_path, local_file)

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
                sp.upload_file_to_folder(caminho_do_arquivo, 'DWPII/srinfo')

        # upload_files(
        #     STEP_3_DATA_PROCESSED, "DWPII/srinfo", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
        # )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")