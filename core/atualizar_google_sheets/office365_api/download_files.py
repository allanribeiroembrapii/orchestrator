import re
import sys, os
from pathlib import PurePath
from dotenv import load_dotenv

#Adicionar o caminho do diretório raiz ao sys.path
load_dotenv()
ROOT = os.getenv('ROOT')
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

from office365_api.office365_api import SharePoint

def save_file(file_n, file_obj, dest):
    file_dir_path = PurePath(dest, file_n)
    # print(f'Debug: Salvando arquivo -> {file_dir_path}')
    with open(file_dir_path, 'wb') as f:
        f.write(file_obj)

def get_file(file_n, folder, dest):
    # print(f'Debug: Baixando arquivo -> {file_n} da pasta -> {folder}')
    file_obj = SharePoint().download_file(file_n, folder)
    save_file(file_n, file_obj, dest)

def get_files(folder, dest):
    # print(f'Debug: Listando arquivos na pasta -> {folder}')
    files_list = SharePoint()._get_files_list(folder)
    for file in files_list:
        get_file(file.name, folder, dest)

def get_files_by_pattern(keyword, folder, dest):
    # print(f'Debug: Listando arquivos na pasta -> {folder} com padrão -> {keyword}')
    files_list = SharePoint()._get_files_list(folder)
    for file in files_list:
        if re.search(keyword, file.name):
            get_file(file.name, folder, dest)

if __name__ == '__main__':
    FOLDER_NAME = sys.argv[1]
    FOLDER_DEST = sys.argv[2]
    FILE_NAME = sys.argv[3]
    FILE_NAME_PATTERN = sys.argv[4]

    if FILE_NAME != 'None':
        get_file(FILE_NAME, FOLDER_NAME, FOLDER_DEST)
    elif FILE_NAME_PATTERN != 'None':
        get_files_by_pattern(FILE_NAME_PATTERN, FOLDER_NAME, FOLDER_DEST)
    else:
        get_files(FOLDER_NAME, FOLDER_DEST)
