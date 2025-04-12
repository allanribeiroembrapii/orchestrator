import os
import sys
from dotenv import load_dotenv
import win32com.client as win32
import time

# Carregar variáveis de ambiente
load_dotenv()
# Carrega o .env da raiz do projeto para obter ROOT_PIPELINE
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
ROOT = os.getenv("ROOT_PIPELINE")

# Caminhos
DWPII_UP = os.path.abspath(os.path.join(ROOT, "DWPII_up"))
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, "office365_api"))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

from office365_api.upload_files import upload_files

# Definir caminhos
SNAPSHOT_FOLDER = os.path.abspath(os.path.join(ROOT, "report_snapshot"))
SNAPSHOT_FILE = os.path.abspath(os.path.join(SNAPSHOT_FOLDER, "report_snapshot_embrapii.xlsx"))
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")


def gerar_report_snapshot():
    # Inicializar o Excel
    excel = win32.gencache.EnsureDispatch("Excel.Application")
    excel.Visible = False

    # Abrir a planilha
    workbook = excel.Workbooks.Open(SNAPSHOT_FILE)

    # Atualizar todas as conexões e consultas de dados
    workbook.RefreshAll()

    # Aguardar a conclusão da atualização (adicionar um atraso)
    print("SNAPSHOT: aguardando a atualização das consultas...")
    time.sleep(120)

    # Definir caminho para salvar o PDF
    pdf_path = os.path.join(SNAPSHOT_FOLDER, "report_snapshot_embrapii.pdf")

    # Exportar para PDF
    workbook.ExportAsFixedFormat(0, pdf_path)

    # salvar
    workbook.Save()

    # Fechar o workbook e o Excel
    workbook.Close(False)
    excel.Application.Quit()

    levar_relatorio_snapshot()


def levar_relatorio_snapshot():
    upload_files(SNAPSHOT_FOLDER, "Reports", SHAREPOINT_SITE, SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
