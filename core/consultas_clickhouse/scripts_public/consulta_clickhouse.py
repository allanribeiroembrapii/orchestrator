import clickhouse_connect
import socket
import os
import sys
from dotenv import load_dotenv

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

def is_vpn_connected(host, port):
    try:
        socket.create_connection((host, port), timeout=5)
        return True  # Conexão bem-sucedida
    except (socket.timeout, OSError):
        return False  # Sem acesso ao banco (VPN pode estar desligada)


def consulta_clickhouse(host, port, user, password, query, pasta, nome_arquivo):
    if is_vpn_connected(host, port):
        print("VPN conectada. Rodando a consulta...")

        # Conectar ao ClickHouse
        client = clickhouse_connect.get_client(host=host, port=port, user=user, password=password)

        # Executa a consulta e obtém os dados como DataFrame
        result = client.query_df(query)

        # Salvar o resultado em um arquivo CSV
        result.to_csv(os.path.abspath(os.path.join(ROOT, pasta ,f"{nome_arquivo}.csv")),
                      index=False, encoding="utf-8")

    else:
        print("VPN NÃO conectada! Conecte-se à VPN e tente novamente.")