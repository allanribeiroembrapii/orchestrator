import json
import os
import time
from datetime import datetime
import traceback


class JsonLogger:
    """Sistema de logging que registra execuções em formato JSON."""

    def __init__(self, log_dir="logs", script_name="unknown"):
        self.log_dir = log_dir
        self.script_name = script_name
        self.execution_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.log_file = os.path.join(log_dir, f"{script_name}_{self.execution_id}.json")

        # Criar diretório de logs se não existir
        os.makedirs(log_dir, exist_ok=True)

        # Inicializar o log
        self.log_data = {
            "script": script_name,
            "execution_id": self.execution_id,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "steps": [],
        }

        # Salvar log inicial
        self._save_log()

    def start_step(self, step_name):
        """Registra o início de um passo de execução"""
        step_data = {
            "name": step_name,
            "start_time": datetime.now().isoformat(),
            "status": "running",
        }
        self.log_data["steps"].append(step_data)
        self._save_log()
        return len(self.log_data["steps"]) - 1  # Retorna o índice do passo no log

    def end_step(self, step_idx, status="success", details=None, error=None):
        """Registra o fim de um passo de execução"""
        step_data = self.log_data["steps"][step_idx]
        step_data["end_time"] = datetime.now().isoformat()
        step_data["status"] = status

        if details:
            step_data["details"] = details

        if error:
            step_data["error"] = {
                "message": str(error),
                "traceback": traceback.format_exc(),
            }

        # Calcular duração
        start_time = datetime.fromisoformat(step_data["start_time"])
        end_time = datetime.fromisoformat(step_data["end_time"])
        duration = (end_time - start_time).total_seconds()
        step_data["duration_seconds"] = duration

        self._save_log()

    def end_execution(self, status="success", message=None):
        """Finaliza o log de execução"""
        self.log_data["end_time"] = datetime.now().isoformat()
        self.log_data["status"] = status

        if message:
            self.log_data["message"] = message

        # Calcular duração total
        start_time = datetime.fromisoformat(self.log_data["start_time"])
        end_time = datetime.fromisoformat(self.log_data["end_time"])
        self.log_data["total_duration_seconds"] = (
            end_time - start_time
        ).total_seconds()

        self._save_log()
        return self.log_data

    def _save_log(self):
        """Salva o log atual no arquivo JSON"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)
