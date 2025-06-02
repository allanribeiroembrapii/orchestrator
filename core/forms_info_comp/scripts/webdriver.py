import os
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService

# Instalar o driver uma vez
edge_service = EdgeService(EdgeChromiumDriverManager().install())

def configurar_webdriver(pasta_download=None):
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
    # options.add_argument("--headless=new") 
    
    if pasta_download is None:
        pasta_download = os.path.join(os.getcwd(), "downloads")

    os.makedirs(pasta_download, exist_ok=True)

    prefs = {
        "download.default_directory": os.path.abspath(pasta_download),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Edge(service=edge_service, options=options)
    return driver