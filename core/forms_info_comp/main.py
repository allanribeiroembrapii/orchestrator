import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# carregar .env
load_dotenv()
ROOT = os.getenv("ROOT")

STEP1= os.path.abspath(os.path.join(ROOT, "step_1_data_raw"))
STEP2 = os.path.abspath(os.path.join(ROOT, "step_2_stage_area"))
STEP3 = os.path.abspath(os.path.join(ROOT, "step_3_data_processed"))
BACKUP = os.path.abspath(os.path.join(ROOT, "backup"))

# Importar módulos necessários
from scripts.apagar_arquivos_pasta import apagar_arquivos_pasta
from scripts.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from scripts.webdriver import configurar_webdriver
from scripts.baixar_dados_srinfo import baixar_dados_srinfo
from scripts.gerar_planilha_final import consolidar_planilhas, ajustes
from scripts.ler_pdfs import ler_pdfs, juntando_planilhas_info, juntando_planilhas_geral, gerando_planilhas_final
from scripts.up_sharepoint import up_sharepoint


def main():

    # buscar arquivo com tickets
    buscar_arquivos_sharepoint()

    # configurar webdriver
    driver = configurar_webdriver(STEP1)

    # baixar dados tickets
    baixar_dados_srinfo(driver)

    # gerando as novas planilhas com informações gerais e complementares
    # excel
    df = consolidar_planilhas(STEP1)
    ajustes(df, STEP2)

    # pdfs
    ler_pdfs()
    juntando_planilhas_info()
    juntando_planilhas_geral()

    # juntando com planilhas anteriores
    gerando_planilhas_final()

    # zipando arquivos e enviando para o sharepoint
    up_sharepoint()


if __name__ == "__main__":
    main()