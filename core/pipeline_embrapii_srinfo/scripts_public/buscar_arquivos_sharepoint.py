import os
import sys
from dotenv import load_dotenv
import inspect
import requests
import pandas as pd
from .connect_sharepoint import SharepointClient
import inspect
import requests
from requests.exceptions import Timeout, RequestException

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

    sp = SharepointClient()
    pasta_origem = "DWPII/srinfo"
    arquivos = sp.list_files(pasta_origem)
    for arquivo in arquivos:
        nome_arquivo = arquivo["name"]
        sp.download_file(f"{pasta_origem}/{nome_arquivo}", os.path.join(CURRENT_DIR, nome_arquivo))

    sp.download_file_from_other_site(
        site_url="embrapii.sharepoint.com:/sites/GEAEDGovernanadeContratos",
        doc_library="Documents",  # só o nome da lib
        file_path="Contratos SEBRAE/Transferência de Atividades (Handsover)/sebrae_bi_interno_base_2.0.xlsx",
        output_path=os.path.join(CURRENT_DIR, "sebrae_bi_interno_base_2.0.xlsx")
    )

    sp = SharepointClient()
    site_id = "embrapii.sharepoint.com,8b15e48e-d76c-46e3-99ed-b26938c118bc,34cff5a0-961f-4738-9269-df1fb2dac987"
    sp.listar_drives_site(site_id)

    api_ibge()
    print("🟢 " + inspect.currentframe().f_code.co_name)

# URL da API do IBGE
IPCA_IBGE = "https://apisidra.ibge.gov.br/values/t/1737/p/all/v/2266/N1/1?formato=json"


def api_ibge():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        response = requests.get(IPCA_IBGE, timeout=10)
        response.raise_for_status()
    except Timeout:
        raise Exception("⏱️ Timeout: API do IBGE demorou para responder.")
    except RequestException as e:
        raise Exception(f"❌ Erro ao conectar com API do IBGE: {e}")

    dados = response.json()
    header = list(dados[0].values())
    data = [list(row.values()) for row in dados[1:]]

    df = pd.DataFrame(data, columns=header)
    output_path = os.path.join(CURRENT_DIR, "ipca_ibge.xlsx")
    df.to_excel(output_path, index=False)

    print("🟢 " + inspect.currentframe().f_code.co_name)


# Executar função
if __name__ == "__main__":
    buscar_arquivos_sharepoint()
