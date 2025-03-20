from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.unidade_embrapii.info_unidades.main_info_unidades import main_info_unidades
from core.unidade_embrapii.equipe_ue.main_equipe_ue import main_equipe_ue
from core.unidade_embrapii.termos_cooperacao.main_termos_cooperacao import (
    main_termos_cooperacao,
)
from core.unidade_embrapii.plano_acao.main_plano_acao import main_plano_acao
from core.ue_peo.update_process import main as ue_peo_update


@task(name="Baixar Informações de Unidades", retries=2)
def baixar_info_unidades_task(driver):
    """Task para baixar informações de unidades EMBRAPII."""
    logger = get_run_logger()
    logger.info("Baixando informações de unidades EMBRAPII...")
    main_info_unidades(driver)
    return True


@task(name="Processar Equipe UE", retries=1)
def processar_equipe_ue_task(driver):
    """Task para processar equipe de unidades EMBRAPII."""
    logger = get_run_logger()
    logger.info("Processando equipe de unidades EMBRAPII...")
    main_equipe_ue(driver)
    return True


@task(name="Processar Termos de Cooperação", retries=1)
def processar_termos_cooperacao_task(driver):
    """Task para processar termos de cooperação."""
    logger = get_run_logger()
    logger.info("Processando termos de cooperação...")
    main_termos_cooperacao(driver)
    return True


@task(name="Processar Plano de Ação", retries=1)
def processar_plano_acao_task(driver):
    """Task para processar plano de ação."""
    logger = get_run_logger()
    logger.info("Processando plano de ação...")
    main_plano_acao(driver)
    return True


@task(name="Atualizar Classificação PEO", retries=1)
def atualizar_ue_peo_task():
    """Task para atualizar classificação PEO de unidades."""
    logger = get_run_logger()
    logger.info("Atualizando classificação PEO de unidades...")
    ue_peo_update()
    return True


@flow(name="Pipeline de Unidades EMBRAPII")
def unidade_embrapii_flow(driver, log=None, selected_modules=None):
    """
    Flow para processar dados de unidades EMBRAPII.

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
        selected_modules = [
            "info_unidades",
            "equipe_ue",
            "termos_cooperacao",
            "plano_acao",
            "ue_peo",
        ]

    # Info Unidades
    if "info_unidades" in selected_modules:
        logger.info("Executando módulo: info_unidades")
        baixar_info_unidades_task(driver)
        log.append("info_unidades")

    # Equipe UE
    if "equipe_ue" in selected_modules:
        logger.info("Executando módulo: equipe_ue")
        processar_equipe_ue_task(driver)
        log.append("equipe_ue")

    # Termos Cooperação
    if "termos_cooperacao" in selected_modules:
        logger.info("Executando módulo: termos_cooperacao")
        processar_termos_cooperacao_task(driver)
        log.append("termos_cooperacao")

    # Plano Ação
    if "plano_acao" in selected_modules:
        logger.info("Executando módulo: plano_acao")
        processar_plano_acao_task(driver)
        log.append("plano_acao")

    # UE PEO
    if "ue_peo" in selected_modules:
        logger.info("Executando módulo: ue_peo")
        atualizar_ue_peo_task()
        log.append("ue_peo")

    return log
