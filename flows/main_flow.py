from prefect import flow, get_run_logger
import os
import sys
import gc
import psutil
from dotenv import load_dotenv
from datetime import datetime
from config.settings import NOTIFICATION_CONFIG

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
USUARIO = os.getenv("USERNAME")
sys.path.append(ROOT)

# Importações de flows secundários
from flows.sharepoint_flow import (
    buscar_arquivos_sharepoint_flow,
    levar_arquivos_sharepoint_flow,
)
from flows.empresa_flow import empresa_flow
from flows.unidade_embrapii_flow import unidade_embrapii_flow
from flows.projeto_flow import projeto_flow
from flows.prospeccao_flow import prospeccao_flow
from flows.negociacoes_flow import negociacoes_flow
from flows.classificacao_flow import classificacao_flow
from flows.portfolio_flow import portfolio_flow
from flows.clickhouse_flow import consultas_clickhouse_flow
from flows.qim_ues_flow import qim_ues_flow
from flows.google_sheets_flow import google_sheets_flow
from flows.notification_flow import enviar_notificacao_teams_flow, enviar_whatsapp_flow
from flows.utils_flow import (
    configurar_webdriver_task,
    encerrar_webdriver_task,
    registrar_log_task,
    comparar_excel_task,
    duracao_tempo,
    criar_estrutura_diretorios_task,
)


