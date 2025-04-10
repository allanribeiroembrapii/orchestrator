import os
import sys
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'analises_relatorios', 'empresas_contratantes'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

from mover_arquivos import mover_arquivos_excel
from scripts_public.processar_excel import processar_excel
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii

# from scripts.baixar_dados_srinfo import baixar_dados_srinfo_empresas_contratantes

def main_empresas_contratantes(driver):
    baixar_dados_srinfo_empresas_contratantes(driver)
    pasta_download = os.getenv('PASTA_DOWNLOAD')
    nome_arquivo = 'raw_relatorio_empresas_contratantes'
    mover_arquivos_excel(1, pasta_download, CURRENT_DIR, nome_arquivo)
    processar_dados_empresas_contratantes()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)



def baixar_dados_srinfo_empresas_contratantes(driver):

    link_listagem = "https://srinfo.embrapii.org.br/analytics/reports/"

    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    
    try:
        #Acessar tela de login
        driver.get('https://srinfo.embrapii.org.br/users/login/')
        time.sleep(5)
        
        #Inserir credenciais
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
        time.sleep(3)

        #selecionar empresas contratantes
        selecionar_relatorio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'select2-id_report-container'))
        )
        selecionar_relatorio.click()
        opcao_empresas_contratantes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Empresas Contratantes')]"))
        )
        opcao_empresas_contratantes.click()
        time.sleep(3)
        
        #visualizar dados
        visualizar_dados_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-success'))
        )
        visualizar_dados_button.click()
        time.sleep(20)

        #Selecionar "9999" no dropdown
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'form-control.input-sm'))
        )
        dropdown.click()
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//option[@value='9999']"))
        )
        option.click()

        carregar_dados_e_fazer_download(driver=driver)
    finally:
        pass
    
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


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(os.path.join(ROOT, 'analises_relatorios', 'empresas_contratantes', 'step_1_data_raw'))
destino = os.path.join(ROOT, 'analises_relatorios', 'empresas_contratantes', 'step_3_data_processed')
nome_arquivo = "empresas_contratantes.xlsx"
arquivo_origem = os.path.join(origem, 'raw_relatorio_empresas_contratantes_1.xlsx')
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    'Empresa',
    'CNPJ',
    'CNAE', 
    'CNAE - Atribuição',
    'Número Projetos',
    'Unidades',
    'Projetos',
    'Parcerias / Programas',
    'Calls',
    'Modalidade de financiamento',
    'Cooperação Internacional',
    'Faixa de faturamento declarada',
    'Faixa de empregados declarada',
    'Contatos declarados',
    'E-mails de contatos declarados',
    'Telefone de contato declarados'
]

novos_nomes_e_ordem = {
    'CNPJ': 'cnpj',
    'Empresa': 'empresa',
    'CNAE': 'cnae', 
    'CNAE - Atribuição': 'nome_cnae',
    'Número Projetos': 'numero_projetos',
    'Unidades': 'unidades_embrapii',
    'Projetos': 'codigo_projetos',
    'Parcerias / Programas': 'parcerias_programas',
    'Calls': 'calls',
    'Modalidade de financiamento': 'modalidades_financiamento',
    'Cooperação Internacional': 'cooperacao_internacional',
    'Faixa de faturamento declarada': 'faixa_faturamento',
    'Faixa de empregados declarada': 'faixa_empregados',
    'Contatos declarados': 'contatos',
    'E-mails de contatos declarados': 'emails_contatos',
    'Telefone de contato declarados': 'telefones_contatos'
}


def processar_dados_empresas_contratantes():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)

#Executar função
if __name__ == "__main__":
    main_empresas_contratantes()