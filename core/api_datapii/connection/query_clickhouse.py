import clickhouse_connect
import socket
import os
from dotenv import load_dotenv


load_dotenv()

ROOT = os.getenv('ROOT_CLICKHOUSE_QUERYS')
USUARIO = os.getenv('usuario_vpn')
SENHA = os.getenv('senha_vpn')
FORTICLIENT_PATH = os.getenv('forticlient_path')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')


def is_vpn_connected(host, port):
    """
    Função para verificar se a VPN está conectada
    host: str - IP do servidor ClickHouse
    port: int - Porta do servidor ClickHouse
    """
    try:
        socket.create_connection((host, port), timeout=5)
        return True  # Conexão bem-sucedida
    except (socket.timeout, OSError):
        return False  # Sem acesso ao banco (VPN pode estar desligada)



def query_clickhouse(host, port, user, password, query):
    """
    Função para consultar ao clickhouse e salvar o resultado em um arquivo CSV
    host: str - IP do servidor ClickHouse
    port: int - Porta do servidor ClickHouse
    user: str - Usuário do ClickHouse
    password: str - Senha do ClickHouse
    query: str - SQL
    """

    if is_vpn_connected(host, port):
        # Conectar ao ClickHouse
        client = clickhouse_connect.get_client(host=host, port=port, user=user, password=password)

        # Executa a query
        client.query_df(query)

    else:
        print("VPN NÃO conectada! Conecte-se à VPN e tente novamente.")


def query_clickhouse_com_retorno(host, port, user, password, query):
    if is_vpn_connected(host, port):
        client = clickhouse_connect.get_client(host=host, port=port, user=user, password=password)
        result = client.query(query)
        return result.result_rows
    else:
        print("VPN NÃO conectada! Conecte-se à VPN e tente novamente.")
        return None