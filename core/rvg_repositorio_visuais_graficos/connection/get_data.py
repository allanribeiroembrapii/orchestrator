import os
import sys
import inspect
from dotenv import load_dotenv
import shutil

from core.rvg_repositorio_visuais_graficos.connection.office365.download_files import get_files
from core.rvg_repositorio_visuais_graficos.connection.office365.upload_files import upload_files

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT_RVG")
FOLDER_XLS= os.path.abspath(os.path.join(ROOT, 'folder_xls'))
FOLDER_PPT= os.path.abspath(os.path.join(ROOT, 'folder_ppt'))

#Sharepoint
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

# Função para verificar e criar diretórios se não existirem
def start_clean(caminho):
    if os.path.exists(caminho):
        shutil.rmtree(caminho)
    os.makedirs(caminho)




def get_arquivos():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # start_clean(FOLDER_XLS)
    start_clean(FOLDER_PPT)

    # Obter dados
    # get_files("General/Repositório de Visuais Gráficos/Excel", FOLDER_XLS)
    get_files("General/Repositório de Visuais Gráficos/PowerPoint", FOLDER_PPT)
    print("🟢 " + inspect.currentframe().f_code.co_name)


def up_arquivos(path_folder, path_folder_sharepoint):
    print("🟡 " + inspect.currentframe().f_code.co_name)
    upload_files(path_folder, path_folder_sharepoint)
    print("🟢 " + inspect.currentframe().f_code.co_name)