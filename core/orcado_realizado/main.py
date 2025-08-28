# Arquivo: main.py

import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv
from core.orcado_realizado.connect_sharepoint import SharepointClient


load_dotenv()
PASTA_SHAREPOINT_DESTINO = os.getenv("sharepoint_repositorio")

def buscar_e_salvar_orcado_realizado():
    """
    Esta função se conecta ao SQL Server, busca os dados, salva em um arquivo 
    Excel (.xlsx) e RETORNA O CAMINHO ABSOLUTO do arquivo.
    """
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
        SELECT * FROM db_bi_silver.sap.tb_orcd_realizado WHERE fg_delet = ''
    """

    conexao = None
    try:
        conexao = pyodbc.connect(string_de_conexao, autocommit=True)
        print("✅ Conexão bem-sucedida!")

        df = pd.read_sql(comando_sql, conexao)
        
        if not df.empty:
            # --- 4. SALVAR OS DADOS E GERAR CAMINHO ABSOLUTO ---
            output_dir = os.path.join(os.getenv("ROOT_ORCADO"), os.getenv("STEP_3_DATA_PROCESSED"))
            file_name = "orcado_realizado.xlsx"

            os.makedirs(output_dir, exist_ok=True)

            caminho_relativo = os.path.join(output_dir, file_name)

            # Converte o caminho para um caminho absoluto (ex: C:\Users\...)
            caminho_absoluto = os.path.abspath(caminho_relativo)

            df.to_excel(caminho_absoluto, index=False)
            print(f"✅ Arquivo '{caminho_absoluto}' salvo com sucesso!")

            # Retorna o caminho completo e sem ambiguidades
            return caminho_absoluto
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


def main():
    """
    Função principal que orquestra a execução do script.
    """
    print("🟡 Iniciando processo de extração de dados...")

    # 1. A função é chamada e seu resultado (o caminho do arquivo) é salvo na variável
    caminho_do_arquivo = buscar_e_salvar_orcado_realizado()

    # 2. Verificamos se o caminho foi retornado com sucesso
    if caminho_do_arquivo:
        # 3. CHAMADA CORRETA: Passamos a variável com o caminho para a função up_sharepoint
        print("Pasta de destino: ", PASTA_SHAREPOINT_DESTINO)
        sp = SharepointClient()
        sp.upload_file_to_folder(caminho_do_arquivo, PASTA_SHAREPOINT_DESTINO)
    else:
        print(
            "🔴 Upload para o SharePoint não foi executado porque o arquivo não foi gerado.")

    print("\n🟢 Processo finalizado.")


if __name__ == '__main__':
    main()
