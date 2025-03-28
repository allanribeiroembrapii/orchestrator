from prefect import flow, task, get_run_logger
from tasks.browser.webdriver_tasks import setup_driver_task
from datetime import datetime
import os
import sys

# Importar caminho raiz
sys.path.append(os.getenv('ROOT'))

@flow(name="Extração de Dados de Empresas")
def empresa_extract_flow(driver=None):
    """Flow para extrair dados específicos de empresas."""
    logger = get_run_logger()
    logger.info("Iniciando extração de dados de empresas")
    
    # Reutilizar driver ou criar um novo se não fornecido
    if driver is None:
        driver = setup_driver_task()
        local_driver = True
    else:
        local_driver = False
    
    try:
        # Importar módulos de funções existentes
        from empresa.info_empresas.main_info_empresas import main_info_empresas_baixar
        from analises_relatorios.empresas_contratantes.main_empresas_contratantes import main_empresas_contratantes
        
        # Executar extrações
        logger.info("Extraindo informações de empresas")
        main_info_empresas_baixar(driver)
        
        logger.info("Extraindo empresas contratantes")
        main_empresas_contratantes(driver)
        
        return {"status": "success", "timestamp": datetime.now().isoformat()}
        
    finally:
        # Fechar driver se foi criado localmente
        if local_driver:
            driver.quit()
    
if __name__ == "__main__":
    # Permite executar este flow individualmente para testes
    empresa_extract_flow()