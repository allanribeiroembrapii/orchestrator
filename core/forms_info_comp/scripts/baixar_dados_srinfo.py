import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import hashlib
import glob
import shutil
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pytesseract
from pdf2image import convert_from_path
import shutil
import unicodedata

# Caminho manual do tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\milena.goncalves\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\Users\milena.goncalves\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
ROOT = os.getenv("ROOT")
STEP1 = os.path.abspath(os.path.join(ROOT, "step_1_data_raw"))

session = requests.Session()
hashes_baixados = set()  # Controle de hash dos PDFs baixados

def esperar_download_terminar(pasta, timeout=30):
    start_time = time.time()
    while True:
        arquivos_temp = [f for f in os.listdir(pasta) if f.endswith(('.crdownload', '.tmp'))]
        if not arquivos_temp:
            break
        if time.time() - start_time > timeout:
            raise TimeoutError("Download não terminou dentro do tempo esperado.")
        time.sleep(1)

def renomear_arquivo_mais_recente(pasta_download, novo_nome_sem_extensao):
    arquivos = glob.glob(os.path.join(pasta_download, '*'))
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo encontrado na pasta de download.")
    
    # Arquivo mais recente
    arquivo_mais_recente = max(arquivos, key=os.path.getctime)
    
    # Detecta extensão real
    _, extensao = os.path.splitext(arquivo_mais_recente)
    
    # Define novo nome com extensão original
    novo_nome_completo = os.path.join(pasta_download, novo_nome_sem_extensao + extensao)

    # Renomeia (ou move)
    shutil.move(arquivo_mais_recente, novo_nome_completo)

    print(f"Arquivo renomeado para: {novo_nome_completo}")
    return novo_nome_completo

def obter_nome_unico(caminho_pasta, nome_arquivo):
    base, ext = os.path.splitext(nome_arquivo)
    contador = 1
    novo_nome = nome_arquivo

    while os.path.exists(os.path.join(caminho_pasta, novo_nome)):
        novo_nome = f"{base} ({contador}){ext}"
        contador += 1
    
    return novo_nome

def baixar_dados_srinfo(driver):

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    try:        
        repasses = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'srinfo_partnership_fundsapproval.xlsx')))
        repasses_sebrae_bndes = repasses[repasses['partnership_name'].str.contains('SEBRAE|BNDES', na=False)]
        repasses_sebrae_bndes = repasses_sebrae_bndes[~repasses_sebrae_bndes['partnership_call_name'].str.contains('1º|2º', na=False)]
        tickets_atual = pd.Series(repasses_sebrae_bndes['fundsapp_ticket_monitoring'].unique()).astype(str).str.replace('.', '', regex=False).str[:5]

        info_gerais = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'info_gerais.xlsx')))
        tickets_info_gerais = pd.Series(info_gerais['ticket'].unique()).astype(str)

        tickets_unicos = tickets_atual[~tickets_atual.isin(tickets_info_gerais)]
        
        total_downloads = 0
        link_n = 1
        baixados_urls = set()  # URLs já baixadas nesta sessão
        total_links = len(tickets_unicos)
        print(f"Total Links: {total_links}")

        for ticket in tickets_unicos:
            print(f"Link {link_n}/{total_links}")
            link_ticket = f"https://tickets.embrapii.org.br/issues/{ticket}"

            total_downloads += baixar_arquivos_com_selenium(username, password, driver, link_ticket, ticket, baixados_urls)
            link_n += 1

        print(f"\nTotal de arquivos baixados: {total_downloads}")

    finally:
        # driver.quit()
        pass

def baixar_arquivos_com_selenium(username, password, driver, url_pagina, num_ticket, baixados_urls):
    print(f"Acessando {url_pagina}...")
    driver.get(url_pagina)
    time.sleep(5)  # Aguarde o carregamento da página se necessário

    if "login" in driver.current_url:
        # Inserir credenciais
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )
        password_field.send_keys(password)

        # Logar
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='login-submit']"))
        )
        login_button.click()

        # Esperar 3 segundos
        time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    total_downloads = 0

    # ✅ Primeiro, verifica se tem arquivos Excel
    links_excel = [urljoin(url_pagina, a['href']) for a in soup.find_all('a', href=True) if a['href'].lower().endswith(('.xls', '.xlsx', '.xlsm'))]

    if links_excel:
        print(f"Arquivos Excel encontrados: {len(links_excel)}")

        for download_url in links_excel:
            total_downloads += baixar_arquivo_com_selenium(driver, download_url, STEP1, num_ticket)
        
        # ✅ Como há Excel, NÃO PROCURA nem BAIXA PDF
        print("Excel encontrado, não será feito download de PDFs nesta página.")
        return total_downloads

    else:
        # ✅ Caso NÃO haja Excel, processa os PDFs
        links_pdf = [urljoin(url_pagina, a['href']) for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]

        print(f"PDFs encontrados na página: {len(links_pdf)}")

        for download_url in links_pdf:
            if download_url in baixados_urls:
                print(f"Arquivo já baixado anteriormente nesta sessão, pulando: {download_url}")
                continue

            print(f"Verificando PDF em: {download_url}")
            total_downloads += baixar_pdf_renderizado_se_conter_formulario(
                driver, download_url, STEP1, num_ticket, hashes_baixados
            )
            baixados_urls.add(download_url)

        return total_downloads

