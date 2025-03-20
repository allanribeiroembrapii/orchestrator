from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.scripts_public.teams_notification import enviar_notificacao_teams
from core.scripts_public.whatsapp import enviar_whatsapp


@task(name="Enviar Notificação Teams", retries=2)
def enviar_notificacao_teams_task(stats):
    """
    Task para enviar notificação para o Microsoft Teams.

    Args:
        stats: Dicionário com estatísticas do pipeline
    """
    logger = get_run_logger()
    logger.info("Enviando notificação para o Microsoft Teams...")
    result = enviar_notificacao_teams(stats)
    if result:
        logger.info("Notificação enviada para o Microsoft Teams com sucesso!")
    else:
        logger.warning("Falha ao enviar notificação para o Microsoft Teams.")
    return result


@task(name="Enviar Mensagem WhatsApp", retries=2)
def enviar_whatsapp_task(mensagem):
    """
    Task para enviar mensagem pelo WhatsApp.

    Args:
        mensagem: Texto da mensagem a ser enviada
    """
    logger = get_run_logger()
    logger.info("Enviando mensagem pelo WhatsApp...")
    result = enviar_whatsapp(mensagem)
    if result:
        logger.info("Mensagem enviada pelo WhatsApp com sucesso!")
    else:
        logger.warning("Falha ao enviar mensagem pelo WhatsApp.")
    return result


@flow(name="Pipeline de Notificação Teams")
def enviar_notificacao_teams_flow(stats):
    """
    Flow para enviar notificação para o Microsoft Teams.

    Args:
        stats: Dicionário com estatísticas do pipeline
    """
    logger = get_run_logger()
    logger.info("Iniciando pipeline de notificação Teams...")
    result = enviar_notificacao_teams_task(stats)
    logger.info("Pipeline de notificação Teams concluído.")
    return result


@flow(name="Pipeline de Notificação WhatsApp")
def enviar_whatsapp_flow(mensagem):
    """
    Flow para enviar mensagem pelo WhatsApp.

    Args:
        mensagem: Texto da mensagem a ser enviada
    """
    logger = get_run_logger()
    logger.info("Iniciando pipeline de notificação WhatsApp...")
    result = enviar_whatsapp_task(mensagem)
    logger.info("Pipeline de notificação WhatsApp concluído.")
    return result
