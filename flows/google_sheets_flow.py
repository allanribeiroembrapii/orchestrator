from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar o módulo main diretamente
from core.atualizar_google_sheets.main import main as atualizar_sheets_main


@task(name="Atualizar Google Sheets", retries=2)
def atualizar_sheets_task():
    """Task para atualizar o Google Sheets com dados do SharePoint."""
    logger = get_run_logger()
    logger.info("Iniciando atualização do Google Sheets...")

    # Chamar a função main sem parâmetros - ela busca suas próprias configurações
    resultado = atualizar_sheets_main()

    if resultado:
        logger.info("Atualização do Google Sheets concluída com sucesso.")
    else:
        logger.error("Falha na atualização do Google Sheets.")

    return resultado


@flow(name="Pipeline de Atualização do Google Sheets")
def google_sheets_flow():
    """Flow para atualizar dados no Google Sheets."""
    logger = get_run_logger()
    logger.info("Iniciando pipeline de atualização do Google Sheets...")

    # Única chamada para a task que encapsula o main
    atualizar_sheets_task()

    logger.info("Pipeline de atualização do Google Sheets concluído.")
    return True
