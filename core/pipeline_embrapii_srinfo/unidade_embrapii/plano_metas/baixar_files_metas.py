import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from glob import glob
import shutil

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

IDS = 'unidade_embrapii\plano_metas\step_1_data_raw\ids_tabela_plano_metas.xlsx'
PASTA_DOWNLOAD = os.getenv('PASTA_DOWNLOAD')

def baixar_files_metas(driver, diretorio):
    lista_ids = pd.read_excel(IDS)['ID'].tolist()

    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
 
    try:
        # Acessar tela de login
        driver.get('https://srinfo.embrapii.org.br/users/login/')
        time.sleep(5)
        
        # Inserir credenciais
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'id_username'))
        )
        username_field.send_keys(username)
        
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'password'))
        )
        password_field.send_keys(password)

        # Logar
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary'))
        )
        login_button.click()

        # Esperar 3 segundos
        time.sleep(3)

        # Acessar cada URL de metas usando os IDs
        for id in lista_ids:
            url = f'https://srinfo.embrapii.org.br/accreditation/goalplan/{id}'
            driver.get(url)
            print(f"Acessando URL: {url}")
            time.sleep(5)

            # Fazer o download
            try:
                excel_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'buttons-excel'))
                )
                excel_button.click()
                time.sleep(3)
                mover_file_raw(diretorio, id)
            except Exception as e:
                print(f"Botão de download não encontrado para o ID {id}: {e}")


    finally:
        driver.quit()




def mover_file_raw(diretorio, id):
    data_raw = os.path.join(diretorio, 'files_raw_metas')

    #Lista todos os arquivos Excel na pasta Downloads
    files = glob(os.path.join(PASTA_DOWNLOAD, '*.xlsx'))
    
    #Ordena os arquivos por data de modificação (mais recentes primeiro)
    files.sort(key=os.path.getmtime, reverse=True)
    file = files[0]
    novo_nome = f"id_{id}.xlsx"
    novo_caminho = os.path.join(data_raw, novo_nome)
    shutil.move(file, novo_caminho)

    

