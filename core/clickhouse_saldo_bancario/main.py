from core.clickhouse_saldo_bancario.connection.connect_vpn import connect_vpn, disconnect_vpn
from core.clickhouse_saldo_bancario.start_clean import start_clean
from core.clickhouse_saldo_bancario.querys.ws_agfinanceiro.ws_agfinanceiro import ws_agfinanceiro
from core.clickhouse_saldo_bancario.querys.ws_agfinanceiro.ws_agfinanceiro import ws_agfinanceiro
from core.clickhouse_saldo_bancario.connection.up_sharepoint import up_sharepoint


def main_agfinanceiro():

    #Start clean
    start_clean()

    #Ligar VPN
    # connect_vpn()

    #Executar querys
    ws_agfinanceiro()

    #Desligar VPN
    # disconnect_vpn()

    #Levar dados para o Sharepoint
    up_sharepoint()


if __name__ == "__main__":
    main_agfinanceiro()