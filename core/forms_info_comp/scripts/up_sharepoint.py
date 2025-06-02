import os
import zipfile
import inspect
from dotenv import load_dotenv
from office365_api.upload_files import upload_files
from datetime import datetime

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
STEP1 = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup'))

#Sharepoint
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

def zipar_arquivos(origem, destino):
    current_datetime = datetime.now().strftime('%Y.%m.%d_%Hh%Mm%Ss')
    arquivo_zip = os.path.join(destino, f'info_comp_{current_datetime}.zip')

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
        zipar_arquivos(STEP1, BACKUP)
        upload_files(BACKUP, "DWPII_backup", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
        upload_files(STEP3, "DWPII/info_comp", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")


