import os
import shutil
from glob import glob
from datetime import datetime
from apagar_arquivos_pasta import apagar_arquivos_pasta

def mover_arquivos_excel(numero_arquivos, pasta_download, diretorio, nome_arquivo):

    data_raw = os.path.join(diretorio, 'step_1_data_raw')

    apagar_arquivos_pasta(data_raw)

    #Lista todos os arquivos Excel na pasta Downloads
    files = glob(os.path.join(pasta_download, '*.xlsx'))
    
    #Ordena os arquivos por data de modificação (mais recentes primeiro)
    files.sort(key=os.path.getmtime, reverse=True)
    
    #Seleciona os n arquivos mais recentes
    files_to_move = files[:numero_arquivos]
    
    # Move os arquivos selecionados para a pasta data_raw com renome
    for i, file in enumerate(files_to_move, start=1):
        novo_nome = f"{nome_arquivo}_{i}.xlsx"
        novo_caminho = os.path.join(data_raw, novo_nome)
        try:
            shutil.move(file, novo_caminho)
        except Exception as e:
            print(f'Erro ao mover {file} para {novo_caminho}. Razão: {e}')
