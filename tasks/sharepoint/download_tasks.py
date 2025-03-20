from prefect import task, get_run_logger
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, "office365_api"))

# Adicionar caminho ao sys.path
sys.path.append(PATH_OFFICE)


@task(name="Baixar Arquivos do SharePoint", retries=2, retry_delay_seconds=60)
def download_sharepoint_files_task(folder, destination):
    """Task para baixar arquivos do SharePoint."""
    logger = get_run_logger()
    logger.info(f"Baixando arquivos do SharePoint da pasta {folder} para {destination}")

    # Importar função do módulo existente
    from office365_api.download_files import get_files

    # Configurar variáveis
    SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
    SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
    SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")

    # Executar download
    try:
        get_files(
            SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, folder, destination
        )
        logger.info(f"Download concluído com sucesso: {folder}")
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar arquivos: {str(e)}")
        raise
