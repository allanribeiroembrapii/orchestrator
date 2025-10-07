import os
import zipfile
import inspect
from dotenv import load_dotenv
from .office365.upload_files import upload_files
from datetime import datetime

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')
STEP1 = os.getenv('STEP_1_DATA_RAW')
STEP3 = os.getenv('STEP_3_DATA_PROCESSED')

#Definição dos caminhos
PASTA_ARQUIVOS = os.path.abspath(os.path.join(ROOT, STEP3))
RAW = os.path.abspath(os.path.join(ROOT, STEP1))
BACKUP = os.path.abspath(os.path.join(ROOT, "data/backup"))

#Sharepoint
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')


def zipar_arquivos(origem, destino):
    current_datetime = datetime.now().strftime('%Y.%m.%d_%Hh%Mm%Ss')
    arquivo_zip = os.path.join(destino, f'oni_querys_{current_datetime}.zip')

    # Cria um objeto ZipFile no modo de escrita
    with zipfile.ZipFile(arquivo_zip, 'w') as zipf:
        # Percorre todos os arquivos da pasta
        for root, dirs, files in os.walk(origem):
            for file in files:
                # Caminho completo do arquivo
                file_path = os.path.join(root, file)
                # Adiciona o arquivo ao ZIP, preservando a estrutura de pastas
                zipf.write(file_path, os.path.relpath(file_path, origem))


def up_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        zipar_arquivos(RAW, BACKUP)
        upload_files(BACKUP, "DWPII_backup", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
        upload_files(PASTA_ARQUIVOS, "dw_pii", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")


