import os
import inspect
from dotenv import load_dotenv
from .office365.upload_files import upload_files
from .office365.download_files import get_file

# carregar .env
load_dotenv()
ROOT = os.getenv("ROOT_DATAPII")


# Sharepoint
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
REPOSITORIO_SHAREPOINT = os.getenv("sharepoint_repositorio")

# Função para verificar e criar diretórios se não existirem
def verificar_criar_diretorio(caminho):
    """
    Verifica se um diretório existe e o cria se não existir.
    
    Args:
        caminho: Caminho do diretório a ser verificado/criado
    """
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        print(f"Diretório criado: {caminho}")

# Definição dos caminhos
RAW = os.path.abspath(os.path.join(ROOT, os.getenv("STEP_1_DATA_RAW")))
DATA_PROCESSED = os.path.abspath(os.path.join(ROOT, os.getenv("STEP_3_DATA_PROCESSED")))

# Verificar e criar diretórios necessários
verificar_criar_diretorio(RAW)
verificar_criar_diretorio(DATA_PROCESSED)


def sharepoint_post():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        upload_files(
            DATA_PROCESSED, "dw_pii", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
        )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")


def sharepoint_get():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Garantir que o diretório RAW existe antes de apagar arquivos
    verificar_criar_diretorio(RAW)
    apagar_arquivos_pasta(RAW)

    get_file("portfolio.xlsx", "DWPII/srinfo", RAW)
    get_file("projetos_empresas.xlsx", "DWPII/srinfo", RAW)
    get_file("info_unidades_embrapii.xlsx", "DWPII/srinfo", RAW)
    print("🟢 " + inspect.currentframe().f_code.co_name)


def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é uma pasta; se não for, cria
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            print(f"Diretório criado: {caminho_pasta}")
            return

        # Lista todos os arquivos na pasta
        arquivos = os.listdir(caminho_pasta)

        # Apaga cada arquivo na pasta
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
    except Exception as e:
        print(f"🔴 Ocorreu um erro ao apagar os arquivos: {e}")
