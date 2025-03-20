from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.negociacoes.negociacoes.main_negociacoes import main_negociacoes
from core.negociacoes.propostas_tecnicas.main_propostas_tecnicas import (
    main_propostas_tecnicas,
)
from core.negociacoes.planos_trabalho.main_planos_trabalho import main_planos_trabalho


@task(name="Processar Negociações", retries=1)
def processar_negociacoes_task(driver):
    """Task para processar negociações."""
    logger = get_run_logger()
    logger.info("Processando negociações...")
    main_negociacoes(driver)
    return True


@task(name="Processar Propostas Técnicas", retries=1)
def processar_propostas_tecnicas_task(driver):
    """Task para processar propostas técnicas."""
    logger = get_run_logger()
    logger.info("Processando propostas técnicas...")
    main_propostas_tecnicas(driver)
    return True


@task(name="Processar Planos de Trabalho", retries=1)
def processar_planos_trabalho_task(driver):
    """Task para processar planos de trabalho."""
    logger = get_run_logger()
    logger.info("Processando planos de trabalho...")
    main_planos_trabalho(driver)
    return True


@flow(name="Pipeline de Negociações")
def negociacoes_flow(driver, log=None, selected_modules=None):
    """
    Flow para processar dados de negociações.

    Args:
        driver: WebDriver configurado
        log: Lista de logs para registrar
        selected_modules: Lista de módulos selecionados para execução

    Returns:
        log: Lista atualizada de logs
    """
    logger = get_run_logger()

    if log is None:
        log = []

    if selected_modules is None:
        selected_modules = ["negociacoes", "propostas_tecnicas", "planos_trabalho"]

    # Negociações
    if "negociacoes" in selected_modules:
        logger.info("Executando módulo: negociacoes")
        processar_negociacoes_task(driver)
        log.append("negociacoes")

    # Propostas Técnicas
    if "propostas_tecnicas" in selected_modules:
        logger.info("Executando módulo: propostas_tecnicas")
        processar_propostas_tecnicas_task(driver)
        log.append("propostas_tecnicas")

    # Planos de Trabalho
    if "planos_trabalho" in selected_modules:
        logger.info("Executando módulo: planos_trabalho")
        processar_planos_trabalho_task(driver)
        log.append("planos_trabalho")

    return log
