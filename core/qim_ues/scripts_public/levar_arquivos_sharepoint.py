import os
from dotenv import load_dotenv
from scripts_public.zipar_arquivos import zipar_arquivos
from office365_api.upload_files import upload_files

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT_QIM_UES')

#Definição dos caminhos
PASTA_ARQUIVOS = os.path.abspath(os.path.join(ROOT, 'up'))
COPY = os.path.abspath(os.path.join(ROOT, 'copy'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup_qim'))
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')


def levar_arquivos_sharepoint():
    zipar_arquivos(COPY, BACKUP)
    upload_files(BACKUP, "DWPII_backup", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
    upload_files(PASTA_ARQUIVOS, "DWPII/qim_ues", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)

