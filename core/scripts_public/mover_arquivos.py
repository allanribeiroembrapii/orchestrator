import os
import sys
import shutil
from glob import glob
from datetime import datetime
from apagar_arquivos_pasta import apagar_arquivos_pasta

def mover_arquivos_excel(numero_arquivos, pasta_download, diretorio, nome_arquivo):
    """
    Move arquivos Excel da pasta de downloads para a pasta de dados brutos.
    
    Args:
        numero_arquivos: Número de arquivos a serem movidos
        pasta_download: Caminho da pasta de downloads
        diretorio: Diretório base do projeto
        nome_arquivo: Nome base para os arquivos movidos
    """
    # Verificar se a pasta de download existe
    if not pasta_download:
        print("ERRO: A variável PASTA_DOWNLOAD não está definida no arquivo .env")
        print("Por favor, adicione o caminho da pasta de downloads no arquivo .env")
        sys.exit(1)
    
    if not os.path.isdir(pasta_download):
        print(f"ERRO: A pasta de downloads '{pasta_download}' não existe")
        print("Por favor, verifique o caminho da pasta de downloads no arquivo .env")
        sys.exit(1)
    
    # Definir o caminho para a pasta de dados brutos
    data_raw = os.path.join(diretorio, 'step_1_data_raw')
    
    # Verificar se a pasta de dados brutos existe
    if not os.path.isdir(data_raw):
        print(f"AVISO: Criando a pasta '{data_raw}'")
        os.makedirs(data_raw, exist_ok=True)
    
    # Limpar a pasta de dados brutos
    apagar_arquivos_pasta(data_raw)
    
    # Listar todos os arquivos Excel na pasta Downloads
    files = glob(os.path.join(pasta_download, '*.xlsx'))
    
    if not files:
        print(f"AVISO: Nenhum arquivo Excel encontrado na pasta '{pasta_download}'")
        return
    
    # Ordenar os arquivos por data de modificação (mais recentes primeiro)
    files.sort(key=os.path.getmtime, reverse=True)
    
    # Selecionar os n arquivos mais recentes
    files_to_move = files[:numero_arquivos]
    
    print(f"Movendo {len(files_to_move)} arquivos para '{data_raw}'")
    
    # Mover os arquivos selecionados para a pasta data_raw com renome
    for i, file in enumerate(files_to_move, start=1):
        novo_nome = f"{nome_arquivo}_{i}.xlsx"
        novo_caminho = os.path.join(data_raw, novo_nome)
        try:
            shutil.move(file, novo_caminho)
            print(f"Arquivo movido: {os.path.basename(file)} -> {novo_nome}")
        except Exception as e:
            print(f'ERRO ao mover {file} para {novo_caminho}. Razão: {e}')
