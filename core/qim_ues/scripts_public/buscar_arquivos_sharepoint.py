import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'copy'))
UP = os.path.abspath(os.path.join(ROOT, 'up'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup_qim'))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

# Adiciona o diretório correto ao sys.path
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(PATH_OFFICE)

from download_files import get_files
from download_files import get_file
from apagar_arquivos_pasta import apagar_arquivos_pasta

def buscar_arquivos_sharepoint():
    apagar_arquivos_pasta(CURRENT_DIR)
    apagar_arquivos_pasta(UP)
    apagar_arquivos_pasta(BACKUP)

    get_files(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "DWPII/qim_ues", CURRENT_DIR)


#Executar função
if __name__ == "__main__":
    buscar_arquivos_sharepoint()