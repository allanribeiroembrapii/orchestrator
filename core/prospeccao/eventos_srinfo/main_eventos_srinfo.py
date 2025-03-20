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
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'prospeccao', 'eventos_srinfo'))
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
def main_eventos_srinfo(driver):
    link = 'https://srinfo.embrapii.org.br/units/events/'
    nome_arquivo = 'prospeccao_eventos_srinfo'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'prospeccao', 'eventos_srinfo', 'step_2_stage_area')
destino = os.path.join(ROOT, 'prospeccao', 'eventos_srinfo', 'step_3_data_processed')
nome_arquivo = "prospeccao_eventos_srinfo.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade EMBRAPII",
    "Data do evento",
    "Título do evento",
    "Local de realização do evento",
    "Tipo de evento",
    "Tipo de participação",
    "Número total de participantes",
    "Número total de empresas participantes",
    "Número total de contatos com empresas",
    "Observações ou comentários",
    "Reconhecida pela EMBRAPII",
]

novos_nomes_e_ordem = {
    'Unidade EMBRAPII': 'unidade_embrapii',
    'Data do evento': 'data_evento',
    'Título do evento': 'titulo_evento',
    'Local de realização do evento': 'local_evento',
    'Tipo de evento': 'tipo_evento',
    'Tipo de participação': 'tipo_participacao',
    'Número total de participantes': 'numero_total_participantes',
    'Número total de empresas participantes': 'numero_total_empresas_participantes',
    'Número total de contatos com empresas': 'numero_total_contratos_empresas',
    'Observações ou comentários': 'observacoes',
    'Reconhecida pela EMBRAPII': 'reconhecida_pela_embrapii',
}

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)


#Executar função
if __name__ == "__main__":
    main_eventos_srinfo()