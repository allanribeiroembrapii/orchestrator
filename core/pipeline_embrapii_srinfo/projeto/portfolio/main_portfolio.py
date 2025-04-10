import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'projeto', 'portfolio'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PATH)

#Importar módulos necessários
from scripts_public.copiar_e_renomear_arquivos import copiar_e_renomear_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from criar_tabela_portfolio import criar_tabela_portfolio

origens = {
    'contratos': os.path.join(ROOT, 'projeto', 'contratos', 'step_3_data_processed', 'contratos.xlsx'),
    'projetos': os.path.join(ROOT, 'projeto', 'projetos', 'step_3_data_processed', 'projetos.xlsx'),
    'classificacao_projeto': os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_3_data_processed', 'classificacao_projeto.xlsx'),
    'negociacao': os.path.join(ROOT, 'analises_relatorios', 'projetos_contratados', 'step_1_data_raw', 'raw_relatorio_projetos_contratados_1.xlsx'),
    'sebrae_srinfo': os.path.join(ROOT, 'projeto', 'sebrae', 'step_3_data_processed', 'sebrae_srinfo.xlsx'),
    'sebrae': os.path.join(ROOT, 'DWPII_copy', 'sebrae_bi_interno_base_2.0.xlsx')
}

# Define o caminho relativo da pasta de destino
destino = os.path.join(CURRENT_DIR, 'step_1_data_raw')

# Renomeia os arquivos ao copiar
renomeios = {
    'contratos': 'raw_contratos.xlsx',
    'projetos': 'raw_projetos.xlsx',
    'classificacao_projeto': 'raw_classificacao_projeto.xlsx',
    'negociacao': 'raw_relatorio_projetos_contratados_1.xlsx',
    'sebrae_srinfo': 'raw_sebrae_srinfo.xlsx',
    'sebrae': 'raw_sebrae.xlsx'
}

def main_portfolio():
    copiar_e_renomear_arquivos(origens, destino, renomeios)
    criar_tabela_portfolio()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)

if __name__ == "__main__":
    main_portfolio()
