import sys
import os

# Get the root directory from the command line argument
if len(sys.argv) > 1:
    root_dir = sys.argv[1]
    # Convert backslashes to forward slashes
    root_dir = root_dir.replace("\\", "/")
    # Add trailing slash if not present
    if not root_dir.endswith("/"):
        root_dir += "/"

    # Add the root directory to the Python path
    sys.path.append(root_dir)

    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (orchestrator root)
    parent_dir = os.path.dirname(current_dir)
    # Add both to Python path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Import the logger and initialize it
    try:
        # Try direct import first (if running from the logs directory)
        try:
            from orchestrator_logs import OrchestratorLogger
        except ImportError:
            # If that fails, try the package import
            from logs.orchestrator_logs import OrchestratorLogger

        logger = OrchestratorLogger.get_instance()
        print("Logger JSON inicializado")
    except Exception as e:
        print(f"Erro ao inicializar o logger: {str(e)}")
        sys.exit(1)
else:
    print("Erro: Caminho raiz não fornecido")
    sys.exit(1)
