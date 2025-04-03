from start_clean import start_clean
from connection.copy_sharepoint import copy_sharepoint
from querys.companies.main_companies import main_companies
from connection.up_sharepoint import up_sharepoint


def oni_querys():

    #Start clean
    start_clean()

    #Buscar empresas no Sharepoint
    copy_sharepoint()

    #Executar querys
    main_companies()

    #Levar dados para o Sharepoint
    up_sharepoint()


if __name__ == "__main__":
    oni_querys()