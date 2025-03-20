from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.qim_ues.main import qim_ues


@task(name="Executar Pipeline QIM UES", retries=1)
def executar_qim_ues_task(buscar=True, baixar=True, manipular=True, levar=True):
    """
    Task para executar o pipeline QIM UES.

    Args:
        buscar: Indica se deve buscar os arquivos
        baixar: Indica se deve baixar os arquivos
        manipular: Indica se deve manipular os dados
        levar: Indica se deve levar os resultados para o SharePoint
    """
    logger = get_run_logger()
    logger.info("Executando pipeline QIM UES...")
    qim_ues(buscar=buscar, baixar=baixar, manipular=manipular, levar=levar)
    return True


@flow(name="Pipeline QIM UES")
def qim_ues_flow(buscar=True, baixar=True, manipular=True, levar=True):
    """
    Flow para executar o pipeline QIM UES.

    Args:
        buscar: Indica se deve buscar os arquivos
        baixar: Indica se deve baixar os arquivos
        manipular: Indica se deve manipular os dados
        levar: Indica se deve levar os resultados para o SharePoint
    """
    logger = get_run_logger()
    logger.info("Iniciando pipeline QIM UES...")

    executar_qim_ues_task(
        buscar=buscar, baixar=baixar, manipular=manipular, levar=levar
    )

    logger.info("Pipeline QIM UES concluído.")
    return True
