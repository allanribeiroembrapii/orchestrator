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
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'empresa', 'info_empresas'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

STEP_1_DATA_RAW = os.path.abspath(os.path.join(CURRENT_DIR, 'step_1_data_raw'))
STEP_2_STAGE_AREA = os.path.abspath(os.path.join(CURRENT_DIR, 'step_2_stage_area'))
STEP_3_DATA_PROCESSED = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(SCRIPTS_PATH)

#Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.processar_excel import processar_excel
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
# from processar_dados_empresas import processar_dados_empresas

def main_info_empresas_baixar(driver):
    apagar_arquivos_pasta(STEP_1_DATA_RAW)
    apagar_arquivos_pasta(STEP_2_STAGE_AREA)
    apagar_arquivos_pasta(STEP_3_DATA_PROCESSED)
    link = 'https://srinfo.embrapii.org.br/company/list/'
    nome_arquivo = 'info_empresas'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados_empresas()

def main_info_empresas_processar():
    agregar_dados_porte_empresa()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


def agregar_dados_porte_empresa():
    path_empresas = os.path.join(ROOT, 'empresa', 'info_empresas', 'step_3_data_processed', 'info_empresas.xlsx')
    path_porte = os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed', 'informacoes_empresas.xlsx')

    df_empresas = pd.read_excel(path_empresas)
    df_porte = pd.read_excel(path_porte)
    # colunas_remover = [
    #     'Código',
    #     'CNAE',
    #     'Empresas',
    #     'CNAE_parte',
    #     'cnae_divisao',
    # ]
    # df_porte = df_porte.drop(columns=colunas_remover)

    # df_empresas = df_empresas.merge(df_porte, left_on='cnpj', right_on='CNPJ', how='left')
    # colunas_remover = [
    #     'CNPJ',
    # ]
    # df_empresas = df_empresas.drop(columns=colunas_remover)

    # novos_nomes = {
    #     'Faixa de faturamento declarada':'faixa_faturamento',
    #     'Faixa de empregados declarada':'faixa_empregados',
    # }
    # df_empresas = df_empresas.rename(columns=novos_nomes)

    df_empresas = df_empresas.drop_duplicates(subset='cnpj')

    path_destino = os.path.join(ROOT, 'empresa', 'info_empresas', 'step_3_data_processed', 'info_empresas.xlsx')

    df_empresas.to_excel(path_destino, index=False)



# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'empresa', 'info_empresas', 'step_2_stage_area')
destino = os.path.join(ROOT, 'empresa', 'info_empresas', 'step_3_data_processed')
nome_arquivo = "info_empresas.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    'CNPJ',
    'Situação',
    'Status',
    'Tipo',
    'Natureza legal',
    'Data de abertura',
    'Nome da empresa',
    'Nome fantasia',
    'CNAE',
    'Atribuição',
    'Estado',
    'Município',
    'CEP',
    'Bairro',
    'Logradouro',
    'Número',
    'Complemento',
    'E-mail',
    'Pessoa Responsável',
    'Situação Especial',
    'Motivo para a situação',
    'Data da Situação Especial',
]

novos_nomes_e_ordem = {
    'CNPJ':'cnpj',
    'Situação':'situacao_cnpj',
    'Status':'status',
    'Tipo':'hierarquia',
    'Natureza legal':'natureza_legal',
    'Data de abertura':'data_abertura',
    'Nome da empresa':'razao_social',
    'Nome fantasia':'nome_fantasia',
    'CNAE':'cnae_principal',
    'Atribuição':'cnae_descricao',
    'Estado':'endereco_uf',
    'Município':'endereco_municipio',
    'CEP':'endereco_cep',
    'Bairro':'endereco_bairro',
    'Logradouro':'endereco_logradouro',
    'Número':'endereco_numero',
    'Complemento':'endereco_complemento',
    'E-mail':'contato_email',
    'Pessoa Responsável':'pessoa_responsavel',
    'Situação Especial':'recuperacao_judicial',
    'Motivo para a situação':'recuperacao_judicial_motivo',
    'Data da Situação Especial':'recuperacao_judicial_data',
}


def processar_dados_empresas():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)
