import os
import inspect
import requests
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()
ROOT = os.getenv('ROOT')

# Definição dos caminhos
RAW = os.path.abspath(os.path.join(ROOT, os.getenv('STEP_1_DATA_RAW')))

# URL da API do IBGE
IPCA_IBGE = 'https://apisidra.ibge.gov.br/values/t/1737/p/all/v/2266/N1/1?formato=json'

def api_ibge():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Pegar os dados da API
    response = requests.get(IPCA_IBGE)
    if response.status_code != 200:
        raise Exception("Erro ao buscar dados da API do IBGE")

    dados = response.json()

    # Extrair cabeçalho da segunda linha (índice 1)
    header = list(dados[0].values())

    # Criar lista de dados a partir da terceira linha em diante (dados reais)
    data = [list(row.values()) for row in dados[1:]]

    # Criar DataFrame com o novo cabeçalho
    df = pd.DataFrame(data, columns=header)

    # Salvar planilha XLSX no caminho RAW
    output_path = os.path.join(RAW, "ipca_ibge.xlsx")
    df.to_excel(output_path, index=False)

    print("🟢 " + inspect.currentframe().f_code.co_name)