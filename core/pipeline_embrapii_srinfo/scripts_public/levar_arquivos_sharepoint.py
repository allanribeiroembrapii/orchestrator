import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PASTA_ARQUIVOS = os.path.abspath(os.path.join(ROOT, 'DWPII_up'))
DWII_COPY = os.path.abspath(os.path.join(ROOT, 'DWPII_copy'))
DWII_BACKUP = os.path.abspath(os.path.join(ROOT, 'DWPII_backup'))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

from upload_files import upload_files
from zipar_arquivos import zipar_arquivos
from criar_db_sqlite import gerar_db_sqlite

def levar_arquivos_sharepoint():

    # gerar_db_sqlite()
    zipar_arquivos(DWII_COPY, DWII_BACKUP)
    upload_files(DWII_BACKUP, "DWPII_backup", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
    upload_files(PASTA_ARQUIVOS, "DWPII/srinfo", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)

#Executar função
if __name__ == "__main__":
    levar_arquivos_sharepoint()
