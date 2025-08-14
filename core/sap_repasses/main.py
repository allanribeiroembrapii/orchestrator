# Arquivo: main.py

import pyodbc
import pandas as pd
import os
import inspect
from dotenv import load_dotenv
from core.sap_repasses.connection.sharepoint import get_files_from_sharepoint, sharepoint_post
from core.sap_repasses.start_clean import start_clean
from core.sap_repasses.classificar_repasses import classificar_repasses

def buscar_e_salvar_sap_repasse():
    """
    Esta função se conecta ao SQL Server, busca os dados, salva em um arquivo 
    Excel (.xlsx) e RETORNA O CAMINHO ABSOLUTO do arquivo.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    load_dotenv()

    # --- 1. CONFIGURAÇÕES DA CONEXÃO ---
    servidor = os.getenv("MS_DB_SERVER")
    banco_de_dados = os.getenv("MS_DB_DATABASE")
    usuario = os.getenv("MS_DB_USER")
    senha = os.getenv("MS_DB_PASSWORD")
    driver_name = os.getenv("MS_DRIVER_NAME", "SQL Server")

    if not all([servidor, banco_de_dados, usuario, senha, driver_name]):
        print("❌ ERRO: Verifique as variáveis de ambiente no arquivo .env.")
        return None

    string_de_conexao = (
        f"DRIVER={{{driver_name}}};"
        f"SERVER={servidor};"
        f"DATABASE={banco_de_dados};"
        f"UID={usuario};"
        f"PWD={senha};"
    )

    comando_sql = """
        SELECT * FROM db_bi_silver.sap_legado.repasses_unidades WHERE icativo = 1
    """

    conexao = None
    try:
        conexao = pyodbc.connect(string_de_conexao, autocommit=True)
        df = pd.read_sql(comando_sql, conexao)

        if not df.empty:
            output_dir = os.path.join(os.getenv("ROOT_SAP_REPASSE"), os.getenv("STEP_1_DATA_RAW"))
            file_name = "sap_raw.xlsx"
            os.makedirs(output_dir, exist_ok=True)
            caminho_relativo = os.path.join(output_dir, file_name)
            caminho_absoluto = os.path.abspath(caminho_relativo)
            df.to_excel(caminho_absoluto, index=False)

        else:
            print("❌ Nenhum dado encontrado para salvar.")
            return None

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"❌ ERRO de Conexão ou SQL: {sqlstate} - {ex}")
        return None
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
        return None
    finally:
        if conexao:
            conexao.close()
            print("🟢 " + inspect.currentframe().f_code.co_name)

def main():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    start_clean()
    buscar_e_salvar_sap_repasse()
    get_files_from_sharepoint()
    classificar_repasses()
    sharepoint_post()
    
    print("🟢 " + inspect.currentframe().f_code.co_name)


if __name__ == '__main__':
    main()
