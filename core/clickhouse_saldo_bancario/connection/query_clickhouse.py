import clickhouse_connect
import socket
import os
import sys
from dotenv import load_dotenv


load_dotenv()

ROOT = os.getenv('ROOT_SALDO_BANCARIO')
USUARIO = os.getenv('usuario_vpn')
SENHA = os.getenv('senha_vpn')
FORTICLIENT_PATH = os.getenv('forticlient_path')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
# sys.path.append(ROOT)


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



def query_clickhouse(host, port, user, password, query, nome_arquivo, pasta=STEP_1_DATA_RAW):
    """
    Função para consultar ao clickhouse e salvar o resultado em um arquivo CSV
    host: str - IP do servidor ClickHouse
    port: int - Porta do servidor ClickHouse
    user: str - Usuário do ClickHouse
    password: str - Senha do ClickHouse
    query: str - Consulta SQL
    pasta: str - Pasta onde o arquivo será salvo
    nome_arquivo: str - Nome do arquivo CSV
    """

    if is_vpn_connected(host, port):
        # Conectar ao ClickHouse
        client = clickhouse_connect.get_client(host=host, port=port, user=user, password=password)

        # Executa a consulta e obtém os dados como DataFrame
        result = client.query_df(query)

        # Salvar o resultado em um arquivo CSV
        result.to_csv(os.path.abspath(os.path.join(ROOT, pasta ,f"{nome_arquivo}.csv")),
                    index=False, encoding="utf-8")
    else:
        print("VPN NÃO conectada! Conecte-se à VPN e tente novamente.")