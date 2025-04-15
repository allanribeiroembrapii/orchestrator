import json
import os
import time
from datetime import datetime
import traceback
from logs.logs_handler import JsonLogger


class OrchestratorLogger:
    """
    Sistema de logging centralizado para o orquestrador EMBRAPII.
    Consolida logs de múltiplos módulos em um único arquivo JSON.
    """

    def __init__(self, log_dir="logs"):
        """
        Inicializa o logger do orquestrador.

        Args:
            log_dir: Diretório onde os logs serão armazenados
        """
        self.log_dir = log_dir
        self.execution_date = datetime.now().strftime("%Y%m%d")
        self.log_file = os.path.join(
            log_dir, f"orchestrator_{self.execution_date}.json"
        )

        # Criar diretório de logs se não existir
        os.makedirs(log_dir, exist_ok=True)

        # Verificar se já existe um log para hoje
        if os.path.exists(self.log_file):
            # Carregar o log existente
            with open(self.log_file, "r", encoding="utf-8") as f:
                self.log_data = json.load(f)
        else:
            # Inicializar novo log
            self.log_data = {"executions": []}

        # Inicializar nova execução
        self.current_execution = {
            "execution_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "modules": [],
        }

        # Adicionar a execução atual ao log
        self.log_data["executions"].append(self.current_execution)
        self._save_log()

    def start_module(self, module_name):
        """
        Registra o início da execução de um módulo.

        Args:
            module_name: Nome do módulo que está sendo executado

        Returns:
            Índice do módulo no log para referência futura
        """
        module_data = {
            "name": module_name,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "steps": [],
        }

        self.current_execution["modules"].append(module_data)
        self._save_log()
        return len(self.current_execution["modules"]) - 1

    def end_module(self, module_idx, status="success", error=None):
        """
        Registra o fim da execução de um módulo.

        Args:
            module_idx: Índice do módulo no log
            status: Status final do módulo ('success' ou 'error')
            error: Informações de erro, se houver
        """
        module_data = self.current_execution["modules"][module_idx]
        module_data["end_time"] = datetime.now().isoformat()
        module_data["status"] = status

        if error:
            module_data["error"] = {
                "message": str(error),
                "traceback": traceback.format_exc(),
            }

        # Calcular duração
        start_time = datetime.fromisoformat(module_data["start_time"])
        end_time = datetime.fromisoformat(module_data["end_time"])
        module_data["duration_seconds"] = (end_time - start_time).total_seconds()

        self._save_log()

    def add_step(
        self, module_idx, step_name, status="success", details=None, error=None
    ):
        """
        Adiciona um passo à execução de um módulo.

        Args:
            module_idx: Índice do módulo no log
            step_name: Nome do passo
            status: Status do passo ('success' ou 'error')
            details: Detalhes adicionais sobre o passo
            error: Informações de erro, se houver
        """
        step_data = {
            "name": step_name,
            "time": datetime.now().isoformat(),
            "status": status,
        }

        if details:
            step_data["details"] = details

        if error:
            step_data["error"] = {
                "message": str(error),
                "traceback": traceback.format_exc(),
            }

        self.current_execution["modules"][module_idx]["steps"].append(step_data)
        self._save_log()

    def end_execution(self, status="success", message=None):
        """
        Finaliza o log da execução atual.

        Args:
            status: Status final da execução ('success' ou 'error')
            message: Mensagem adicional sobre a execução
        """
        self.current_execution["end_time"] = datetime.now().isoformat()
        self.current_execution["status"] = status

        if message:
            self.current_execution["message"] = message

        # Calcular duração total
        start_time = datetime.fromisoformat(self.current_execution["start_time"])
        end_time = datetime.fromisoformat(self.current_execution["end_time"])
        self.current_execution["total_duration_seconds"] = (
            end_time - start_time
        ).total_seconds()

        self._save_log()
        return self.current_execution

    def _save_log(self):
        """Salva o log atual no arquivo JSON"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_instance(log_dir="logs"):
        """
        Método de fábrica para obter uma instância do logger.
        Útil para compartilhar a mesma instância entre diferentes módulos.

        Args:
            log_dir: Diretório onde os logs serão armazenados

        Returns:
            Instância do OrchestratorLogger
        """
        if not hasattr(OrchestratorLogger, "_instance"):
            OrchestratorLogger._instance = OrchestratorLogger(log_dir)
        return OrchestratorLogger._instance
