import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
STEP1 = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw'))
STEP2 = os.path.abspath(os.path.join(ROOT, 'step_2_stage_area'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))
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

# Adiciona o diretório correto ao sys.path
sys.path.append(SCRIPTS)
sys.path.append(PATH_OFFICE)

from download_files import get_file, get_files
from scripts.apagar_arquivos_pasta import apagar_arquivos_pasta

def buscar_arquivos_sharepoint(gerar_novo = False):
    apagar_arquivos_pasta(STEP1)
    apagar_arquivos_pasta(STEP2)
    apagar_arquivos_pasta(STEP3)

    get_file("portfolio.xlsx", "DWPII//srinfo", STEP1)
    get_file("macroentregas.xlsx", "DWPII//srinfo", STEP1)
    get_file("projetos_empresas.xlsx", "DWPII//srinfo", STEP1)
    get_file("informacoes_empresas.xlsx", "DWPII//srinfo", STEP1)
    get_file("empresas_contratantes.xlsx", "DWPII//srinfo", STEP1)
    get_file("pedidos_pi.xlsx", "DWPII//srinfo", STEP1)
    get_file("info_unidades_embrapii.xlsx", "DWPII//srinfo", STEP1)
    get_file("ibge_municipios.xlsx", "DWPII//lookup_tables", STEP1)
    get_file("oni_companies.xlsx", "dw_pii", STEP1)
    get_file("Contas Bancárias - UE.xlsx", "DWPII//lookup_tables", STEP1)
    # get_file("srinfo_sebrae_sourceamount.xlsx", "dw_pii", STEP1)
    # get_file("srinfo_unit.xlsx", "dw_pii", STEP1)
    # get_file("srinfo_company_company.xlsx", "dw_pii", STEP1)
    if gerar_novo == False:
        get_files("DWPII//sebrae_ufs", STEP1)