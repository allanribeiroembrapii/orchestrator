import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'DWPII_copy'))
DWPII_UP = os.path.abspath(os.path.join(ROOT, 'DWPII_up'))
DWPII_BACKUP = os.path.abspath(os.path.join(ROOT, 'DWPII_backup'))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

SHAREPOINT_SITE_SEBRAE = os.getenv('sharepoint_url_site_sebrae')
SHAREPOINT_SITE_NAME_SEBRAE = os.getenv('sharepoint_site_name_sebrae')
SHAREPOINT_DOC_SEBRAE = os.getenv('sharepoint_doc_library_sebrae')

# Adiciona o diretório correto ao sys.path
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(PATH_OFFICE)

from download_files import get_files
from download_files import get_file
from apagar_arquivos_pasta import apagar_arquivos_pasta

def buscar_arquivos_sharepoint():
    apagar_arquivos_pasta(CURRENT_DIR)
    apagar_arquivos_pasta(DWPII_UP)
    apagar_arquivos_pasta(DWPII_BACKUP)
    
    get_file(SHAREPOINT_SITE_SEBRAE, SHAREPOINT_SITE_NAME_SEBRAE, SHAREPOINT_DOC_SEBRAE, "sebrae_bi_interno_base_2.0.xlsx",
              "Contratos SEBRAE/Transferência de Atividades (Handsover)/", CURRENT_DIR)
    get_files(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "DWPII/srinfo", CURRENT_DIR)
    print('Passou aqui')


#Executar função
if __name__ == "__main__":
    buscar_arquivos_sharepoint()