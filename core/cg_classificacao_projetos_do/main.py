import os
import inspect
import shutil
import win32com.client as win32
import pandas as pd
from dotenv import load_dotenv
from core.cg_classificacao_projetos_do.office365_api.download_files import get_file
from core.cg_classificacao_projetos_do.office365_api.upload_files import upload_files
from core.cg_classificacao_projetos_do.connect_sharepoint import SharepointClient
from datetime import datetime
import time
import pyautogui
import pygetwindow as gw


# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv('ROOT_CG_CLASSIFICACAO_PROJETOS_DO')
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')
RAW_CLASS_PROJETOS = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw', 'classificacao_projeto.xlsx'))
RAW_CLASS_PROJETOS_CG = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw', 'CG_Classificação de Projetos.xlsx'))
RAW_UE_FONTE_PRIORITARIO = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw', 'ue_fonte_recurso_prioritario.xlsx'))
RAW_PORTFOLIO = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw', 'portfolio.xlsx'))
SA_CLASS_PROJETOS_CG = os.path.abspath(os.path.join(ROOT, 'step_2_stage_area', 'classificacao_projeto_cg.xlsx'))
DP_CLASS_PROJETOS_CG = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed', 'classificacao_projeto_cg.xlsx'))
STEP3 = os.path.join(ROOT, "step_3_data_processed")
OUTPUT = os.path.join(ROOT, "output")
OUTPUT_CG_PROJETOS = os.path.abspath(os.path.join(OUTPUT, 'CG_Classificação de Projetos.xlsx'))

# Dicionário de Calls
CALL_SIMPLIFICADA = {
    "BNDES 1": "BNDES",
    "BNDES 2 Bioeconomia Florestal": "BNDES",
    "BNDES 2 Bioeconomia Florestal; SEBRAE Ciclo Integrado": "BNDES",
    "BNDES 2 Bioeconomia Florestal; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
    "BNDES 2 Defesa": "BNDES",
    "BNDES 2 Defesa; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
    "BNDES 2 Economia Circular": "BNDES",
    "BNDES 2 Economia Circular; SEBRAE Ciclo Integrado": "BNDES",
    "BNDES 2 Materiais Avançados": "BNDES",
    "BNDES 2 Novos Biocombustíveis": "BNDES",
    "BNDES 2 Novos Biocombustíveis; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
    "BNDES 2 Tec. Estratégicas SUS": "BNDES",
    "BNDES 2 Tec. Estratégicas SUS; SEBRAE Ciclo Integrado": "BNDES",
    "BNDES 2 Trans. Digital - Conectividade": "BNDES",
    "BNDES 2 Trans. Digital - Conectividade; SEBRAE Ciclo Integrado": "BNDES",
    "BNDES 2 Trans. Digital - Conectividade; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
    "BNDES 2 Trans. Digital - Soluções Digitais": "BNDES",
    "BNDES 2 Trans. Digital - Soluções Digitais; SEBRAE 2º CONTRATO": "BNDES",
    "BNDES 2 Trans. Digital - Soluções Digitais; SEBRAE Ciclo Integrado": "BNDES",
    "BNDES 2 Trans. Digital - Soluções Digitais; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
    "Contrato de Gestão 1": "CG",
    "Contrato de Gestão 2": "CG",
    "Contrato de Gestão Ciclo 2": "CG",
    "Contrato de Gestão Ciclo 2; SEBRAE 3": "CG",
    "Min. Saúde 1": "CG",
    "PPI 1": "PPI",
    "ROTA 1": "ROTA",
    "ROTA 1; SEBRAE 2º CONTRATO": "ROTA",
    "ROTA 1; SEBRAE Ciclo Integrado": "ROTA",
    "ROTA 1; SEBRAE Ciclo Integrado 4º Contrato": "ROTA",
    "ROTA 2030 Estruturante": "ROTA",
    "Rota Startup 1": "ROTA",
    "SEBRAE 1º CONTRATO": "CG",
    "SEBRAE 2º CONTRATO": "CG",
    "SEBRAE 3": "CG",
    "SEBRAE Ciclo Integrado": "CG",
    "SEBRAE Ciclo Integrado 4º Contrato": "CG",
}

