import os
import sys
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def configurar_webdriver():
    """
    Configura e retorna uma instância do Microsoft Edge WebDriver.
    
    Requer as seguintes variáveis de ambiente no arquivo .env:
    - SRINFO_USERNAME: Nome de usuário para login no SRInfo
    - PASSWORD: Senha para login no SRInfo
    - PASTA_DOWNLOAD: Caminho para a pasta de downloads
    
    Returns:
        webdriver.Edge: Instância configurada do Edge WebDriver
    """
    try:
        # Instalar o driver a cada chamada para garantir compatibilidade
        edge_service = EdgeService(EdgeChromiumDriverManager().install())
        
        # Configurar opções do navegador
        options = webdriver.EdgeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('log-level=3')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument("--incognito")  # Modo anônimo
        options.add_argument("--disable-cache")
        
        # Inicializar o driver
        driver = webdriver.Edge(service=edge_service, options=options)
        
        # Configurar timeout padrão para esperas
        driver.implicitly_wait(10)  # Espera implícita de 10 segundos
        
        return driver
    
    except Exception as e:
        print(f"Erro ao configurar o WebDriver: {str(e)}")
        sys.exit(1)
