from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.prospeccao.comunicacao.main_comunicacao import main_comunicacao
from core.prospeccao.eventos_srinfo.main_eventos_srinfo import main_eventos_srinfo
from core.prospeccao.prospeccao.main_prospeccao import main_prospeccao


@task(name="Processar Comunicação", retries=1)
def processar_comunicacao_task(driver):
    """Task para processar dados de comunicação."""
    logger = get_run_logger()
    logger.info("Processando dados de comunicação...")
    main_comunicacao(driver)
    return True


@task(name="Processar Eventos SRInfo", retries=1)
def processar_eventos_srinfo_task(driver):
    """Task para processar eventos SRInfo."""
    logger = get_run_logger()
    logger.info("Processando eventos SRInfo...")
    main_eventos_srinfo(driver)
    return True


@task(name="Processar Prospecção", retries=1)
def processar_prospeccao_task(driver):
    """Task para processar dados de prospecção."""
    logger = get_run_logger()
    logger.info("Processando dados de prospecção...")
    main_prospeccao(driver)
    return True


@flow(name="Pipeline de Prospecção")
def prospeccao_flow(driver, log=None, selected_modules=None):
    """
    Flow para processar dados de prospecção.

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
        selected_modules = ["comunicacao", "eventos_srinfo", "prospeccao"]

    # Comunicação
    if "comunicacao" in selected_modules:
        logger.info("Executando módulo: comunicacao")
        processar_comunicacao_task(driver)
        log.append("comunicacao")

    # Eventos SRInfo
    if "eventos_srinfo" in selected_modules:
        logger.info("Executando módulo: eventos_srinfo")
        processar_eventos_srinfo_task(driver)
        log.append("eventos_srinfo")

    # Prospecção
    if "prospeccao" in selected_modules:
        logger.info("Executando módulo: prospeccao")
        processar_prospeccao_task(driver)
        log.append("prospeccao")

    return log
