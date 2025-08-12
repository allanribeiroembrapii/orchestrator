import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService

def configurar_webdriver():
    # Caminho absoluto ou relativo do driver local
    driver_path = os.path.join(os.getcwd(), "drivers", "msedgedriver.exe")

    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"EdgeDriver não encontrado em: {driver_path}")

    options = webdriver.EdgeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('log-level=3')
    options.add_argument('--remote-debugging-port=0')
    options.add_argument('--incognito')
    options.add_argument('--disable-cache')

    service = EdgeService(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)
    return driver