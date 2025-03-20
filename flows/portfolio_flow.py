from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.projeto.portfolio.main_portfolio import main_portfolio


@task(name="Processar Portfolio", retries=1)
def processar_portfolio_task():
    """Task para processar portfolio."""
    logger = get_run_logger()
    logger.info("Processando portfolio...")
    main_portfolio()
    return True


@flow(name="Pipeline de Portfolio")
def portfolio_flow(log=None):
    """
    Flow para processar portfolio.

    Args:
        log: Lista de logs para registrar

    Returns:
        log: Lista atualizada de logs
    """
    logger = get_run_logger()

    if log is None:
        log = []

    logger.info("Executando módulo: portfolio")
    processar_portfolio_task()
    log.append("portfolio")

    return log
