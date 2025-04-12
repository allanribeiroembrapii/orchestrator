import os
import sys
from dotenv import load_dotenv

# carregar .env
load_dotenv()
ROOT = os.getenv("ROOT_PIPELINE")
PASTA = "plano_acao"

# Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, "scripts_public"))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, "unidade_embrapii", PASTA))
# SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, "step_3_data_processed"))

# Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

# Importar módulos necessários
from scripts_public.webdriver import configurar_webdriver
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import (
    copiar_arquivos_finalizados_para_dwpii,
)
from scripts_public.processar_excel import processar_excel

# from tratamento_dados import processar_dados
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta

STEP_1_DATA_RAW = os.path.abspath(os.path.join(CURRENT_DIR, "step_1_data_raw"))
STEP_2_STAGE_AREA = os.path.abspath(os.path.join(CURRENT_DIR, "step_2_stage_area"))
STEP_3_DATA_PROCESSED = os.path.abspath(os.path.join(CURRENT_DIR, "step_3_data_processed"))


# Definição da função
def main_plano_acao(driver):
    apagar_arquivos_pasta(STEP_1_DATA_RAW)
    apagar_arquivos_pasta(STEP_2_STAGE_AREA)
    apagar_arquivos_pasta(STEP_3_DATA_PROCESSED)
    link = "https://srinfo.embrapii.org.br/accreditation/actionplans/"
    nome_arquivo = PASTA
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, "unidade_embrapii", PASTA, "step_2_stage_area")
destino = os.path.join(ROOT, "unidade_embrapii", PASTA, "step_3_data_processed")
nome_arquivo = PASTA + ".xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade",
    "Termo de Cooperação",
    "Número do aditivo",
    "Data de Início do Plano de Ação",
    "Data de Término do Plano de Ação",
    "Competências Técnicas",
    "Linhas de Atuação",
    "Status",
]

novos_nomes_e_ordem = {
    "Unidade": "unidade_embrapii",
    "Termo de Cooperação": "termo_cooperacao",
    "Número do aditivo": "numero_aditivo",
    "Data de Início do Plano de Ação": "data_inicio_plano_acao",
    "Data de Término do Plano de Ação": "data_termino_plano_acao",
    "Competências Técnicas": "competencias_tecnicas",
    "Linhas de Atuação": "linhas_atuacao",
    "Status": "status",
}

# Campos de data e valor
campos_data = ["data_inicio_plano_acao", "data_termino_plano_acao"]


def processar_dados():
    processar_excel(
        arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data
    )
