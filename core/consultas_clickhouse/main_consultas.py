import os
import sys
import shutil
from dotenv import load_dotenv
from consultas_clickhouse.scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta
from consultas_clickhouse.scripts_public.main_registros_financeiros import main_registros_financeiros
from consultas_clickhouse.scripts_public.main_anexo8 import main_anexo8
from consultas_clickhouse.scripts_public.main_repasses import main_repasses
from consultas_clickhouse.scripts_public.levar_arquivos_sharepoint import levar_arquivos_sharepoint

load_dotenv()
ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

ARQUIVOS_BRUTOS = os.path.abspath(os.path.join(ROOT, '1_data_raw'))
ARQUIVOS_PROCESSADOS = os.path.abspath(os.path.join(ROOT, '2_data_processed'))
BACKUP = os.path.abspath(os.path.join(ROOT, 'backup'))

def main(anexo8 = False, registros_financeiros = False, repasses = False, levar = False, an8_por_unidade = False, an8_por_projeto = False, an8_por_mes = False,
         an8_ano_especifico = None, an8_mes_especifico = None, an8_tirar_desqualificados = False):
    
    if anexo8 or registros_financeiros or repasses:
        print("Apagando arquivos das pastas.")
        apagar_arquivos_pasta(ARQUIVOS_BRUTOS)
        apagar_arquivos_pasta(ARQUIVOS_PROCESSADOS)
        apagar_arquivos_pasta(BACKUP)

    if anexo8:
        main_anexo8(an8_por_unidade, an8_por_projeto, an8_por_mes, an8_mes_especifico, an8_ano_especifico, an8_tirar_desqualificados)
        # shutil.move(os.path.abspath(os.path.join(ARQUIVOS_BRUTOS, 'anexo8.csv')), ARQUIVOS_PROCESSADOS)

    if registros_financeiros:
        main_registros_financeiros()

    if repasses:
        main_repasses()

    if levar:
        print("Levando arquivos processados para o Sharepoint")
        levar_arquivos_sharepoint()

if __name__ == "__main__":
    main(anexo8=True, registros_financeiros=True, repasses=True, levar=True,
         an8_por_unidade=True, an8_por_projeto=True, an8_por_mes=True)