def puxar_planilhas():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    #Definindo nomes das pastas
    data_raw = os.path.join(ROOT, "step_1_data_raw")
    stage_area = os.path.join(ROOT, "step_2_stage_area")
    data_processed = os.path.join(ROOT, "step_3_data_processed")
    output = os.path.join(ROOT, "output")
    
    #Apagar arquivos
    apagar_arquivos_pasta(data_raw)
    apagar_arquivos_pasta(stage_area)
    apagar_arquivos_pasta(data_processed)
    apagar_arquivos_pasta(output)

    sp = SharepointClient()

    pasta_srinfo = "DWPII/srinfo"
    pasta_unidades = "DWPII/unidades_embrapii"

    lista_arquivos = {
        pasta_srinfo: {
            "portfolio",
            "classificacao_projeto",
            "CG_Classificação de Projetos",
        },
        pasta_unidades: {
            "ue_fonte_recurso_prioritario",
        },
    }

    baixar_arquivos(sp, lista_arquivos, data_raw)

    print("🟢 " + inspect.currentframe().f_code.co_name)

def baixar_arquivos(sp, lista, inputs):
    for pasta, nomes in lista.items():
        for nome in nomes:
            filename = f"{nome}.xlsx"
            remote_path = f"{pasta}/{filename}"
            local_file = os.path.join(inputs, filename)
            print(f"⬇️  Baixando: {remote_path} -> {local_file}")
            sp.download_file(remote_path, local_file)

def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é uma pasta; se não for, cria
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            return
        
        # Lista todos os arquivos na pasta
        arquivos = os.listdir(caminho_pasta)
        
        # Apaga cada arquivo na pasta
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
    except Exception as e:
        print(f"🔴 Ocorreu um erro ao apagar os arquivos: {e}")

