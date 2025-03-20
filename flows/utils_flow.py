from prefect import flow, task, get_run_logger
import sys
import os
import gc
import psutil
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar módulos originais
from core.scripts_public.registrar_log import registrar_log
from core.scripts_public.comparar_excel import comparar_excel
from core.scripts_public.scripts_public import criar_estrutura_diretorios


@task(name="Criar Estrutura de Diretórios")
def criar_estrutura_diretorios_task():
    """Task para verificar e criar a estrutura de diretórios necessária."""
    logger = get_run_logger()
    logger.info("Verificando e criando estrutura de diretórios...")

    # Criar estrutura básica
    criar_estrutura_diretorios()

    # Garantir que diretórios específicos existam
    diretorios = [
        # Diretórios para empresa
        os.path.join(ROOT, "empresa", "info_empresas", "step_1_data_raw"),
        os.path.join(ROOT, "empresa", "info_empresas", "step_2_stage_area"),
        os.path.join(ROOT, "empresa", "info_empresas", "step_3_data_processed"),
        # Diretórios para análises e relatórios
        os.path.join(
            ROOT, "analises_relatorios", "empresas_contratantes", "step_1_data_raw"
        ),
        os.path.join(
            ROOT, "analises_relatorios", "empresas_contratantes", "step_2_stage_area"
        ),
        os.path.join(
            ROOT,
            "analises_relatorios",
            "empresas_contratantes",
            "step_3_data_processed",
        ),
        os.path.join(
            ROOT, "analises_relatorios", "projetos_contratados", "step_1_data_raw"
        ),
        os.path.join(
            ROOT, "analises_relatorios", "projetos_contratados", "step_2_stage_area"
        ),
        os.path.join(
            ROOT, "analises_relatorios", "projetos_contratados", "step_3_data_processed"
        ),
        # Diretórios para unidades EMBRAPII
        os.path.join(ROOT, "unidade_embrapii", "info_unidades", "step_1_data_raw"),
        os.path.join(ROOT, "unidade_embrapii", "info_unidades", "step_2_stage_area"),
        os.path.join(
            ROOT, "unidade_embrapii", "info_unidades", "step_3_data_processed"
        ),
        os.path.join(ROOT, "unidade_embrapii", "equipe_ue", "step_1_data_raw"),
        os.path.join(ROOT, "unidade_embrapii", "equipe_ue", "step_2_stage_area"),
        os.path.join(ROOT, "unidade_embrapii", "equipe_ue", "step_3_data_processed"),
        os.path.join(ROOT, "unidade_embrapii", "termos_cooperacao", "step_1_data_raw"),
        os.path.join(
            ROOT, "unidade_embrapii", "termos_cooperacao", "step_2_stage_area"
        ),
        os.path.join(
            ROOT, "unidade_embrapii", "termos_cooperacao", "step_3_data_processed"
        ),
        os.path.join(ROOT, "unidade_embrapii", "plano_acao", "step_1_data_raw"),
        os.path.join(ROOT, "unidade_embrapii", "plano_acao", "step_2_stage_area"),
        os.path.join(ROOT, "unidade_embrapii", "plano_acao", "step_3_data_processed"),
        # Diretórios para projetos
        os.path.join(ROOT, "projeto", "sebrae", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "sebrae", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "sebrae", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "projetos_empresas", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "projetos_empresas", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "projetos_empresas", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "projetos", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "projetos", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "projetos", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "contratos", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "contratos", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "contratos", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "estudantes", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "estudantes", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "estudantes", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "pedidos_pi", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "pedidos_pi", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "pedidos_pi", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "macroentregas", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "macroentregas", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "macroentregas", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "classificacao_projeto", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "classificacao_projeto", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "classificacao_projeto", "step_3_data_processed"),
        os.path.join(ROOT, "projeto", "portfolio", "step_1_data_raw"),
        os.path.join(ROOT, "projeto", "portfolio", "step_2_stage_area"),
        os.path.join(ROOT, "projeto", "portfolio", "step_3_data_processed"),
        # Diretórios para prospecção
        os.path.join(ROOT, "prospeccao", "comunicacao", "step_1_data_raw"),
        os.path.join(ROOT, "prospeccao", "comunicacao", "step_2_stage_area"),
        os.path.join(ROOT, "prospeccao", "comunicacao", "step_3_data_processed"),
        os.path.join(ROOT, "prospeccao", "eventos_srinfo", "step_1_data_raw"),
        os.path.join(ROOT, "prospeccao", "eventos_srinfo", "step_2_stage_area"),
        os.path.join(ROOT, "prospeccao", "eventos_srinfo", "step_3_data_processed"),
        os.path.join(ROOT, "prospeccao", "prospeccao", "step_1_data_raw"),
        os.path.join(ROOT, "prospeccao", "prospeccao", "step_2_stage_area"),
        os.path.join(ROOT, "prospeccao", "prospeccao", "step_3_data_processed"),
        # Diretórios para negociações
        os.path.join(ROOT, "negociacoes", "negociacoes", "step_1_data_raw"),
        os.path.join(ROOT, "negociacoes", "negociacoes", "step_2_stage_area"),
        os.path.join(ROOT, "negociacoes", "negociacoes", "step_3_data_processed"),
        os.path.join(ROOT, "negociacoes", "propostas_tecnicas", "step_1_data_raw"),
        os.path.join(ROOT, "negociacoes", "propostas_tecnicas", "step_2_stage_area"),
        os.path.join(
            ROOT, "negociacoes", "propostas_tecnicas", "step_3_data_processed"
        ),
        os.path.join(ROOT, "negociacoes", "planos_trabalho", "step_1_data_raw"),
        os.path.join(ROOT, "negociacoes", "planos_trabalho", "step_2_stage_area"),
        os.path.join(ROOT, "negociacoes", "planos_trabalho", "step_3_data_processed"),
        # Diretórios para classificação CG
        os.path.join(ROOT, "cg_classificacao_projetos", "step_1_data_raw"),
        os.path.join(ROOT, "cg_classificacao_projetos", "step_2_stage_area"),
        os.path.join(ROOT, "cg_classificacao_projetos", "step_3_data_processed"),
        # Diretórios para atualização do Google Sheets
        os.path.join(ROOT, "atualizar_google_sheets", "inputs"),
        # Diretórios para QIM UES
        os.path.join(ROOT, "qim_ues", "arquivos_brutos"),
        os.path.join(ROOT, "qim_ues", "backup_qim"),
        os.path.join(ROOT, "qim_ues", "copy"),
        os.path.join(ROOT, "qim_ues", "up"),
        # Diretórios para DWPII
        os.path.join(ROOT, "DWPII_backup"),
        os.path.join(ROOT, "DWPII_copy"),
        os.path.join(ROOT, "DWPII_up"),
        # Diretório para logs
        os.path.join(ROOT, "logs"),
        # Diretório para lookup tables
        os.path.join(ROOT, "lookup_tables"),
    ]

    # Criar diretórios se não existirem
    for diretorio in diretorios:
        os.makedirs(diretorio, exist_ok=True)
        logger.debug(f"Diretório verificado/criado: {diretorio}")

    logger.info("Estrutura de diretórios verificada e criada com sucesso")
    return True


