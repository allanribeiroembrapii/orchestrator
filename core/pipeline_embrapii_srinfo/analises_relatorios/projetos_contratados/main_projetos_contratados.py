import os
import sys
import pandas as pd
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'analises_relatorios', 'projetos_contratados'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))

#Adicionar caminhos ao sys.path
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

from mover_arquivos import mover_arquivos_excel
from scripts.baixar_dados_srinfo import baixar_dados_srinfo_projetos_contratados

def main_projetos_contratados(driver):
    baixar_dados_srinfo_projetos_contratados(driver)
    pasta_download = os.getenv('PASTA_DOWNLOAD')
    nome_arquivo = 'raw_relatorio_projetos_contratados'
    mover_arquivos_excel(1, pasta_download, CURRENT_DIR, nome_arquivo)
    caminho = r'analises_relatorios\projetos_contratados\step_1_data_raw\raw_relatorio_projetos_contratados_1.xlsx'
    filtrar_main_projetos_contratados(caminho)

def filtrar_main_projetos_contratados(caminho):
    df = pd.read_excel(caminho)
    df_filtrado = df[df['Status'] != 'Desqualificado']
    df_filtrado.to_excel(caminho, index=False)


#Executar função
if __name__ == "__main__":
    main_projetos_contratados()