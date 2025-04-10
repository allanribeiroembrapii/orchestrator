from connection.get_data import get_data
from api_scripts.api_site_embrapii import api_site_embrapii

def main():

    #Buscar dados
    get_data()

    #Scripts
    api_site_embrapii()

if __name__ == "__main__":
    main()