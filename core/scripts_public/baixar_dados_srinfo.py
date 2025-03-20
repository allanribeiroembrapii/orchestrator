import os
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from bs4 import BeautifulSoup

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def baixar_dados_srinfo(driver, link_listagem, num_pages = None, option1000 = None, sebrae = False):
    """
    Baixa dados do SRInfo usando Selenium WebDriver.
    
    Requer as seguintes variáveis de ambiente no arquivo .env:
    - SRINFO_USERNAME: Nome de usuário para login no SRInfo
    - PASSWORD: Senha para login no SRInfo
    
    Args:
        driver: Instância do WebDriver
        link_listagem: URL da página de listagem
        num_pages: Número de páginas a serem processadas (opcional)
        option1000: Se True, seleciona 1000 itens por página, caso contrário 9999 (opcional)
        sebrae: Se True, adiciona um tempo de espera adicional para páginas do Sebrae (opcional)
        
    Returns:
        int: Número de downloads realizados
    """
    # Obter credenciais do arquivo .env
    username = os.getenv('SRINFO_USERNAME')
    password = os.getenv('PASSWORD')
    
    # Verificar se as credenciais estão definidas
    if not username or not password:
        print("ERRO: Credenciais incompletas. Verifique se SRINFO_USERNAME e PASSWORD estão definidos no arquivo .env")
        print("Por favor, adicione sua senha no arquivo .env na variável PASSWORD")
        sys.exit(1)
 
    try:
        # Acessar tela de login
        print("Acessando página de login do SRInfo...")
        driver.get('https://srinfo.embrapii.org.br/users/login/')
        time.sleep(5)
        
        # Inserir credenciais
        print(f"Fazendo login com o usuário: {username}")
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'id_username'))
        )
        username_field.send_keys(username)
        
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'password'))
        )
        password_field.send_keys(password)


        #Logar
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary'))
        )
        login_button.click()

        #Esperar 3 segundos
        time.sleep(3)

        #Ir para a listagem
        driver.get(link_listagem)
        
        #Selecionar "9999" no dropdown
        time.sleep(7)
        dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'form-control.input-sm'))
        )
        dropdown.click()

        if option1000:
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//option[@value='1000']"))
                )
            
        else:
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//option[@value='9999']"))
                )
            
        if sebrae:
            time.sleep(15)
            option.click()
        
        else:
            option.click()

        carregar_dados_e_fazer_download(driver=driver)
        numero_download = 1

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Encontrar o elemento
        if num_pages == None:
            valor = soup.find('a', {'data-dt-idx': '5'})

            if valor and valor.text.isdigit():  # Verifica se o texto é um número
                num_pages = int(valor.text)  # Converte o texto para número inteiro
            else:
                pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.pagination li')
                num_pages = len(pagination) - 2

        if num_pages > 1:
            for page_number in range(num_pages-1):
                #Clicar na página seguinte
                next_page = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="object-list_next"]/a'))
                )
                next_page.click()

                carregar_dados_e_fazer_download(driver=driver)
                numero_download += 1


    finally:
        # driver.quit()
        pass
    
    return numero_download

def carregar_dados_e_fazer_download(driver):
    #Esperar até 90 segundos para carregar
    time.sleep(2)
    WebDriverWait(driver, 90).until(
        EC.invisibility_of_element_located((By.ID, 'object-list_processing'))
    )
    time.sleep(2)

    #Fazer o download
    excel_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'buttons-excel'))
    )
    excel_button.click()
    time.sleep(3)
