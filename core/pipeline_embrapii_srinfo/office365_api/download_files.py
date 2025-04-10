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

def get_file(sharepoint_site, sharepoint_site_name, sharepoint_doc, file_n, folder, dest):
    # print(f'Debug: Baixando arquivo -> {file_n} da pasta -> {folder}')
    file_obj = SharePoint().download_file(sharepoint_site, sharepoint_site_name, sharepoint_doc, file_n, folder)
    save_file(file_n, file_obj, dest)

def get_files(sharepoint_site, sharepoint_site_name, sharepoint_doc, folder, dest):
    # print(f'Debug: Listando arquivos na pasta ->{sharepoint_site} - {sharepoint_site_name} - {folder}')
    files_list = SharePoint()._get_files_list(sharepoint_site, sharepoint_doc, folder)
    for file in files_list:
        get_file(sharepoint_site, sharepoint_site_name, sharepoint_doc, file.name, folder, dest)

def get_files_by_pattern(sharepoint_site, sharepoint_doc, keyword, folder, dest):
    # print(f'Debug: Listando arquivos na pasta -> {folder} com padrão -> {keyword}')
    files_list = SharePoint()._get_files_list(sharepoint_site, folder)
    for file in files_list:
        if re.search(keyword, file.name):
            get_file(sharepoint_site, sharepoint_doc, file.name, folder, dest)

if __name__ == '__main__':
    FOLDER_NAME = sys.argv[1]
    FOLDER_DEST = sys.argv[2]
    FILE_NAME = sys.argv[3]
    FILE_NAME_PATTERN = sys.argv[4]

    SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
    SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
    SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

    SHAREPOINT_SITE_SEBRAE = os.getenv('sharepoint_url_site_sebrae')
    SHAREPOINT_SITE_NAME_SEBRAE = os.getenv('sharepoint_site_name_sebrae')
    SHAREPOINT_DOC_SEBRAE = os.getenv('sharepoint_doc_library_sebrae')

    if FILE_NAME != 'None':
        get_file(SHAREPOINT_SITE_NAME, SHAREPOINT_DOC, FILE_NAME, FOLDER_NAME, FOLDER_DEST)
        get_file(SHAREPOINT_SITE_NAME_SEBRAE, SHAREPOINT_DOC_SEBRAE, FILE_NAME, FOLDER_NAME, FOLDER_DEST)
    elif FILE_NAME_PATTERN != 'None':
        get_files_by_pattern(SHAREPOINT_SITE, FILE_NAME_PATTERN, FOLDER_NAME, FOLDER_DEST)
        get_files_by_pattern(SHAREPOINT_SITE_SEBRAE, FILE_NAME_PATTERN, FOLDER_NAME, FOLDER_DEST)
    else:
        get_files(SHAREPOINT_SITE, FOLDER_NAME, FOLDER_DEST)
        get_files(SHAREPOINT_SITE_SEBRAE, FOLDER_NAME, FOLDER_DEST)
