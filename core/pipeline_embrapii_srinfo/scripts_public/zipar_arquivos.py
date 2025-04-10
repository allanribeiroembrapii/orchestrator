import os
import zipfile
from datetime import datetime

def zipar_arquivos(origem, destino):
    current_datetime = datetime.now().strftime('%Y.%m.%d_%Hh%Mm%Ss')
    arquivo_zip = os.path.join(destino, f'srinfo_{current_datetime}.zip')

    # Cria um objeto ZipFile no modo de escrita
    with zipfile.ZipFile(arquivo_zip, 'w') as zipf:
        # Percorre todos os arquivos da pasta
        for root, dirs, files in os.walk(origem):
            for file in files:
                # Caminho completo do arquivo
                file_path = os.path.join(root, file)
                # Adiciona o arquivo ao ZIP, preservando a estrutura de pastas
                zipf.write(file_path, os.path.relpath(file_path, origem))