def baixar_arquivo_com_selenium(driver, url, pasta_destino, num_ticket):
    arquivos_antes = set(os.listdir(pasta_destino))  # arquivos já existentes
    driver.get(url)
    time.sleep(5)  # Aguarde carregamento / download

    esperar_download_terminar(pasta_destino)

    # Verifica arquivos após o download
    arquivos_depois = set(os.listdir(pasta_destino))
    novos_arquivos = arquivos_depois - arquivos_antes

    if not novos_arquivos:
        print("Nenhum novo arquivo foi baixado.")
        return 0

    # Pegamos o novo arquivo (em teoria deve ser apenas um)
    novo_arquivo_nome = list(novos_arquivos)[0]
    novo_arquivo_caminho = os.path.join(pasta_destino, novo_arquivo_nome)

    if not os.path.exists(novo_arquivo_caminho):
        print("Arquivo recém-baixado não foi encontrado.")
        return 0

    print(f"Verificando hash de: {novo_arquivo_caminho}")
    hash_arquivo = calcular_hash_arquivo(novo_arquivo_caminho)
    print(f"Hash calculado: {hash_arquivo}")

    if hash_arquivo in hashes_baixados:
        print(f"Arquivo duplicado detectado. Removendo: {novo_arquivo_caminho}")
        os.remove(novo_arquivo_caminho)
        return 0

    hashes_baixados.add(hash_arquivo)

    # Renomear
    nome_original = f'formulario_{num_ticket}'
    nome_unico = obter_nome_unico(pasta_destino, nome_original)
    extensao = os.path.splitext(novo_arquivo_caminho)[1]
    novo_caminho = os.path.join(pasta_destino, nome_unico + extensao)

    shutil.move(novo_arquivo_caminho, novo_caminho)
    print(f"Arquivo salvo: {novo_caminho}")
    return 1

def baixar_pdf_renderizado_se_conter_formulario(driver, url, pasta_destino, num_ticket, hashes_baixados):
    try:
        cookies = driver.get_cookies()
        s = requests.Session()
        for c in cookies:
            s.cookies.set(c['name'], c['value'])

        response = s.get(url, verify=False)
        if response.status_code == 200:
            # Calcula hash do conteúdo
            pdf_hash = hashlib.sha256(response.content).hexdigest()

            if pdf_hash in hashes_baixados:
                print(f"PDF já baixado com esse conteúdo (hash repetido), pulando: {url}")
                return 0

            hashes_baixados.add(pdf_hash)

            # Salva temporariamente
            nome_temp = f"temp_{num_ticket}.pdf"
            caminho_pdf = os.path.join(pasta_destino, nome_temp)

            with open(caminho_pdf, 'wb') as f:
                f.write(response.content)

            print(f"PDF temporário baixado: {caminho_pdf}")

            # Processa e salva se contiver "formulario"
            salvou = processar_e_salvar_pdf(caminho_pdf, pasta_destino, num_ticket)

            return 1 if salvou else 0

        else:
            print(f"Falha ao baixar PDF: status code {response.status_code}")
            return 0

    except Exception as e:
        print(f"Erro ao processar PDF renderizado: {e}")
        return 0

def processar_e_salvar_pdf(pdf_caminho, pasta_destino, ticket):
    try:
        imagens = convert_from_path(pdf_caminho, poppler_path=poppler_path)
        encontrou_formulario = False

        for imagem in imagens:
            texto_extraido = pytesseract.image_to_string(imagem)
            texto_normalizado = remover_acentos(texto_extraido).lower()

            if "formulario" in texto_normalizado:
                encontrou_formulario = True
                break  # Não precisa checar as outras páginas

        if encontrou_formulario:
            novo_nome = f"formulario_{ticket}.pdf"
            novo_caminho = os.path.join(pasta_destino, novo_nome)

            # Se já existir, cria nome único
            novo_nome_unico = obter_nome_unico(pasta_destino, novo_nome)
            novo_caminho = os.path.join(pasta_destino, novo_nome_unico)

            shutil.move(pdf_caminho, novo_caminho)
            print(f"PDF mantido e renomeado para: {novo_caminho}")
            return True
        else:
            os.remove(pdf_caminho)
            print(f"PDF removido (não contém 'formulario'): {pdf_caminho}")
            return False

    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        return False

def calcular_hash_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
    
def obter_arquivo_mais_recente(pasta):
   arquivos = glob.glob(os.path.join(pasta, '*'))
   return max(arquivos, key=os.path.getctime) if arquivos else None

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')