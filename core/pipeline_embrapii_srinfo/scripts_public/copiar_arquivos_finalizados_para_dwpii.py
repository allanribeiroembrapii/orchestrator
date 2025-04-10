import os
import shutil
from dotenv import load_dotenv

# Carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

def copiar_arquivos_finalizados_para_dwpii(diretorio):
    """
    Copia arquivos .xlsx do diretório especificado para o diretório DWPII_up.
    
    Args:
    diretorio (str): Caminho completo do diretório onde os arquivos .xlsx estão localizados.
    """
    # Caminho do destino
    destino = os.path.abspath(os.path.join(ROOT, 'DWPII_up'))
    
    # Certificar-se de que o destino existe
    if not os.path.exists(destino):
        os.makedirs(destino)
    
    # Verificar se o diretório fornecido existe
    if not os.path.isdir(diretorio):
        print(f"O diretório {diretorio} não existe.")
        return
    
    # Iterar sobre os arquivos no diretório
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith('.xlsx'):
            caminho_completo = os.path.join(diretorio, arquivo)
            shutil.copy(caminho_completo, destino)

