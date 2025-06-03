import os
import sys
from dotenv import load_dotenv
import inspect
import requests
import pandas as pd

# carregar .env
load_dotenv()
# Carrega o .env da raiz do projeto para obter ROOT_PIPELINE
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
ROOT = os.getenv("ROOT_PIPELINE")

# Definição dos caminhos
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, "scripts_public"))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, "DWPII_copy"))
DWPII_UP = os.path.abspath(os.path.join(ROOT, "DWPII_up"))
DWPII_BACKUP = os.path.abspath(os.path.join(ROOT, "DWPII_backup"))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, "office365_api"))

SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")

SHAREPOINT_SITE_SEBRAE = os.getenv("sharepoint_url_site_sebrae")
SHAREPOINT_SITE_NAME_SEBRAE = os.getenv("sharepoint_site_name_sebrae")
SHAREPOINT_DOC_SEBRAE = os.getenv("sharepoint_doc_library_sebrae")

# Adiciona o diretório correto ao sys.path
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(PATH_OFFICE)

from office365_api.download_files import get_files
from office365_api.download_files import get_file
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta


def buscar_arquivos_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    apagar_arquivos_pasta(CURRENT_DIR)
    apagar_arquivos_pasta(DWPII_UP)
    apagar_arquivos_pasta(DWPII_BACKUP)

    get_file(
        SHAREPOINT_SITE_SEBRAE,
        SHAREPOINT_SITE_NAME_SEBRAE,
        SHAREPOINT_DOC_SEBRAE,
        "sebrae_bi_interno_base_2.0.xlsx",
        "Contratos SEBRAE/Transferência de Atividades (Handsover)/",
        CURRENT_DIR,
    )
    get_files(SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, "DWPII/srinfo", CURRENT_DIR)
    api_ibge()
    print("🟢 " + inspect.currentframe().f_code.co_name)

# URL da API do IBGE
IPCA_IBGE = "https://apisidra.ibge.gov.br/values/t/1737/p/all/v/2266/N1/1?formato=json"


def api_ibge():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Pegar os dados da API
    response = requests.get(IPCA_IBGE)
    if response.status_code != 200:
        raise Exception("Erro ao buscar dados da API do IBGE")

    dados = response.json()

    # Extrair cabeçalho da segunda linha (índice 1)
    header = list(dados[0].values())

    # Criar lista de dados a partir da terceira linha em diante (dados reais)
    data = [list(row.values()) for row in dados[1:]]

    # Criar DataFrame com o novo cabeçalho
    df = pd.DataFrame(data, columns=header)

    # Salvar planilha XLSX no caminho RAW
    output_path = os.path.join(CURRENT_DIR, "ipca_ibge.xlsx")
    # Garantir que o diretório existe antes de salvar o arquivo
    df.to_excel(output_path, index=False)

    print("🟢 " + inspect.currentframe().f_code.co_name)


# Executar função
if __name__ == "__main__":
    buscar_arquivos_sharepoint()