@task(name="Configurar WebDriver", retries=3, retry_delay_seconds=30)
def configurar_webdriver_task():
    """Task para configurar e inicializar o WebDriver."""
    logger = get_run_logger()
    logger.info("Configurando WebDriver...")

    # Instalar o driver uma vez
    edge_service = EdgeService(EdgeChromiumDriverManager().install())

    options = webdriver.EdgeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("log-level=3")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument("--incognito")
    options.add_argument("--disable-cache")

    driver = webdriver.Edge(service=edge_service, options=options)
    logger.info("WebDriver configurado com sucesso")
    return driver


@task(name="Encerrar WebDriver")
def encerrar_webdriver_task(driver):
    """Task para encerrar o WebDriver de forma segura."""
    logger = get_run_logger()
    logger.info("Encerrando WebDriver...")

    driver.quit()
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == "msedgedriver":
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    gc.collect()

    logger.info("WebDriver encerrado com sucesso")
    return True


@task(name="Registrar Log")
def registrar_log_task(log):
    """
    Task para registrar logs.

    Args:
        log: Lista de logs para registrar
    """
    logger = get_run_logger()
    logger.info("Registrando logs...")
    registrar_log(log)
    return True


@task(name="Comparar Excel", retries=1)
def comparar_excel_task():
    """Task para comparar arquivos Excel e obter estatísticas."""
    logger = get_run_logger()
    logger.info("Comparando arquivos Excel...")
    novos = comparar_excel()
    logger.info(f"Novos projetos: {novos[0]}")
    logger.info(f"Novas empresas: {novos[1]}")
    logger.info(f"Projetos sem classificação: {novos[2]}")
    return novos


def duracao_tempo(inicio, fim):
    """
    Calcula a duração entre dois timestamps.

    Args:
        inicio: Timestamp de início
        fim: Timestamp de fim

    Returns:
        str: Duração formatada
    """
    duracao = fim - inicio
    segundos = duracao.total_seconds()
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segundos = int(segundos % 60)

    if horas > 0:
        return f"{horas}h {minutos}m {segundos}s"
    elif minutos > 0:
        return f"{minutos}m {segundos}s"
    else:
        return f"{segundos}s"
