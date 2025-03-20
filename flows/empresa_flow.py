from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.empresa.info_empresas.main_info_empresas import main as main_info_empresas
from core.analises_relatorios.empresas_contratantes.main_empresas_contratantes import (
    main_empresas_contratantes,
)
from core.scripts_public.registrar_log import registrar_log


@task(name="Processar Informações de Empresas", retries=2)
def processar_info_empresas_task(driver):
    """
    Task para processar informações de empresas.
    Usa configurações automáticas do módulo.

    Args:
        driver: WebDriver configurado
    """
    logger = get_run_logger()
    logger.info("Processando informações de empresas...")

    resultado = main_info_empresas(driver=driver)

    if resultado:
        logger.info("Processamento de informações de empresas concluído com sucesso.")
    else:
        logger.error("Falha no processamento de informações de empresas.")

    return resultado


@task(name="Processar Empresas Contratantes", retries=1)
def processar_empresas_contratantes_task(driver):
    """Task para processar empresas contratantes."""
    logger = get_run_logger()
    logger.info("Processando empresas contratantes...")
    main_empresas_contratantes(driver)
    return True


@flow(name="Pipeline de Empresas")
def empresa_flow(driver, log=None, selected_modules=None):
    """
    Flow para processar dados de empresas.

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
        selected_modules = ["info_empresas", "empresas_contratantes"]

    # Info Empresas
    if "info_empresas" in selected_modules:
        logger.info("Executando módulo: info_empresas")
        processar_info_empresas_task(driver)
        log.append("info_empresas")

    # Empresas Contratantes
    if "empresas_contratantes" in selected_modules:
        logger.info("Executando módulo: empresas_contratantes")
        processar_empresas_contratantes_task(driver)
        log.append("empresas_contratantes")

    return log
