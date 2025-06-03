import os
import sys
from .connection.get_data import get_data
from .api_scripts.api_site_embrapii import api_site_embrapii
from .api_scripts.api_embrapii_estados import api_embrapii_nos_estados

def main():
    try:
        # Buscar dados
        get_data()

        # Scripts
        api_site_embrapii()
        api_embrapii_nos_estados()

    except Exception as e:
        # Registrar erro no log
        # Re-lançar a exceção para manter o comportamento original
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro na execução do módulo api_datapii: {str(e)}")
        sys.exit(1)
