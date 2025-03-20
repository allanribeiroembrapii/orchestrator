from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.consultas_clickhouse.main_consultas import main as main_consultas


@task(name="Executar Consultas ClickHouse", retries=1)
def executar_consultas_clickhouse_task(
    anexo8=True, registros_financeiros=True, repasses=True, levar=True
):
    """
    Task para executar consultas no ClickHouse.

    Args:
        anexo8: Indica se deve processar o anexo 8
        registros_financeiros: Indica se deve processar registros financeiros
        repasses: Indica se deve processar repasses
        levar: Indica se deve levar os resultados para o SharePoint
    """
    logger = get_run_logger()
    logger.info("Executando consultas no ClickHouse...")
    main_consultas(
        anexo8=anexo8,
        registros_financeiros=registros_financeiros,
        repasses=repasses,
        levar=levar,
    )
    return True


@flow(name="Pipeline de Consultas ClickHouse")
def consultas_clickhouse_flow(
    anexo8=True, registros_financeiros=True, repasses=True, levar=True
):
    """
    Flow para executar consultas no ClickHouse.

    Args:
        anexo8: Indica se deve processar o anexo 8
        registros_financeiros: Indica se deve processar registros financeiros
        repasses: Indica se deve processar repasses
        levar: Indica se deve levar os resultados para o SharePoint
    """
    logger = get_run_logger()
    logger.info("Iniciando pipeline de consultas ClickHouse...")

    executar_consultas_clickhouse_task(
        anexo8=anexo8,
        registros_financeiros=registros_financeiros,
        repasses=repasses,
        levar=levar,
    )

    logger.info("Pipeline de consultas ClickHouse concluído.")
    return True