def preparar_dados():
    """
    Comparar as duas planilhas de classificação de projetos e adicionar as novas linhas em classificacao_projeto_cg.xlsx
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        # Definir os dataframes
        df_class_projeto = pd.read_excel(RAW_CLASS_PROJETOS)
        df_class_projeto = df_class_projeto[df_class_projeto["Áreas de Aplicação"] == "Saúde"]
        df_class_projeto_cg = pd.read_excel(RAW_CLASS_PROJETOS_CG)
        df_portfolio = pd.read_excel(RAW_PORTFOLIO)
        df_ue_prioritario = pd.read_excel(RAW_UE_FONTE_PRIORITARIO, sheet_name="unidades_embrapii")
        
        # Garantir que a coluna "Código" está como string para evitar problemas de comparação
        df_class_projeto["Código"] = df_class_projeto["Código"].astype(str)
        df_class_projeto_cg["Código"] = df_class_projeto_cg["Código"].astype(str)
        
        # Identificar os registros que estão em df_class_projeto, mas não em df_class_projeto_cg
        novos_registros = df_class_projeto[~df_class_projeto["Código"].isin(df_class_projeto_cg["Código"])]
        
        # Selecionar apenas as colunas que existem em df_class_projeto_cg
        colunas_comuns = [col for col in df_class_projeto.columns if col in df_class_projeto_cg.columns]
        novos_registros = novos_registros[colunas_comuns]
        
        # Preencher valores padrão para as novas colunas
        if "AUT_Classificação CG" in df_class_projeto_cg.columns:
            novos_registros["AUT_Classificação CG"] = "Não definido"
        if "AUT_Critério" in df_class_projeto_cg.columns:
            novos_registros["AUT_Critério"] = "Não definido"
        if "DO_Status Análise" in df_class_projeto_cg.columns:
            novos_registros["DO_Status Análise"] = "Não analisado"
        
        # Preencher "Data da Extração SRInfo" com o primeiro valor da coluna "data_extracao_dados" em df_portfolio
        if "Data da Extração SRInfo" in df_class_projeto_cg.columns and "data_extracao_dados" in df_portfolio.columns:
            data_extracao = df_portfolio["data_extracao_dados"].iloc[0]
            novos_registros["Data da Extração SRInfo"] = data_extracao
        
        # Remover colunas completamente vazias antes de concatenar
        novos_registros = novos_registros.dropna(how='all', axis=1)
        
        # Concatenar os novos registros ao dataframe existente
        df_class_projeto_cg = pd.concat([df_class_projeto_cg, novos_registros], ignore_index=True)

        # Call simplificada em df_class_projeto_cg
        if "Call" in df_class_projeto_cg.columns:
            df_class_projeto_cg["Call_Simplificada"] = df_class_projeto_cg["Call"].map(CALL_SIMPLIFICADA).fillna("Não informado")
        
        # Fonte prioritária de recursos
        if "Unidade EMBRAPII" in df_class_projeto_cg.columns and "unidade_embrapii" in df_ue_prioritario.columns:
            mapeamento_fonte = df_ue_prioritario.set_index("unidade_embrapii")["fonte_prioritaria_recursos_sgf_2"].to_dict()
            df_class_projeto_cg["Fonte Prioritária da UE"] = df_class_projeto_cg["Unidade EMBRAPII"].map(mapeamento_fonte)
            df_class_projeto_cg["Fonte Prioritária da UE"].fillna("Não informado", inplace=True)

        # Salvar a planilha atualizada
        df_class_projeto_cg.to_excel(SA_CLASS_PROJETOS_CG, index=False)
        
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")

def classificar_cg():
    """
    Realizar a pré-classificação dos projetos.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        df_class_projeto_cg = pd.read_excel(SA_CLASS_PROJETOS_CG)
        
        # Aplicar regras de classificação somente para registros não definidos
        filtro_nao_definido = df_class_projeto_cg["AUT_Classificação CG"] == "Não definido"

        # Caso nenhuma regra tenha sido aplicada, definir como Indefinido
        df_class_projeto_cg.loc[filtro_nao_definido & (df_class_projeto_cg["AUT_Classificação CG"] == "Não definido"), ["AUT_Classificação CG", "AUT_Critério"]] = ["Não se aplica", ""]
        
        # Regra 3: Ministério da Ciência, Tecnologia e Inovação
        df_class_projeto_cg.loc[filtro_nao_definido & (df_class_projeto_cg["Fonte Prioritária da UE"] == "MCTI"), ["AUT_Classificação CG", "AUT_Critério"]] = ["MCTI", "Fonte prioritária da UE"]

        # Regra 2: Ministério da Educação
        df_class_projeto_cg.loc[filtro_nao_definido & (df_class_projeto_cg["Fonte Prioritária da UE"] == "MEC"), ["AUT_Classificação CG", "AUT_Critério"]] = ["MEC", "Fonte prioritária da UE"]
        
        # Regra 1: Ministério da Saúde
        df_class_projeto_cg.loc[filtro_nao_definido & (df_class_projeto_cg["Áreas de Aplicação"] == "Saúde"), ["AUT_Classificação CG", "AUT_Critério"]] = ["MS", "Área de Aplicação"]
        df_class_projeto_cg.loc[filtro_nao_definido & (df_class_projeto_cg["Fonte Prioritária da UE"] == "MS"), ["AUT_Classificação CG", "AUT_Critério"]] = ["MS", "Fonte prioritária da UE"]
        
        # Regra 0: Não se aplica
        df_class_projeto_cg.loc[filtro_nao_definido & (df_class_projeto_cg["Call_Simplificada"] != "CG"), ["AUT_Classificação CG", "AUT_Critério"]] = ["Não se aplica", ""]
        
        # Salvar a planilha atualizada
        df_class_projeto_cg.to_excel(DP_CLASS_PROJETOS_CG, index=False)
        
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")

