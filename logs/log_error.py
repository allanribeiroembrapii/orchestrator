import sys
import os

# Get the root directory and error details from command line arguments
if len(sys.argv) >= 4:
    root_dir = sys.argv[1]
    step_name = sys.argv[2]
    error_message = sys.argv[3]

    # Convert backslashes to forward slashes
    root_dir = root_dir.replace("\\", "/")
    # Add trailing slash if not present
    if not root_dir.endswith("/"):
        root_dir += "/"

    # Add the root directory to the Python path
    sys.path.append(root_dir)

    # Import the logger and log the error
    try:
        from logs.orchestrator_logs import OrchestratorLogger

        logger = OrchestratorLogger.get_instance()
        logger.add_step(-1, step_name, status="error", error=error_message)
        logger.end_execution("error", f"Falha em {step_name}")
        print(f"Erro registrado: {step_name} - {error_message}")
    except Exception as e:
        print(f"Erro ao registrar o erro: {str(e)}")
        sys.exit(1)
else:
    print("Erro: Argumentos insuficientes")
    print("Uso: python log_error.py <root_dir> <step_name> <error_message>")
    sys.exit(1)
