from core.rvg_repositorio_visuais_graficos.connection.get_data import get_arquivos, up_arquivos
import win32com.client
import os
from dotenv import load_dotenv
import pythoncom
import gc
import pyautogui
import time

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT_RVG")
FOLDER_XLS= os.path.abspath(os.path.join(ROOT, 'folder_xls'))
FOLDER_PPT= os.path.abspath(os.path.join(ROOT, 'folder_ppt'))

def main_rvg():
    try:
        # Buscar arquivo
        get_arquivos()

        # Atualizar excel
        # for filename in os.listdir(FOLDER_XLS):
        #     if filename.lower().endswith(".xlsx"):
        #         caminho_xls = os.path.join(FOLDER_XLS, filename)
        #         refresh_xls(caminho_xls)

        # up_arquivos(FOLDER_XLS, 'General/Repositório de Visuais Gráficos/Excel')

        atualizar_excel()

        #Atualizar ppt
        for filename in os.listdir(FOLDER_PPT):
            if filename.lower().endswith(".pptx"):
                caminho_ppt = os.path.join(FOLDER_PPT, filename)
                refresh_ppt(caminho_ppt)
        
        up_arquivos(FOLDER_PPT, 'General/Repositório de Visuais Gráficos/PowerPoint')


    except Exception as e:
        raise


def refresh_xls(caminho_arquivo):
    pythoncom.CoInitialize()
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.DisplayAlerts = False
        excel.Visible = False 

        wb = excel.Workbooks.Open(caminho_arquivo)

        # Atualiza todas as conexões de dados
        try:
            wb.RefreshAll()
        except Exception as e:
            print(f"Erro ao chamar RefreshAll: {e}")

        # Aguarda atualização completar
        excel.CalculateUntilAsyncQueriesDone()

        # Salva e fecha
        wb.Save()
        wb.Close()

    except Exception as e:
        print(f"Erro ao atualizar o arquivo Excel: {e}")

    finally:
        excel.Quit()
        del excel
        gc.collect()
        pythoncom.CoUninitialize()


def refresh_ppt(ppt):
    pythoncom.CoInitialize()

    # Instancia Excel primeiro (mantém aberto entre os gráficos)
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = False
    excel_app.DisplayAlerts = False

    # Instancia PowerPoint
    ppt_app = win32com.client.Dispatch("PowerPoint.Application")
    ppt_app.Visible = True
    ppt_app.DisplayAlerts = False

    presentation = ppt_app.Presentations.Open(ppt)

    for slide in presentation.Slides:
        for shape in slide.Shapes:
            try:
                if shape.HasChart:
                    chart = shape.Chart
                    try:
                        chart.ChartData.Activate()  # ativa a planilha vinculada
                        chart.Refresh()
                    except Exception as e:
                        print(f"Erro ao atualizar gráfico no slide {slide.SlideIndex}: {e}")
            except Exception as e:
                print(f"Erro inesperado no slide {slide.SlideIndex}: {e}")

    presentation.Save()
    presentation.Close()

    # Fecha os aplicativos (Excel por último)
    ppt_app.Quit()
    excel_app.Quit()

    # Limpeza de objetos COM
    del ppt_app
    del excel_app
    del presentation
    gc.collect()
    pythoncom.CoUninitialize()

    print("✅ Atualização de gráficos concluída.")
    pythoncom.CoUninitialize() 



def atualizar_excel():
    time.sleep(2)  # Tempo para você alternar para a área de trabalho

    # Tecla Windows
    pyautogui.press('win')
    time.sleep(1)

    # Digita "Excel"
    pyautogui.write('Excel')
    time.sleep(1)

    # Pressiona Enter para abrir o Excel
    pyautogui.press('enter')
    time.sleep(4)

    # Pressiona Tab para mover para o campo de pesquisa
    pyautogui.press('tab')
    time.sleep(1)

    # Digita o nome do arquivo (você pode ajustar conforme necessário)
    pyautogui.write('rvg_reposit')
    time.sleep(1)

    # Pressiona Enter para abrir o arquivo
    pyautogui.press('enter')
    time.sleep(5)

    # Pressiona Alt, S, G, A para Atualizar Tudo
    pyautogui.press('alt')
    time.sleep(0.5)
    pyautogui.press('s')
    time.sleep(0.5)
    pyautogui.press('g')
    time.sleep(0.5)
    pyautogui.press('a')
    print("⏳ Aguardando atualização...")

    # Aguarda 20 segundos
    time.sleep(20)

    # Fecha Excel com Alt+F4
    pyautogui.hotkey('alt', 'f4')
    time.sleep(2)
    print("✅ Atualização concluída e Excel fechado.")