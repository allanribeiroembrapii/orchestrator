import os
import inspect
import requests
import pandas as pd
from dotenv import load_dotenv


# Função para verificar e criar diretórios se não existirem
def verificar_criar_diretorio(caminho):
    """
    Verifica se um diretório existe e o cria se não existir.

    Args:
        caminho: Caminho do diretório a ser verificado/criado
    """
    diretorio = os.path.dirname(caminho)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
        print(f"Diretório criado: {diretorio}")


# Carregar variáveis de ambiente do .env
load_dotenv()
ROOT = os.getenv("ROOT_DATAPII")

# Definição dos caminhos
RAW = os.path.abspath(os.path.join(ROOT, os.getenv("STEP_1_DATA_RAW")))

# Verificar e criar diretório RAW se não existir
verificar_criar_diretorio(RAW)

# URL da API do IBGE
IPCA_IBGE = "https://apisidra.ibge.gov.br/values/t/1737/p/all/v/2266/N1/1?formato=json"


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
    # Garantir que o diretório existe antes de salvar o arquivo
    verificar_criar_diretorio(output_path)
    df.to_excel(output_path, index=False)

    print("🟢 " + inspect.currentframe().f_code.co_name)
