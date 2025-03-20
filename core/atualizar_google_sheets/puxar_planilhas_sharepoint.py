import os
import sys
from dotenv import load_dotenv
from core.office365_api.download_files import get_file
import inspect

# carregar .env e tudo mais
load_dotenv(encoding="latin-1")
ROOT = os.getenv("ROOT")
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, "core", "office365_api"))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

# Obter configurações do SharePoint
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")


# puxar planilhas do sharepoint
def puxar_planilhas():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Garantir que o diretório inputs existe
    # Ajustando o caminho para considerar a nova estrutura com a pasta core
    inputs = os.path.join(os.path.dirname(ROOT), "inputs")
    os.makedirs(inputs, exist_ok=True)

    # Limpar a pasta inputs
    apagar_arquivos_pasta(inputs)

    # Baixar arquivos do SharePoint
    try:
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "portfolio.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "projetos_empresas.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "informacoes_empresas.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "info_unidades_embrapii.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "ue_linhas_atuacao.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "macroentregas.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "negociacoes_negociacoes.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "classificacao_projeto.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "projetos.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "prospeccao_prospeccao.xlsx",
            "DWPII/srinfo",
            inputs,
        )
        get_file(
            SHAREPOINT_SITE,
            SHAREPOINT_SITE_NAME,
            SHAREPOINT_DOC,
            "cnae_ibge.xlsx",
            "DWPII/lookup_tables",
            inputs,
        )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro ao baixar arquivos do SharePoint: {e}")
        raise


def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é válido
        if not os.path.isdir(caminho_pasta):
            print(f"O caminho {caminho_pasta} não é uma pasta válida.")
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
