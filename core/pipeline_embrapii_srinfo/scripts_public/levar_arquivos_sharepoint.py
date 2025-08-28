import os
import sys
from dotenv import load_dotenv
from .connect_sharepoint import SharepointClient
import inspect

# carregar .env
load_dotenv()
# Carrega o .env da raiz do projeto para obter ROOT_PIPELINE
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
ROOT = os.getenv("ROOT_PIPELINE")

# Definição dos caminhos
PASTA_ARQUIVOS = os.path.abspath(os.path.join(ROOT, "DWPII_up"))
DWII_COPY = os.path.abspath(os.path.join(ROOT, "DWPII_copy"))
DWII_BACKUP = os.path.abspath(os.path.join(ROOT, "DWPII_backup"))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, "office365_api"))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")

from office365_api.upload_files import upload_files
from scripts_public.zipar_arquivos import zipar_arquivos
from scripts_public.criar_db_sqlite import gerar_db_sqlite


def levar_arquivos_sharepoint():

    # # gerar_db_sqlite()
    # zipar_arquivos(DWII_COPY, DWII_BACKUP)
    # # upload_files(DWII_BACKUP, "DWPII_backup", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)


    # upload_files(
    #     PASTA_ARQUIVOS, "DWPII/srinfo", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
    # )

    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        sp = SharepointClient()

        # Listar arquivos na pasta
        for nome_arquivo in os.listdir(PASTA_ARQUIVOS):
            caminho_do_arquivo = os.path.join(PASTA_ARQUIVOS, nome_arquivo)
            if os.path.isfile(caminho_do_arquivo):
                sp.upload_file_to_folder(caminho_do_arquivo, 'DWPII/srinfo')
    except Exception as e:
        print(f"🔴 Erro: {e}")


# Executar função
if __name__ == "__main__":
    levar_arquivos_sharepoint()
