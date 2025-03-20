from prefect import task, get_run_logger
import os
import psutil
import gc
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager


@task(name="Configurar WebDriver", retries=3, retry_delay_seconds=30)
def setup_driver_task():
    """Task para configurar e inicializar o WebDriver com recursos de retry."""
    logger = get_run_logger()
    logger.info("Configurando WebDriver...")

    # Instalar o driver uma vez
    edge_service = EdgeService(EdgeChromiumDriverManager().install())

    options = webdriver.EdgeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("log-level=3")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument("--incognito")
    options.add_argument("--disable-cache")

    driver = webdriver.Edge(service=edge_service, options=options)
    logger.info("WebDriver configurado com sucesso")
    return driver


@task(name="Encerrar WebDriver")
def cleanup_driver_task(driver):
    """Task para encerrar o WebDriver de forma segura."""
    logger = get_run_logger()
    logger.info("Encerrando WebDriver...")

    driver.quit()
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == "msedgedriver":
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    gc.collect()

    logger.info("WebDriver encerrado com sucesso")
    return True
