import os
import sys

# Obter o diretório atual e o diretório raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Adicionar o diretório atual ao path para permitir importações absolutas
sys.path.append(current_dir)

# Adicionar o caminho do diretório raiz ao sys.path para importar o logger
sys.path.append(root_dir)

# Importar funções necessárias
try:
    from connection.get_data import get_data
    from api_scripts.api_site_embrapii import api_site_embrapii
except ImportError:
    # Tentar importações relativas
    from .connection.get_data import get_data
    from .api_scripts.api_site_embrapii import api_site_embrapii


def main():

    try:
        # Buscar dados
        print("🟡 get_data")
        get_data()

        print("🟢 get_data")

        # Scripts
        print("🟡 api_site_embrapii")
        api_site_embrapii()
        print("🟢 api_site_embrapii")

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
