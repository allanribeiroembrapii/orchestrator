import os
import zipfile
import inspect
from dotenv import load_dotenv
from datetime import datetime
from .connect_sharepoint import SharepointClient


#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT_CLICKHOUSE_QUERYS')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')

#Definição dos caminhos
PASTA_ARQUIVOS = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED))
RAW = os.path.abspath(os.path.join(ROOT, '1_data_raw'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup'))

#Sharepoint
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')


def zipar_arquivos(origem, destino):
    current_datetime = datetime.now().strftime('%Y.%m.%d_%Hh%Mm%Ss')
    arquivo_zip = os.path.join(destino, f'consultas_clickhouse_{current_datetime}.zip')

    # Cria um objeto ZipFile no modo de escrita
    with zipfile.ZipFile(arquivo_zip, 'w') as zipf:
        # Percorre todos os arquivos da pasta
        for root, dirs, files in os.walk(origem):
            for file in files:
                # Caminho completo do arquivo
                file_path = os.path.join(root, file)
                # Adiciona o arquivo ao ZIP, preservando a estrutura de pastas
                zipf.write(file_path, os.path.relpath(file_path, origem))


def up_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        sp = SharepointClient()

        # Listar arquivos na pasta
        for nome_arquivo in os.listdir(PASTA_ARQUIVOS):
            caminho_do_arquivo = os.path.join(PASTA_ARQUIVOS, nome_arquivo)
            if os.path.isfile(caminho_do_arquivo):
                sp.upload_file_to_folder(caminho_do_arquivo, 'dw_pii')
    except Exception as e:
        print(f"🔴 Erro: {e}")


