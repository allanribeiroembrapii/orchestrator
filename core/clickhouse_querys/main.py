from connection.connect_vpn import connect_vpn, disconnect_vpn
from start_clean import start_clean
from querys.ws_projetos_modelo_embrapii.ws_main import ws_projetos_modelo_embrapii


def main():

    #Start clean
    start_clean()

    #Ligar VPN
    # connect_vpn()

    #Executar querys
    ws_projetos_modelo_embrapii()

    #Desligar VPN
    # disconnect_vpn()


if __name__ == "__main__":
    main()