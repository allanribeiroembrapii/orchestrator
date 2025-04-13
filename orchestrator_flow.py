import os
import sys
import subprocess
from datetime import timedelta
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.server.schemas.schedules import CronSchedule

# Adicionar o diretório raiz do projeto ao PATH
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)


@task(
    name="Executar Script",
    retries=2,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def executar_script(nome_script, caminho_script):
    """Executa um script Python."""
    logger = get_run_logger()
    logger.info(f"Iniciando execução do script: {nome_script}")

    try:
        # Executa o script Python diretamente
        result = subprocess.run(
            [sys.executable, caminho_script], capture_output=True, text=True, check=True
        )
        logger.info(f"Script {nome_script} executado com sucesso!")
        logger.debug(f"Saída: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar {nome_script}: {e}")
        logger.error(f"Saída de erro: {e.stderr}")
        raise Exception(f"Falha na execução do script {nome_script}")


@flow(name="Orquestrador EMBRAPII", description="Orquestrador dos scripts EMBRAPII em sequência")
def orquestrador_flow(run_pipeline=True, run_google_sheets=True, run_api_datapii=True):
    """
    Flow principal que orquestra a execução dos scripts EMBRAPII em sequência.

    Args:
        run_pipeline (bool): Se deve executar o script pipeline_embrapii_srinfo
        run_google_sheets (bool): Se deve executar o script atualizar_google_sheets
        run_api_datapii (bool): Se deve executar o script api_datapii
    """
    logger = get_run_logger()
    logger.info("Iniciando orquestrador de scripts EMBRAPII")

    # Definir caminhos para os scripts
    pipeline_script = os.path.join(ROOT_DIR, "core", "pipeline_embrapii_srinfo", "main.py")
    google_sheets_script = os.path.join(ROOT_DIR, "core", "atualizar_google_sheets", "main.py")
    api_datapii_script = os.path.join(ROOT_DIR, "core", "api_datapii", "main.py")

    # Executar em sequência
    if run_pipeline:
        pipeline_result = executar_script("pipeline_embrapii_srinfo", pipeline_script)
        # Só continua se o script anterior tiver sucesso
        if not pipeline_result:
            logger.error("Pipeline SRInfo falhou. Interrompendo sequência.")
            return False

    if run_google_sheets:
        google_sheets_result = executar_script("atualizar_google_sheets", google_sheets_script)
        if not google_sheets_result:
            logger.error("Atualização Google Sheets falhou. Interrompendo sequência.")
            return False

    if run_api_datapii:
        api_datapii_result = executar_script("api_datapii", api_datapii_script)
        if not api_datapii_result:
            logger.error("API DataPII falhou.")
            return False

    logger.info("Sequência de scripts EMBRAPII concluída com sucesso!")
    return True


# Flow para execução diária (todos os scripts)
@flow(name="Orquestrador Diário EMBRAPII")
def orquestrador_diario():
    """Flow diário que executa todos os scripts em sequência."""
    return orquestrador_flow(run_pipeline=True, run_google_sheets=True, run_api_datapii=True)


# Flow para execução quinzenal (apenas pipeline_embrapii_srinfo)
@flow(name="Orquestrador Quinzenal EMBRAPII")
def orquestrador_quinzenal():
    """Flow quinzenal que executa apenas o pipeline embrapii_srinfo."""
    return orquestrador_flow(run_pipeline=True, run_google_sheets=False, run_api_datapii=False)


if __name__ == "__main__":
    # Execução manual do flow
    # orquestrador_flow()

    # Criar deployments usando o método serve()
    print("Criando deployment diário...")
    orquestrador_diario.serve(
        name="EMBRAPII - Sequência Diária",
        cron="0 8 * * *",  # Executa todos os dias às 8:00 da manhã
        tags=["embrapii", "diario"],
        description="Executa diariamente os scripts pipeline_embrapii_srinfo, atualizar_google_sheets e api_datapii em sequência",
    )
