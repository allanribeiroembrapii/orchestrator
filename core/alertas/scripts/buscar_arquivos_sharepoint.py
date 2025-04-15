import os
import sys
from dotenv import load_dotenv
import inspect

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
DIR_PLANILHAS_ATRASOS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'planilhas'))
DIR_PLANILHAS = os.path.abspath(os.path.join(ROOT, 'copy_sharepoint_atual'))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'connection', 'office365_api'))

SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

from download_files import get_file

def buscar_arquivos_sharepoint():
    """
    Função para buscar arquivos específicos do Sharepoint.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "portfolio.xlsx", "DWPII/srinfo", DIR_PLANILHAS)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "registro_alertas.xlsx", "DWPII/alertas", DIR_PLANILHAS)
        get_file(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "macroentregas.xlsx", "DWPII/srinfo", DIR_PLANILHAS_ATRASOS)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")