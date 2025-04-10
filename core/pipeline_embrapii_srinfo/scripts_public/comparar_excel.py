import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

def comparar_excel():

    # Caminhos dos arquivos
    DWPII_COPY = os.path.abspath(os.path.join(ROOT, 'DWPII_copy'))
    DWPII_UP = os.path.abspath(os.path.join(ROOT, 'DWPII_up'))

    # Leitura das planilhas
    copy_projetos = pd.read_excel(os.path.abspath(os.path.join(DWPII_COPY, "portfolio.xlsx")))
    copy_empresas = pd.read_excel(os.path.abspath(os.path.join(DWPII_COPY, "informacoes_empresas.xlsx")))
    up_projetos = pd.read_excel(os.path.abspath(os.path.join(DWPII_UP, "portfolio.xlsx")))
    up_empresas = pd.read_excel(os.path.abspath(os.path.join(DWPII_UP, "informacoes_empresas.xlsx")))
    classif = pd.read_excel(os.path.abspath(os.path.join(DWPII_UP, "classificacao_projeto.xlsx")))

    # Calculando numero de novos projetos, novas empresas e numero de projetos sem classificacao 
    proj = len(up_projetos[~up_projetos['codigo_projeto'].isin(copy_projetos['codigo_projeto'])])
    emp = len(up_empresas[~up_empresas['cnpj'].isin(copy_empresas['cnpj'])])
    clas = len(classif[classif['Tecnologias Habilitadoras'] == 'Não definido'])

    return [proj, emp, clas]

# Executar função
if __name__ == "__main__":
    comparar_excel()