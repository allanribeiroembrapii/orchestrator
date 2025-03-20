import os
import sys
from dotenv import load_dotenv
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

ARQUIVOS_BRUTOS = os.path.abspath(os.path.join(ROOT, 'qim_ues/arquivos_brutos'))

def criar_diretorio_se_nao_existir(diretorio):
    """
    Cria um diretório se ele não existir.
    
    Args:
        diretorio (str): Caminho do diretório a ser criado
    """
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
        print(f"Diretório criado: {diretorio}")
    return diretorio

def baixar_dados_srinfo_qim(driver):
    # Criar diretório para arquivos brutos se não existir
    criar_diretorio_se_nao_existir(ARQUIVOS_BRUTOS)
    
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

        # Abrir o dropdown
        dropdown_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-selection--single"))
        )
        dropdown_button.click()

        # Obter a quantidade de opções no dropdown
        options_css_selector = ".select2-results__option"
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, options_css_selector)))

        options = driver.find_elements(By.CSS_SELECTOR, options_css_selector)
        total_options = len(options)

        # Listas para armazenar DataFrames
        pa_qim = []
        resultados = []

        # Iterar sobre as opções
        for i in range(total_options):
            try:
                # Reabrir o dropdown antes de cada seleção
                dropdown_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-selection--single"))
                )
                dropdown_button.click()

                # Recapturar as opções após reabrir o dropdown
                options = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, options_css_selector))
                )

                # Selecionar a opção pelo índice
                option = options[i]
                option_text = option.text.strip()  # Capturar o texto da opção
                option.click()
                driver.get('https://srinfo.embrapii.org.br/analytics/new_summary/')

                index_pa_qim = extrair_textos(driver, option_text, pa_qim)
                extrair_tabelas(driver, index_pa_qim, resultados, pa_qim)            

            except Exception as e:
                print(f"Erro ao selecionar a opção {i}: {e}")

        # Salvar os DataFrames
        if pa_qim:
            final_df = pd.concat(pa_qim, ignore_index=True)
            final_df.to_excel(os.path.join(ARQUIVOS_BRUTOS, 'pa_qim.xlsx'), index=True)

        if resultados:
            final_df2 = pd.concat(resultados, ignore_index=True)
            final_df2.to_excel(os.path.join(ARQUIVOS_BRUTOS, 'resultados.xlsx'), index=False)

    except Exception as e:
        print(f"Erro ao baixar dados do SRInfo para QIM UES: {e}")
        raise e


def extrair_textos(driver, option_text, pa_qim):
    try:
        # Extrair dados para pa_qim
        xpath_pa = '//*[@id="qim-summary"]/div[1]/div/div[1]/div/div/span[3]'
        xpath_data ='//*[@id="qim-summary"]/div[1]/div/div[1]/div/div/span[2]'
        xpath_referencia = '//*[@id="qim-summary"]/div[1]/div/div[2]/span'
        xpath_nota_qim = '//*[@id="qim-summary"]/div[4]/div/div/div[1]/div/div[1]/h3'

        pas = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_pa))
        )
        datas = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_data))
        )
        referencias = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_referencia))
        )
        notas = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_nota_qim))
        )

        pa = [elemento.text.strip() for elemento in pas]
        data = [elemento.text.strip() for elemento in datas]
        referencia = [elemento.text.strip() for elemento in referencias]
        nota = [elemento.text.strip() for elemento in notas]

        # Criar DataFrame com os dados para pa_qim
        df = pd.DataFrame([[option_text]], columns=['unidade_embrapii'])  # Colocar option_text dentro de uma lista
        df['pa_vigente'] = pa
        df['data_inicio_pa'] = data
        df['periodo_referencia'] = referencia
        df['nota_qim'] = nota

        # Adicionar o DataFrame à lista pa_qim
        pa_qim.append(df)

        # Capturar o índice atual
        index_pa_qim = len(pa_qim) - 1  # Índice na lista pa_qim

        return index_pa_qim

    except Exception as e:
        print(f"Erro ao extrair textos: {e}")


def extrair_tabelas(driver, index_pa_qim, resultados, pa_qim):
    # Esperar o botão ser clicável e clicar nele
    try:
        tabela_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="qim-summary"]/div[4]/div/div/div[2]/div/div/div[2]/div[1]/div/button'))
        )
        tabela_button.click()
    except Exception as e:
        print(f"Erro ao clicar no botão: {e}")

    # Esperar pela tabela aparecer após o clique
    try:
        tabela = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="object-qim-list"]'))
        )
        linhas = tabela.find_elements(By.XPATH, ".//tbody/tr")

        tabela_dados = []
        for linha in linhas:
            celulas = linha.find_elements(By.XPATH, ".//td")
            valores = [celula.text.strip() for celula in celulas]
            valores.insert(0, index_pa_qim)  # Usar índice do pa_qim como referência

            # Adicionar as colunas adicionais do DataFrame pa_qim (unidade_embrapii, pa_vigente, periodo_referencia)
            pa_qim_row = pa_qim[index_pa_qim]
            unidade_embrapii = pa_qim_row['unidade_embrapii'].iloc[0]
            pa_vigente = pa_qim_row['pa_vigente'].iloc[0]
            data_inicio_pa = pa_qim_row['data_inicio_pa'].iloc[0]
            periodo_referencia = pa_qim_row['periodo_referencia'].iloc[0]

            valores.insert(1, unidade_embrapii)
            valores.insert(2, pa_vigente)
            valores.insert(3, data_inicio_pa)
            valores.insert(4, periodo_referencia)

            tabela_dados.append(valores)

        # Criar DataFrame com os dados da tabela e as novas colunas
        df_resultados = pd.DataFrame(
            tabela_dados, 
            columns=["id_pa", "unidade_embrapii", "pa_vigente", "data_inicio_pa", "periodo_referencia", "num_meta", "titulo_meta", "peso_meta", "resultado"]
        )
        resultados.append(df_resultados)

    except Exception as e:
        print(f"Erro ao extrair tabelas: {e}")
