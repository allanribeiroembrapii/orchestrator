import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório pai ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection.sharepoint import sharepoint_get
from connection.api_query import api_ibge


# Função para verificar e criar diretórios se não existirem
def verificar_criar_diretorio(caminho):
    """
    Verifica se um diretório existe e o cria se não existir.

    Args:
        caminho: Caminho do diretório a ser verificado/criado
    """
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        print(f"Diretório criado: {caminho}")


# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT_DATAPII")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")


def get_data():
    # Verificar e criar diretórios necessários
    RAW = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW))
    STAGE = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA))
    PROCESSED = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED))

    verificar_criar_diretorio(RAW)
    verificar_criar_diretorio(STAGE)
    verificar_criar_diretorio(PROCESSED)

    # Obter dados
    sharepoint_get()
    api_ibge()
