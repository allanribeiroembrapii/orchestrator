from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.scripts_public.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from core.scripts_public.levar_arquivos_sharepoint import (
    levar_arquivos_sharepoint as levar_arquivos,
)


@task(name="Buscar Arquivos do SharePoint", retries=2)
def buscar_arquivos_sharepoint_task():
    """Task para buscar arquivos do SharePoint."""
    logger = get_run_logger()
    logger.info("Buscando arquivos do SharePoint...")
    buscar_arquivos_sharepoint()
    return True


@task(name="Levar Arquivos para o SharePoint", retries=2)
def levar_arquivos_sharepoint_task():
    """Task para levar arquivos para o SharePoint."""
    logger = get_run_logger()
    logger.info("Enviando arquivos para o SharePoint...")
    levar_arquivos()
    return True


@flow(name="Pipeline de Busca de Arquivos do SharePoint")
def buscar_arquivos_sharepoint_flow():
    """Flow para buscar arquivos do SharePoint."""
    logger = get_run_logger()
    logger.info("Iniciando busca de arquivos do SharePoint...")
    buscar_arquivos_sharepoint_task()
    logger.info("Busca de arquivos do SharePoint concluída.")
    return True


@flow(name="Pipeline de Envio de Arquivos para o SharePoint")
def levar_arquivos_sharepoint_flow():
    """Flow para levar arquivos para o SharePoint."""
    logger = get_run_logger()
    logger.info("Iniciando envio de arquivos para o SharePoint...")
    levar_arquivos_sharepoint_task()
    logger.info("Envio de arquivos para o SharePoint concluído.")
    return True
