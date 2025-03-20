import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'unidade_embrapii', 'termos_cooperacao'))
# SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

#Importar módulos necessários
from scripts_public.webdriver import configurar_webdriver
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.processar_excel import processar_excel
# from tratamento_dados import processar_dados

#Definição da função
def main_termos_cooperacao(driver):
    link = 'https://srinfo.embrapii.org.br/accreditation/cooperationterms/'
    nome_arquivo = 'termos_cooperacao'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'unidade_embrapii', 'termos_cooperacao', 'step_2_stage_area')
destino = os.path.join(ROOT, 'unidade_embrapii', 'termos_cooperacao', 'step_3_data_processed')
nome_arquivo = "termos_cooperacao.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade",
    "Chamada Pública",
    "Termo de Cooperação",
    "Aditivo",
    "Data de assinatura",
    "Data de início",
    "Data final",
    "Multicarteira?",
    "Formação de RH",
    "Status do Termo de Cooperação",
    "Status do Credenciamento da Unidade",
]

novos_nomes_e_ordem = {
    "Unidade": 'unidade_embrapii',
    "Chamada Pública": 'chamada_publica',
    "Termo de Cooperação": 'termo_cooperacao',
    "Aditivo": 'aditivo',
    "Data de assinatura": 'data_assinatura',
    "Data de início": 'data_inicio',
    "Data final": 'data_final',
    "Multicarteira?": 'multicarteira',
    "Formação de RH": 'formacao_rh',
    "Status do Termo de Cooperação": 'status_termo_cooperacao',
    "Status do Credenciamento da Unidade": 'status_credenciamento_unidade',
}

# Campos de data e valor
campos_data = ['data_assinatura', 'data_inicio', 'data_final']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data)
