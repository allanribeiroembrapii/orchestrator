import os
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()
ROOT = os.getenv('ROOT')

# Definição dos caminhos
PATH_PROJETO = os.path.abspath(os.path.join(ROOT, 'projeto', 'projetos', 'step_3_data_processed', 'projetos.xlsx'))

def filtrar_projetos(path_arquivo_a_ser_filtrado):
    # Carregar o arquivo a ser filtrado
    arquivo_a_ser_filtrado = pd.read_excel(path_arquivo_a_ser_filtrado)
    
    # Carregar a lista de projetos
    lista_projetos = pd.read_excel(PATH_PROJETO)['codigo_projeto']
    
    # Filtrar os projetos que estão na lista de projetos
    arquivo_filtrado = arquivo_a_ser_filtrado[arquivo_a_ser_filtrado['codigo_projeto'].isin(lista_projetos)]
    
    # Salvar o arquivo filtrado no mesmo caminho
    arquivo_filtrado.to_excel(path_arquivo_a_ser_filtrado, index=False)
