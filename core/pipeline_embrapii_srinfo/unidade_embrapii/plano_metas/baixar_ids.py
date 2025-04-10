import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def baixar_ids_tabela_plano_metas(driver):

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

        # Ir para a listagem
        driver.get('https://srinfo.embrapii.org.br/accreditation/goalplans/')
        
        # Esperar a página carregar
        time.sleep(7)
        dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'form-control.input-sm'))
        )
        dropdown.click()
        option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//option[@value='9999']"))
                )
        option.click()
        time.sleep(7)

        # Capturar todos os elementos <input> dentro da classe "select-checkbox context-menu"
        ids = []
        elements = driver.find_elements(By.CSS_SELECTOR, 'td.select-checkbox.context-menu input.id')
        for element in elements:
            value = element.get_attribute('value')
            ids.append(value)

        # Exportar os valores para um arquivo Excel
        df = pd.DataFrame(ids, columns=['ID'])
        df.to_excel('unidade_embrapii\plano_metas\step_1_data_raw\ids_tabela_plano_metas.xlsx', index=False)
        print("Dados exportados para ids_tabela_plano_metas.xlsx com sucesso!")

    finally:
        pass


