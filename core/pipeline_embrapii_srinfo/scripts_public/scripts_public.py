import os
from dotenv import load_dotenv
from scripts_public.baixar_dados_srinfo import baixar_dados_srinfo
from scripts_public.mover_arquivos import mover_arquivos_excel
from scripts_public.append_arquivos import append_excel_files

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


def baixar_e_juntar_arquivos(
    driver, link, diretorio, nome_arquivo, num_pages=None, option1000=None, sebrae=False
):

    pasta_download = os.getenv("PASTA_DOWNLOAD")

    numero_arquivos = baixar_dados_srinfo(driver, link, num_pages, option1000, sebrae)
    mover_arquivos_excel(numero_arquivos, pasta_download, diretorio, nome_arquivo)
    append_excel_files(diretorio, nome_arquivo)
