import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT_BFA')

#Definição dos caminhos
STEP1 = os.path.abspath(os.path.join(ROOT, 'data', 'step_1_data_raw'))
STEP2 = os.path.abspath(os.path.join(ROOT, 'data', 'step_2_stage_area'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'data', 'step_3_data_processed'))
COPY = os.path.abspath(os.path.join(ROOT, 'data', 'copy'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'data', 'backup'))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))
SCRIPTS = os.path.abspath(os.path.join(ROOT, 'scripts'))

# Verifica e cria a pasta se não existir
if not os.path.exists(STEP1):
    os.makedirs(STEP1)

# Verifica e cria a pasta se não existir
if not os.path.exists(STEP2):
    os.makedirs(STEP2)

# Verifica e cria a pasta se não existir
if not os.path.exists(STEP3):
    os.makedirs(STEP3)

# Verifica e cria a pasta se não existir
if not os.path.exists(COPY):
    os.makedirs(COPY)

# Verifica e cria a pasta se não existir
if not os.path.exists(BACKUP):
    os.makedirs(BACKUP)

# Adiciona o diretório correto ao sys.path
sys.path.append(SCRIPTS)
sys.path.append(PATH_OFFICE)

from office365_api.download_files import get_file, get_file_gepes
from scripts.apagar_arquivos_pasta import apagar_arquivos_pasta

def buscar_arquivos_sharepoint():
    apagar_arquivos_pasta(STEP1)
    apagar_arquivos_pasta(STEP2)
    apagar_arquivos_pasta(STEP3)
    apagar_arquivos_pasta(COPY)
    apagar_arquivos_pasta(BACKUP)

    get_file("BFA - Base de Dados para BI.xlsx", "General//Programas Estratégicos//BFA", STEP1)
    get_file_gepes("bfa_projetos.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_projetos_empresas.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_projetos_unidades.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_execucao.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_status_macroentregas.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_comentarios.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_stage_gates.xlsx", "dw_pii", COPY)
    get_file_gepes("bfa_empresas_info.xlsx", "dw_pii", COPY)