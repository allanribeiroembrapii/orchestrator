import sys
import os

# Get the root directory from command line arguments
if len(sys.argv) > 1:
    root_dir = sys.argv[1]

    # Convert backslashes to forward slashes
    root_dir = root_dir.replace("\\", "/")
    # Add trailing slash if not present
    if not root_dir.endswith("/"):
        root_dir += "/"

    # Add the root directory to the Python path
    sys.path.append(root_dir)

    # Import the logger and log the success
    try:
        from logs.orchestrator_logs import OrchestratorLogger

        logger = OrchestratorLogger.get_instance()
        logger.end_execution("success", "Todos os módulos executados com sucesso")
        print("Execução finalizada com sucesso e registrada no log")
    except Exception as e:
        print(f"Erro ao registrar o sucesso: {str(e)}")
        sys.exit(1)
else:
    print("Erro: Caminho raiz não fornecido")
    sys.exit(1)
