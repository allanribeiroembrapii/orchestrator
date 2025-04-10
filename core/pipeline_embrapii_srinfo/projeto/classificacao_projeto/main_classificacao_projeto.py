import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'projeto', 'classificacao_projeto'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(SCRIPTS_PATH)

#Importar módulos necessários
from scripts_public.copiar_e_renomear_arquivos import copiar_e_renomear_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from new_classificacao_projeto import new_classificacao_projeto
from atualizacao_classificacao_projeto import atualizacao_classificao_projeto

#definir variáveis de copiar_e_renomear_arquivos
origens = {
        'projetos_contratados': os.path.join(ROOT, 'analises_relatorios', 'projetos_contratados', 'step_1_data_raw', 'raw_relatorio_projetos_contratados_1.xlsx'),
        'projetos_empresas': os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed', 'projetos_empresas.xlsx'),
        'informacoes_empresas': os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed', 'informacoes_empresas.xlsx'),
        'cnae_divisao': os.path.join(ROOT, 'DWPII_copy', 'lookuptable_cnae_divisao.xlsx'),
        'competencias_ues': os.path.join(ROOT, 'DWPII_copy', 'lookuptable_competencias_ues.xlsx'),
        'classificacao_projeto': os.path.join(ROOT, 'DWPII_copy', 'classificacao_projeto.xlsx')
    }

# Define o caminho relativo da pasta de destino
destino = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw')

# Renomeia os arquivos ao copiar
renomeios = {
    'projetos_contratados': 'raw_projetos_contratados.xlsx',
    'projetos_empresas': 'projetos_empresas.xlsx',
    'informacoes_empresas': 'informacoes_empresas.xlsx',
    'cnae_divisao': 'raw_cnae_divisao.xlsx',
    'competencias_ues': 'raw_competencias_ues.xlsx',
    'classificacao_projeto': 'atual_classificacao_projeto.xlsx'
}


def main_classificacao_projeto():
    copiar_e_renomear_arquivos(origens, destino, renomeios)
    new_classificacao_projeto()
    atualizacao_classificao_projeto()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)

if __name__ == "__main__":
    main_classificacao_projeto()