@flow(
    name="Pipeline SRInfo EMBRAPII",
    description="Pipeline principal de extração de dados do SRInfo",
)
def main_pipeline_flow(
    selected_modules=None,
    plano_metas=False,
    gerar_snapshot=False,
    enviar_wpp=False,
    enviar_teams=True,
):
    """
    Flow principal que orquestra o pipeline de extração de dados do SRInfo.

    Args:
        selected_modules (list): Lista de módulos selecionados para execução
        plano_metas (bool): Indica se deve processar o plano de metas
        gerar_snapshot (bool): Indica se deve gerar o snapshot
        enviar_wpp (bool): Indica se deve enviar mensagem pelo WhatsApp
        enviar_teams (bool): Indica se deve enviar notificação para o Teams
    """
    logger = get_run_logger()
    inicio = datetime.now()
    logger.info(f'Início: {inicio.strftime("%d/%m/%Y %H:%M:%S")}')

    # Verificar e criar estrutura de diretórios
    logger.info("Verificando e criando estrutura de diretórios...")
    criar_estrutura_diretorios_task()

    # Se nenhum módulo for selecionado, executar todos
    if selected_modules is None:
        selected_modules = [
            "sharepoint",
            "info_empresas",
            "empresas_contratantes",
            "info_unidades",
            "equipe_ue",
            "termos_cooperacao",
            "plano_acao",
            "ue_peo",
            "sebrae",
            "projetos_contratados",
            "projetos_empresas",
            "projetos",
            "contratos",
            "estudantes",
            "pedidos_pi",
            "macroentregas",
            "comunicacao",
            "eventos_srinfo",
            "prospeccao",
            "negociacoes",
            "propostas_tecnicas",
            "planos_trabalho",
            "classificacao_projetos",
            "cg_classificacao_projetos",
            "portfolio",
            "levar_arquivos_sharepoint",
            "consultas_clickhouse",
            "qim_ues",
            "atualizar_google_sheets",
        ]

    # Registrar etapas de execução
    log = []

    # SEÇÃO 1: COLETA DE DADOS
    logger.info("SEÇÃO 1: COLETA DE DADOS")

    # SharePoint - sempre executado
    logger.info("Buscando arquivos do SharePoint...")
    buscar_arquivos_sharepoint_flow()

    # Configurar WebDriver
    logger.info("Configurando WebDriver...")
    driver = configurar_webdriver_task()

    try:
        # Empresas
        if any(
            m in selected_modules for m in ["info_empresas", "empresas_contratantes"]
        ):
            logger.info("Processando dados de empresas...")
            log = empresa_flow(driver, log, selected_modules)

        # Unidades Embrapii
        if any(
            m in selected_modules
            for m in [
                "info_unidades",
                "equipe_ue",
                "termos_cooperacao",
                "plano_acao",
                "ue_peo",
            ]
        ):
            logger.info("Processando dados de unidades Embrapii...")
            log = unidade_embrapii_flow(driver, log, selected_modules)

        # Projetos
        if any(
            m in selected_modules
            for m in [
                "sebrae",
                "projetos_contratados",
                "projetos_empresas",
                "projetos",
                "contratos",
                "estudantes",
                "pedidos_pi",
                "macroentregas",
            ]
        ):
            logger.info("Processando dados de projetos...")
            log = projeto_flow(driver, log, selected_modules)

        # Prospecção
        if any(
            m in selected_modules
            for m in ["comunicacao", "eventos_srinfo", "prospeccao"]
        ):
            logger.info("Processando dados de prospecção...")
            log = prospeccao_flow(driver, log, selected_modules)

        # Negociações
        if any(
            m in selected_modules
            for m in ["negociacoes", "propostas_tecnicas", "planos_trabalho"]
        ):
            logger.info("Processando dados de negociações...")
            log = negociacoes_flow(driver, log, selected_modules)

        # SEÇÃO 2: PROCESSAMENTO DE DADOS
        logger.info("SEÇÃO 2: PROCESSAMENTO DE DADOS")

        # Classificação de Projetos
        if any(
            m in selected_modules
            for m in ["classificacao_projetos", "cg_classificacao_projetos"]
        ):
            logger.info("Processando classificação de projetos...")
            log = classificacao_flow(log, selected_modules)

        # Processamento de Empresas (segunda fase)
        if "info_empresas" in selected_modules:
            from flows.empresa_flow import processar_info_empresas_task

            logger.info("Processando informações de empresas...")
            processar_info_empresas_task()

        # Portfolio
        if "portfolio" in selected_modules:
            logger.info("Processando portfolio...")
            log = portfolio_flow(log)

        # Registrar Log
        logger.info("Registrando logs...")
        registrar_log_task(log)

        # SEÇÃO 3: LEVAR ARQUIVOS PARA O SHAREPOINT
        logger.info("SEÇÃO 3: LEVAR ARQUIVOS PARA O SHAREPOINT")

        if "levar_arquivos_sharepoint" in selected_modules:
            logger.info("Enviando arquivos para o SharePoint...")
            levar_arquivos_sharepoint_flow()

        # SEÇÃO 4: CONSULTAS CLICKHOUSE
        logger.info("SEÇÃO 4: CONSULTAS CLICKHOUSE")

        if "consultas_clickhouse" in selected_modules:
            logger.info("Executando consultas ClickHouse...")
            consultas_clickhouse_flow()

        # QIM UES
        if "qim_ues" in selected_modules:
            logger.info("Executando pipeline QIM UES...")
            qim_ues_flow()

        # SEÇÃO 5: ATUALIZAR GOOGLE SHEETS
        logger.info("SEÇÃO 5: ATUALIZAR GOOGLE SHEETS")

        if "atualizar_google_sheets" in selected_modules:
            logger.info("Atualizando planilhas no Google Sheets...")
            google_sheets_flow()

        # Opcional: Gerar snapshot
        if gerar_snapshot:
            logger.info("Gerando snapshot")
            from core.scripts_public.report_snapshot import gerar_report_snapshot

            gerar_report_snapshot()

        # Comparar Excel - sempre executado para gerar estatísticas
        logger.info("Comparando arquivos Excel...")
        novos = comparar_excel_task()

    finally:
        # Garantir que o WebDriver seja encerrado
        logger.info("Encerrando WebDriver")
        encerrar_webdriver_task(driver)

    # Finalização e registro de logs
    fim = datetime.now()
    duracao = duracao_tempo(inicio, fim)

    # Links para relatórios
    link_classificacao = NOTIFICATION_CONFIG["links"]["classificacao"]
    link_snapshot = NOTIFICATION_CONFIG["links"]["snapshot"]

    # Preparar mensagem de notificação
    mensagem = (
        f"*Pipeline SRInfo*\n"
        f'Iniciado em: {inicio.strftime("%d/%m/%Y %H:%M:%S")}\n'
        f'Finalizado em: {fim.strftime("%d/%m/%Y %H:%M:%S")}\n'
        f"_Duração total: {duracao}_\n\n"
        f"Novos projetos: {novos[0]}\n"
        f"Novas empresas: {novos[1]}\n"
        f"Projetos sem classificação: {novos[2]}\n\n"
        f"Relatório Executivo (snapshot): {link_snapshot}\n\n"
        f"Link para classificação dos projetos: {link_classificacao}"
    )

    logger.info(mensagem)

    # Enviar notificações
    if enviar_wpp:
        enviar_whatsapp_flow(mensagem)

    if enviar_teams:
        enviar_notificacao_teams_flow(
            {
                "inicio": inicio.strftime("%d/%m/%Y %H:%M:%S"),
                "fim": fim.strftime("%d/%m/%Y %H:%M:%S"),
                "duracao": duracao,
                "novos_projetos": novos[0],
                "novas_empresas": novos[1],
                "projetos_sem_classificacao": novos[2],
                "status": "success",
            }
        )

    logger.info(f'Fim: {fim.strftime("%d/%m/%Y %H:%M:%S")}')

    return {
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "duracao": duracao,
        "novos_projetos": novos[0],
        "novas_empresas": novos[1],
        "projetos_sem_classificacao": novos[2],
    }


if __name__ == "__main__":
    # Permite executar o flow diretamente para testes
    main_pipeline_flow()
