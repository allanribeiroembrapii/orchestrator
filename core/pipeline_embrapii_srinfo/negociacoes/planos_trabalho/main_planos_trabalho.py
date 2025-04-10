import os
import sys
import pandas as pd
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'negociacoes', 'planos_trabalho'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
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
def main_planos_trabalho(driver):
    link = 'https://srinfo.embrapii.org.br/units/negotiations/workplans/'
    nome_arquivo = 'negociacoes_planos_trabalho'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'negociacoes', 'planos_trabalho', 'step_2_stage_area')
destino = os.path.join(ROOT, 'negociacoes', 'planos_trabalho', 'step_3_data_processed')
nome_arquivo = "negociacoes_planos_trabalho.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade EMBRAPII",
    "Data de entrega",
    "Código da Negociação",
    "CNPJ",
    "Objetivos",
    "Valor total",
    "Duração (meses)",
    "Versão",
]

novos_nomes_e_ordem = {
    "Código da Negociação": 'codigo_negociacao',
    "Unidade EMBRAPII": 'unidade_embrapii',
    "Data de entrega": 'data_entrega',
    "CNPJ": 'cnpj',
    "Objetivos": 'objetivos',
    "Valor total": 'valor_total',
    "Duração (meses)": 'duracao_meses',
    "Versão": 'versao', 
}

# Campos de data e valor
campos_data = ['data_entrega']
campos_valor = ['valor_total']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)

     # Criando planos de trabalho empresas
    planos_trabalho = pd.read_excel(arquivo_destino)
    planos_trabalho['cnpj'] = planos_trabalho['cnpj'].fillna('').astype(str)
    empresas = planos_trabalho

    empresas['cnpj'] = empresas['cnpj'].str.split(';')
    empresas = empresas.explode('cnpj')
    empresas['cnpj'] = empresas['cnpj'].str.strip()
    empresas = empresas[~empresas[['cnpj']].eq('').any(axis=1)]
    empresas = empresas[['codigo_negociacao', 'cnpj']]
    empresas = empresas.drop_duplicates()

    planos_trabalho = planos_trabalho.drop(['cnpj'], axis=1)
    planos_trabalho = planos_trabalho.drop_duplicates()

    planos_trabalho.to_excel(arquivo_destino, index = False)
    empresas.to_excel(os.path.join(destino, 'planos_trabalho_empresas.xlsx'), index = False)