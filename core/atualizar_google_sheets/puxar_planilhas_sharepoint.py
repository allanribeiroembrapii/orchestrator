import os
import sys
from dotenv import load_dotenv
import inspect

# Obter o diretório atual e o diretório raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_GSHET")
if not ROOT:
    ROOT = current_dir

# Tentar encontrar o diretório office365_api
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, "office365_api"))
if not os.path.exists(PATH_OFFICE):
    # Tentar encontrar em outros locais comuns
    PATH_OFFICE = os.path.abspath(
        os.path.join(root_dir, "core", "pipeline_embrapii_srinfo", "office365_api")
    )
    if not os.path.exists(PATH_OFFICE):
        PATH_OFFICE = os.path.abspath(os.path.join(root_dir, "office365_api"))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

try:
    from office365_api.download_files import get_file
except ImportError:
    sys.path.append(os.path.dirname(PATH_OFFICE))
    from download_files import get_file


# puxar planilhas do sharepoint
def puxar_planilhas():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    inputs = os.path.join(ROOT, "inputs")
    apagar_arquivos_pasta(inputs)

    get_file("portfolio.xlsx", "DWPII/srinfo", inputs)
    get_file("projetos_empresas.xlsx", "DWPII/srinfo", inputs)
    get_file("informacoes_empresas.xlsx", "DWPII/srinfo", inputs)
    get_file("info_unidades_embrapii.xlsx", "DWPII/srinfo", inputs)
    get_file("pedidos_pi.xlsx", "DWPII/srinfo", inputs)
    get_file("ue_linhas_atuacao.xlsx", "DWPII/srinfo", inputs)
    get_file("macroentregas.xlsx", "DWPII/srinfo", inputs)
    get_file("negociacoes_negociacoes.xlsx", "DWPII/srinfo", inputs)
    get_file("classificacao_projeto.xlsx", "DWPII/srinfo", inputs)
    get_file("projetos.xlsx", "DWPII/srinfo", inputs)
    get_file("prospeccao_prospeccao.xlsx", "DWPII/srinfo", inputs)
    get_file("cnae_ibge.xlsx", "DWPII/lookup_tables", inputs)
    print("🟢 " + inspect.currentframe().f_code.co_name)


def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é uma pasta; se não for, cria
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            return

        # Lista todos os arquivos na pasta
        arquivos = os.listdir(caminho_pasta)

        # Apaga cada arquivo na pasta
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
    except Exception as e:
        print(f"🔴 Ocorreu um erro ao apagar os arquivos: {e}")


# puxar_planilhas()
