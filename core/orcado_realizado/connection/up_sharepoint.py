# Arquivo: connection/up_sharepoint.py

import inspect
from dotenv import load_dotenv
from .office365.upload_files import upload_files
import os # Manter o os para outras variáveis de ambiente

# Carregar .env para as configurações do SharePoint
load_dotenv()

# Configurações do SharePoint (estas continuam úteis)
SHAREPOINT_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC = os.getenv('sharepoint_doc_library')

def up_sharepoint(caminho_absoluto_do_arquivo: str):
    """
    Esta função agora ACEITA um caminho de arquivo como parâmetro e o utiliza
    diretamente para fazer o upload.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    # Pega apenas o diretório do caminho completo do arquivo recebido
    # Ex: de "C:\temp\meu_arquivo.xlsx" pega "C:\temp"
    diretorio_do_arquivo = os.path.dirname(caminho_absoluto_do_arquivo)
    
    try:
        print(f"Iniciando upload da pasta: '{diretorio_do_arquivo}'")
        
        # A função upload_files espera um DIRETÓRIO (pasta), não um arquivo.
        # Por isso extraímos o diretório do caminho completo.
        upload_files(diretorio_do_arquivo, "dw_pii", SHAREPOINT_SITE,
                     SHAREPOINT_SITE_NAME, SHAREPOINT_DOC)
                     
        print("🟢 Upload para o SharePoint concluído com sucesso.")
        
    except FileNotFoundError:
        print(f"🔴 ERRO: A pasta para upload não foi encontrada: '{diretorio_do_arquivo}'")
    except Exception as e:
        print(f"🔴 Erro durante o upload para o SharePoint: {e}")

# A função zipar_arquivos pode continuar aqui se você a utiliza em outro lugar.
# Se ela não for mais necessária, pode ser removida.