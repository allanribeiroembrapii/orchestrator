from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.projeto.sebrae.main_sebrae import main_sebrae
from core.analises_relatorios.projetos_contratados.main_projetos_contratados import (
    main_projetos_contratados,
)
from core.projeto.projetos_empresas.main_projetos_empresas import main_projetos_empresas
from core.projeto.projetos.main_projetos import main_projetos
from core.projeto.contratos.main_contratos import main_contratos
from core.projeto.estudantes.main_estudantes import main_estudantes
from core.projeto.pedidos_pi.main_pedidos_pi import main_pedidos_pi
from core.projeto.macroentregas.main_macroentregas import main_macroentregas


@task(name="Processar Dados do Sebrae", retries=1)
def processar_sebrae_task(driver):
    """Task para processar dados do Sebrae."""
    logger = get_run_logger()
    logger.info("Processando dados do Sebrae...")
    main_sebrae(driver)
    return True


@task(name="Processar Projetos Contratados", retries=1)
def processar_projetos_contratados_task(driver):
    """Task para processar projetos contratados."""
    logger = get_run_logger()
    logger.info("Processando projetos contratados...")
    main_projetos_contratados(driver)
    return True


@task(name="Processar Projetos de Empresas", retries=1)
def processar_projetos_empresas_task():
    """Task para processar projetos de empresas."""
    logger = get_run_logger()
    logger.info("Processando projetos de empresas...")
    main_projetos_empresas()
    return True


@task(name="Processar Projetos", retries=1)
def processar_projetos_task(driver):
    """Task para processar projetos."""
    logger = get_run_logger()
    logger.info("Processando projetos...")
    main_projetos(driver)
    return True


@task(name="Processar Contratos", retries=1)
def processar_contratos_task(driver):
    """Task para processar contratos."""
    logger = get_run_logger()
    logger.info("Processando contratos...")
    main_contratos(driver)
    return True


@task(name="Processar Estudantes", retries=1)
def processar_estudantes_task(driver):
    """Task para processar estudantes."""
    logger = get_run_logger()
    logger.info("Processando estudantes...")
    main_estudantes(driver)
    return True


@task(name="Processar Pedidos PI", retries=1)
def processar_pedidos_pi_task(driver):
    """Task para processar pedidos PI."""
    logger = get_run_logger()
    logger.info("Processando pedidos PI...")
    main_pedidos_pi(driver)
    return True


@task(name="Processar Macroentregas", retries=1)
def processar_macroentregas_task(driver):
    """Task para processar macroentregas."""
    logger = get_run_logger()
    logger.info("Processando macroentregas...")
    main_macroentregas(driver)
    return True


@flow(name="Pipeline de Projetos")
def projeto_flow(driver, log=None, selected_modules=None):
    """
    Flow para processar dados de projetos.

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
            "sebrae",
            "projetos_contratados",
            "projetos_empresas",
            "projetos",
            "contratos",
            "estudantes",
            "pedidos_pi",
            "macroentregas",
        ]

    # Sebrae
    if "sebrae" in selected_modules:
        logger.info("Executando módulo: sebrae")
        processar_sebrae_task(driver)
        log.append("sebrae")

    # Projetos Contratados
    if "projetos_contratados" in selected_modules:
        logger.info("Executando módulo: projetos_contratados")
        processar_projetos_contratados_task(driver)
        log.append("projetos_contratados")

    # Projetos Empresas
    if "projetos_empresas" in selected_modules:
        logger.info("Executando módulo: projetos_empresas")
        processar_projetos_empresas_task()
        log.append("projetos_empresas")

    # Projetos
    if "projetos" in selected_modules:
        logger.info("Executando módulo: projetos")
        processar_projetos_task(driver)
        log.append("projetos")

    # Contratos
    if "contratos" in selected_modules:
        logger.info("Executando módulo: contratos")
        processar_contratos_task(driver)
        log.append("contratos")

    # Estudantes
    if "estudantes" in selected_modules:
        logger.info("Executando módulo: estudantes")
        processar_estudantes_task(driver)
        log.append("estudantes")

    # Pedidos PI
    if "pedidos_pi" in selected_modules:
        logger.info("Executando módulo: pedidos_pi")
        processar_pedidos_pi_task(driver)
        log.append("pedidos_pi")

    # Macroentregas
    if "macroentregas" in selected_modules:
        logger.info("Executando módulo: macroentregas")
        processar_macroentregas_task(driver)
        log.append("macroentregas")

    return log
