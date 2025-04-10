import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#sys.path
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
sys.path.append(SCRIPTS_PUBLIC_PATH)

from scripts_public.processar_excel import processar_excel

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