def add_novas_linhas_tratada():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        # Buscar os dados
        df_raw = pd.read_excel(RAW_CLASS_PROJETOS_CG, sheet_name="analise_do")
        df_processed = pd.read_excel(DP_CLASS_PROJETOS_CG)
        df_processed = df_processed[df_processed["Call_Simplificada"] == "CG"]
        df_processed = df_processed[df_processed["Fonte Prioritária da UE"] != "MS"]
        df_portfolio = pd.read_excel(RAW_PORTFOLIO)
        
        # Comparar os arquivos e identificar novos registros
        df_novos_registros = df_processed[~df_processed["Código"].isin(df_raw["Código"])]

        # contar número de novos registros
        novos_registros = df_novos_registros.shape[0]
        
        # Eliminar colunas desnecessárias
        colunas_remover = ["DO_Análise", "DO_Data Análise", "DO_Responsável Análise", "DO_Observações"]
        df_novos_registros = df_novos_registros.drop(columns=[col for col in colunas_remover if col in df_novos_registros.columns], errors="ignore")
        
        # Converter colunas de data para string formatada
        for col in df_novos_registros.select_dtypes(include=["datetime64"]).columns:
            df_novos_registros[col] = df_novos_registros[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Abrir o Excel via COM object
        excel = win32.gencache.EnsureDispatch("Excel.Application")
        excel.Visible = False  # Manter o Excel oculto durante a execução
        workbook = excel.Workbooks.Open(RAW_CLASS_PROJETOS_CG)
        sheet = workbook.Sheets("analise_do")
        
        # Encontrar a primeira linha vazia na coluna A
        last_row = sheet.Cells(sheet.Rows.Count, 1).End(-4162).Row + 1  # xlUp equivalente
        
        # Inserir os dados no Excel a partir da primeira linha vazia
        for i, row in enumerate(df_novos_registros.itertuples(index=False, name=None), start=last_row):
            for j, value in enumerate(row, start=1):
                sheet.Cells(i, j).Value = str(value) if isinstance(value, pd.Timestamp) else value
        

        # Remover valor 65535 das colunas B, I, Q, R, T nas linhas inseridas
        colunas_alvo = [2, 9, 17, 18, 20]
        for i in range(last_row, last_row + len(df_novos_registros)):
            for col in colunas_alvo:
                if sheet.Cells(i, col).Value == 65535:
                    sheet.Cells(i, col).Value = ""
        for i in range(last_row, last_row + len(df_novos_registros)):
            if sheet.Cells(i, 17).Value == "Área de Aplicação":
                sheet.Cells(i, 17).Value = ""
        
        # Adicionar valores na coluna I - Valor Total Embrapii
        # df_portfolio["valor_total"] = (
        #     df_portfolio["valor_embrapii"].fillna(0) +
        #     df_portfolio["valor_empresa"].fillna(0) +
        #     df_portfolio["valor_unidade_embrapii"].fillna(0) +
        #     df_portfolio["valor_sebrae"].fillna(0)
        # )
        df_portfolio["valor_total"] = df_portfolio["valor_embrapii"].fillna(0)

        # Criar um dicionário para lookup rápido (como um PROCV)
        mapa_valores = df_portfolio.set_index("codigo_projeto")["valor_total"].to_dict()

        # Preencher a coluna I com os valores correspondentes da coluna A (código do projeto)
        for i in range(last_row, last_row + len(df_novos_registros)):
            codigo = sheet.Cells(i, 1).Value  # Coluna A = código do projeto
            valor_total = mapa_valores.get(codigo, "")
            sheet.Cells(i, 9).Value = valor_total  # Coluna I = coluna 9


        # Salvar e fechar o arquivo Excel
        workbook.Save()
        workbook.Close()
        excel.Quit()
        
        # Fazer uma cópia do arquivo para a pasta OUTPUT
        shutil.copy(RAW_CLASS_PROJETOS_CG, os.path.join(OUTPUT, os.path.basename(RAW_CLASS_PROJETOS_CG)))
        
        print("🟢 " + inspect.currentframe().f_code.co_name)

        return novos_registros
    
    except Exception as e:
        print(f"🔴 Erro: {e}")

def levar_sharepoint():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        upload_files(OUTPUT, "DWPII/srinfo", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")


def sharepoint_post():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        sp = SharepointClient()

        # Listar arquivos na pasta
        for nome_arquivo in os.listdir(OUTPUT):
            caminho_do_arquivo = os.path.join(OUTPUT, nome_arquivo)
            if os.path.isfile(caminho_do_arquivo):
                sp.upload_file_to_folder(caminho_do_arquivo, 'DWPII/srinfo')

        # upload_files(
        #     STEP_3_DATA_PROCESSED, "dw_pii", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC
        # )
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")

def duracao_tempo(inicio, fim):
    duracao = fim - inicio
    horas, resto = divmod(duracao.total_seconds(), 3600)
    minutos, segundos = divmod(resto, 60)
    
    # Formatá-la como uma string no formato HH:MM:SS
    duracao_formatada = f'{int(horas):02}:{int(minutos):02}:{int(segundos):02}'

    return duracao_formatada

def ordenar_com_pyautogui():
    # Abre o Excel com o arquivo
    excel = win32.gencache.EnsureDispatch("Excel.Application")
    excel.Visible = True
    excel.WindowState = -4137 
    workbook = excel.Workbooks.Open(OUTPUT_CG_PROJETOS)

    # Espera o Excel carregar (ajuste se necessário)
    time.sleep(5)

    for window in gw.getWindowsWithTitle('Excel'):
        if window.isMinimized:
            window.restore()
        window.activate()
        break  # Ativa a primeira janela do Excel encontrada

    time.sleep(3)

    # Seleciona a célula ativa e navega até E1
    pyautogui.hotkey('ctrl', 'up')
    pyautogui.hotkey('ctrl', 'left')
    for _ in range(4):
        pyautogui.press('right')

    # Acessa Alt+C, depois S, depois Z para ordenar decrescente
    time.sleep(0.5)
    pyautogui.keyDown('alt')
    pyautogui.press('c')
    pyautogui.keyUp('alt')
    time.sleep(0.5)
    pyautogui.press('s')  # Classificar
    time.sleep(0.5)
    pyautogui.press('z')  # Decrescente

    time.sleep(1)

    # Salvar e fechar
    workbook.Save()
    workbook.Close(SaveChanges=True)
    excel.Quit()

def molde_email(dados, hoje):
    return f"""
    <div class="container">
        <div style="margin: 10px">
            <b>Planilha de Classificação de Projetos CG-MS atualizada: {hoje}</b>
            <ul>
                <li>Novos registros: <b>{dados['novos_registros']}</b></li>
            </ul>
        </div>
        <span>
            Link da planilha: <a href="https://embrapii.sharepoint.com/:x:/r/sites/GEPES/Documentos%20Compartilhados/DWPII/srinfo/CG_Classifica%C3%A7%C3%A3o%20de%20Projetos.xlsx?d=w2957507e953c4f91849d72517de138ff&csf=1&web=1&e=LCu6js">clique aqui</a>
        </span>
    </div>
    """

def alerta_email(novos_registros):

    # Dados finais para o email
    dados = {
        'novos_registros': novos_registros,
    }

    data_formatada = datetime.today().strftime('%d/%m/%Y')
    # Gera HTML e envia
    html = molde_email(dados, data_formatada)
    enviar_email(html)

def enviar_email(html):
    print("🟡 " + inspect.currentframe().f_code.co_name)
    destinatarios = [
        "allan.ribeiro@embrapii.org.br",
        "milena.goncalves@embrapii.org.br",
        "juliana.oliveira@embrapii.org.br",
        "eduardo.duarte@embrapii.org.br",
        "emanoel.querette@embrapii.org.br"
    ]

    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = ";".join(destinatarios)
    mail.Subject = "🤖 - Projetos CG MS - Saúde | Alerta de Atualização"
    mail.HTMLBody = html

    mail.Send()
    print("🟢 " + inspect.currentframe().f_code.co_name)


def main():
    #início
    print('Início: ', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    inicio = datetime.now()
    
    #funções
    puxar_planilhas()
    preparar_dados()
    classificar_cg()
    novos_registros = add_novas_linhas_tratada()
    ordenar_com_pyautogui()
    sharepoint_post()
    alerta_email(novos_registros)

    #fim
    fim = datetime.now()
    duracao = duracao_tempo(inicio, fim)
    print(f'Duração total: {duracao}')
    print('Fim: ', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()