import os
import sys
from dotenv import load_dotenv


#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')
PASTA = 'plano_metas'

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'unidade_embrapii', PASTA))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))
DIRETORIO_METAS_CONSOLIDADAS = os.path.abspath(os.path.join(CURRENT_DIR, 'metas_consolidadas'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

#Importar módulos necessários
from scripts_public.webdriver import configurar_webdriver
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.processar_excel import processar_excel
from baixar_ids import baixar_ids_tabela_plano_metas
from join_ids_plano_metas import join_ids_plano_metas
from baixar_files_metas import baixar_files_metas
from join_metas import join_metas
from ajustar_metas_consolidadas import ajustar_metas_consolidadas

#Definição da função
def main_plano_metas(driver):
    print('Tabela Plano de Metas')
    link = 'https://srinfo.embrapii.org.br/accreditation/goalplans/'
    nome_arquivo = PASTA
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)
    print('Tabela de IDs')
    baixar_ids_tabela_plano_metas(driver)
    join_ids_plano_metas()
    print('Tabela de Metas')
    baixar_files_metas(driver, CURRENT_DIR)
    join_metas()
    ajustar_metas_consolidadas()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_METAS_CONSOLIDADAS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'unidade_embrapii', PASTA, 'step_2_stage_area')
destino = os.path.join(ROOT, 'unidade_embrapii', PASTA, 'step_3_data_processed')
nome_arquivo = PASTA + ".xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade",
    "Termo de Cooperação",
    "Número do aditivo",
    "Data de Início e Término do PA",
    "Status",
]

novos_nomes_e_ordem = {
    "Unidade": 'unidade_embrapii',
    "Termo de Cooperação": 'termo_cooperacao',
    "Número do aditivo": 'numero_aditivo',
    "Data de Início e Término do PA": 'data_inicio_fim_plano_acao',
    "Status": 'status',
}

# Campos de data e valor
campos_data = ['data_inicio_fim_plano_acao']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data)
