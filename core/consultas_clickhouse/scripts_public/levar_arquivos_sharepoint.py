import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PASTA_ARQUIVOS = os.path.abspath(os.path.join(ROOT, '2_data_processed'))
RAW = os.path.abspath(os.path.join(ROOT, '1_data_raw'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup'))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

from upload_files import upload_files
from consultas_clickhouse.scripts_public.zipar_arquivos import zipar_arquivos

def levar_arquivos_sharepoint():

    # gerar_db_sqlite()
    zipar_arquivos(RAW, BACKUP)
    upload_files(BACKUP, "DWPII_backup", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
    upload_files(PASTA_ARQUIVOS, "DWPII/consultas_clickhouse", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)

#Executar função
if __name__ == "__main__":
    levar_arquivos_sharepoint()
