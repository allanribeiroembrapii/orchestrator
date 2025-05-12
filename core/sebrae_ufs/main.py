from scripts.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from scripts.gerando_planilha import gerando_planilha, processar_BD_portfolio
from office365_api.upload_files import upload_files
import os
from dotenv import load_dotenv

load_dotenv()
ROOT = os.getenv('ROOT')
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))


def main():
    # Carregar arquivos do SharePoint
    print("Passo 1/4: Buscando arquivos do SharePoint")
    buscar_arquivos_sharepoint()

    # Gerando planilha geral
    print("Passo 2/4: Gerando planilha_geral")
    gerando_planilha()

    # Processando BD_portfolio
    print("Passo 3/4: Processando BD_portfolio")
    processar_BD_portfolio()

    # Levando BD_portfolio para o SharePoint
    print("Passo 4/4: Levando BD_portfolio para o SharePoint")
    upload_files(STEP3, 'DWPII/sebrae_ufs')

if __name__ == "__main__":
    main()