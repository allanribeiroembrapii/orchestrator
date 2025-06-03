import re
import sys, os
from pathlib import PurePath
from core.rvg_repositorio_visuais_graficos.connection.office365.office365_api import SharePoint


def upload_files(pasta_arquivos, destino, keyword=None):
    file_list = get_list_of_files(pasta_arquivos)
    for file in file_list:
        if keyword is None or keyword == 'None' or re.search(keyword, file[0]):
            file_content = get_file_content(file[1])
            SharePoint().upload_file(file[0], destino, file_content)


def get_list_of_files(folder):
    file_list = []
    folder_item_list = os.listdir(folder)
    for item in folder_item_list:
        item_full_path = PurePath(folder, item)
        if os.path.isfile(item_full_path):
            file_list.append([item, item_full_path])
    return file_list


# read files and return the content of files
def get_file_content(file_path):
    with open(file_path, "rb") as f:
        return f.read()
