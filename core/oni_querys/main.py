from start_clean import start_clean
from querys.companies.main_companies import main_companies
from connection.up_sharepoint import up_sharepoint
from connection.copy_sharepoint import copy_sharepoint


def oni_querys():
    
    # Start clean
    start_clean()

    # Copiar arquivo anterior do Sharepoint
    copy_sharepoint()

    # Executar querys
    main_companies()

    # Levar versão mais recente para o Sharepoint
    up_sharepoint()


if __name__ == "__main__":
    oni_querys()
