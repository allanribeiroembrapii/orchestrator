from dotenv import load_dotenv
import os
import sys
from core.clickhouse_saldo_bancario.connection.query_clickhouse import query_clickhouse
import pandas as pd

load_dotenv()

ROOT = os.getenv('ROOT_SALDO_BANCARIO')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def clickhouse_saldo_bancario():
    """
    Dados de empresas, sem inativação e sem CNPJ nulo
    """
    query = """
        SELECT * FROM db_ouro.saldo_bancario_bb_periodo
    """
    nome_arquivo = "saldo_bancario_bb_periodo"

    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Ajustar coluna de data
    df_raw['dt_carga'] = pd.to_datetime(df_raw['dt_carga'])

    # Filtrar data mais recente
    data_mais_recente = df_raw['dt_carga'].max()
    df_raw = df_raw[df_raw['dt_carga'] == data_mais_recente]

    # Manter colunas desejadas
    df_raw = df_raw[['id_cnta_corrente', 'vl_total', 'dt_carga']]

    # Remover timezone da dt_carga (Excel não aceita)
    df_raw['dt_carga'] = df_raw['dt_carga'].dt.tz_localize(None)

    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"agfin_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)


def clickhouse_saldo_bancario_historico():
    """
    Dados de empresas, sem inativação e sem CNPJ nulo
    """
    query = """
        SELECT * FROM db_ouro.saldo_bancario_bb_periodo
    """
    nome_arquivo = "saldo_bancario_bb_historico"

    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Ajustar coluna de data
    df_raw['dt_carga'] = pd.to_datetime(df_raw['dt_carga'])

    # Manter colunas desejadas
    df_raw = df_raw[['id_cnta_corrente', 'vl_total', 'dt_carga']]

    # Remove duplicatas
    df_raw = df_raw.drop_duplicates()

    # Remover timezone da dt_carga (Excel não aceita)
    df_raw['dt_carga'] = df_raw['dt_carga'].dt.tz_localize(None)

    # Remover cargas duplicadas no mesmo dia por conta (ficar com a mais antiga do dia)
    df_raw['dia'] = df_raw['dt_carga'].dt.normalize()  # zera hora, fica só a data
    df_raw = (
        df_raw
        .sort_values(['id_cnta_corrente', 'dia', 'dt_carga'])              # mais antiga primeiro
        .drop_duplicates(subset=['id_cnta_corrente', 'dia'], keep='first') # mantém a 1ª do dia
        .drop(columns='dia')
    )

    # Calcular variação diária por conta
    df_raw = df_raw.sort_values(by=['id_cnta_corrente', 'dt_carga'])

    # Calcular a diferença de vl_total entre dias consecutivos por conta
    df_raw['var_diario'] = df_raw.groupby('id_cnta_corrente')['vl_total'].diff()
    df_raw['var_diario'] = df_raw['var_diario'].fillna(0)


    # Salvar em formato Excel
    path_file_processed = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, f"agfin_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)

