import os
import sys
from dotenv import load_dotenv
import inspect

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')
STEP1 = os.getenv('STEP_1_DATA_RAW')

#Definição dos caminhos
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'connection'))
PATH_OFFICE = os.path.abspath(os.path.join(CURRENT_DIR, 'office365'))

SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

from connection.office365.download_files import get_file

def copy_sharepoint():    
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "oni_companies.xlsx",
                "dw_pii", STEP1)
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")


#Executar função
if __name__ == "__main__":
    copy_sharepoint()