import os
import sys
import inspect
from dotenv import load_dotenv

# Obter o diretório atual e o diretório raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Adicionar o diretório pai ao path para permitir importações absolutas
sys.path.append(parent_dir)

try:
    from connection.sharepoint import sharepoint_get
    from connection.api_query import api_ibge
except ImportError:
    # Tentar importações relativas
    from .sharepoint import sharepoint_get
    from .api_query import api_ibge


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
if not ROOT:
    ROOT = parent_dir

STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
if not STEP_1_DATA_RAW:
    STEP_1_DATA_RAW = "data/step_1_data_raw"

STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
if not STEP_2_STAGE_AREA:
    STEP_2_STAGE_AREA = "data/step_2_stage_area"

STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")
if not STEP_3_DATA_PROCESSED:
    STEP_3_DATA_PROCESSED = "data/step_3_data_processed"


def get_data():
    print("🟡 " + inspect.currentframe().f_code.co_name)
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
    print("🟢 " + inspect.currentframe().f_code.co_name)
