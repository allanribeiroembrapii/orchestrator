import os
import sys

# Obter o diretório atual e o diretório raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Adicionar o diretório atual ao path para permitir importações absolutas
sys.path.append(current_dir)

# Adicionar o caminho do diretório raiz ao sys.path para importar o logger
sys.path.append(root_dir)

try:
    from logs.orchestrator_logs import OrchestratorLogger
except ImportError:
    sys.path.append(os.path.join(root_dir, "logs"))
    from logs.orchestrator_logs import OrchestratorLogger

# Importar funções necessárias
try:
    from connection.get_data import get_data
    from api_scripts.api_site_embrapii import api_site_embrapii
except ImportError:
    # Tentar importações relativas
    from .connection.get_data import get_data
    from .api_scripts.api_site_embrapii import api_site_embrapii


def main():
    # Inicializar o logger
    logger = OrchestratorLogger.get_instance()
    module_idx = logger.start_module("api_datapii")

    try:
        # Buscar dados
        print("🟡 get_data")
        get_data()
        logger.add_step(module_idx, "get_data", status="success")
        print("🟢 get_data")

        # Scripts
        print("🟡 api_site_embrapii")
        api_site_embrapii()
        logger.add_step(module_idx, "api_site_embrapii", status="success")
        print("🟢 api_site_embrapii")

        # Finalizar o log do módulo com sucesso
        logger.end_module(module_idx, "success")

    except Exception as e:
        # Registrar erro no log
        logger.end_module(module_idx, "error", error=e)
        # Re-lançar a exceção para manter o comportamento original
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro na execução do módulo api_datapii: {str(e)}")
        sys.exit(1)
