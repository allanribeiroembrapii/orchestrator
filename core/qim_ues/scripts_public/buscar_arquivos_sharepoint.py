import os
from dotenv import load_dotenv
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta
from office365_api.download_files import get_files

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT_QIM_UES')

#Definição dos caminhos
COPY = os.path.abspath(os.path.join(ROOT, 'copy'))
UP = os.path.abspath(os.path.join(ROOT, 'up'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup_qim'))
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')


def buscar_arquivos_sharepoint():
    apagar_arquivos_pasta(COPY)
    apagar_arquivos_pasta(UP)
    apagar_arquivos_pasta(BACKUP)
    get_files(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "DWPII/qim_ues", COPY)

