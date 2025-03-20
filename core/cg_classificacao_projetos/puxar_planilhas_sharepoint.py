import os
import sys
from dotenv import load_dotenv
from office365_api.download_files import get_file
import inspect

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv('ROOT')
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)



# puxar_planilhas()


