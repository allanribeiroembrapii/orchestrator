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
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'prospeccao', 'prospeccao'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

#Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.processar_excel import processar_excel
# from tratamento_dados import processar_dados

#Definição da função
def main_prospeccao(driver):
    link = 'https://srinfo.embrapii.org.br/units/prospects/'
    nome_arquivo = 'prospeccao_prospeccao'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'prospeccao', 'prospeccao', 'step_2_stage_area')
destino = os.path.join(ROOT, 'prospeccao', 'prospeccao', 'step_3_data_processed')
nome_arquivo = "prospeccao_prospeccao.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade EMBRAPII",
    "Data da prospecção",
    "Nome da empresa",
    "Será feita proposta?",
    "Relatório",
    "Iniciativa da prospecção",
    "Tipo de interação",
    "CNPJ da Empresa",
    "Pessoa contatada na empresa",
    "Cargo da pessoa contatada",
    "Observações ou comentários",
    "Reconhecida pela EMBRAPII",
]

novos_nomes_e_ordem = {
    'Unidade EMBRAPII': 'unidade_embrapii',
    'Data da prospecção': 'data_prospeccao',
    'Nome da empresa': 'nome_empresa',
    'Será feita proposta?': 'sera_feita_proposta',
    'Relatório': 'relatorio',
    'Iniciativa da prospecção': 'iniciativa_prospeccao',
    'Tipo de interação': 'tipo_interacao',
    'CNPJ da Empresa': 'cnpj_empresa',
    'Pessoa contatada na empresa': 'pessoa_contatada_empresa_nome',
    'Cargo da pessoa contatada': 'pessoa_contatada_empresa_cargo',
    'Observações ou comentários': 'observacoes',
    'Reconhecida pela EMBRAPII': 'reconhecida_embrapii',
}

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)


#Executar função
if __name__ == "__main__":
    main_prospeccao()