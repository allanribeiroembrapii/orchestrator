from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.projeto.classificacao_projeto.main_classificacao_projeto import (
    main_classificacao_projeto,
)
from core.cg_classificacao_projetos.main import main as main_cg_classificacao_projetos


@task(name="Processar Classificação de Projetos", retries=1)
def processar_classificacao_projetos_task():
    """Task para processar classificação de projetos."""
    logger = get_run_logger()
    logger.info("Processando classificação de projetos...")
    main_classificacao_projeto()
    return True


@task(name="Processar Classificação CG de Projetos", retries=1)
def processar_cg_classificacao_projetos_task():
    """Task para processar classificação CG de projetos."""
    logger = get_run_logger()
    logger.info("Processando classificação CG de projetos...")
    main_cg_classificacao_projetos()
    return True


@flow(name="Pipeline de Classificação de Projetos")
def classificacao_flow(log=None, selected_modules=None):
    """
    Flow para processar classificação de projetos.

    Args:
        log: Lista de logs para registrar
        selected_modules: Lista de módulos selecionados para execução

    Returns:
        log: Lista atualizada de logs
    """
    logger = get_run_logger()

    if log is None:
        log = []

    if selected_modules is None:
        selected_modules = ["classificacao_projetos", "cg_classificacao_projetos"]

    # Classificação Projetos
    if "classificacao_projetos" in selected_modules:
        logger.info("Executando módulo: classificacao_projetos")
        processar_classificacao_projetos_task()
        log.append("classificacao_projetos")

    # Classificação CG de Projetos
    if "cg_classificacao_projetos" in selected_modules:
        logger.info("Executando módulo: cg_classificacao_projetos")
        processar_cg_classificacao_projetos_task()
        log.append("cg_classificacao_projetos")

    return log
