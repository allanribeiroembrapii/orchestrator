"""
Script para configurar o ambiente Prefect completo para o projeto EMBRAPII.
Este script cria os work pools, deployments e configurações necessárias.
"""

import subprocess
import sys
import os


def setup_prefect_environment():
    """Configura o ambiente Prefect completo conforme documentação oficial."""
    print("Configurando ambiente Prefect para o projeto EMBRAPII...")

    # Criar work pool para processamento
    try:
        result = subprocess.run(
            ["prefect", "work-pool", "create", "embrapii-pool", "--type", "process"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Work pool 'embrapii-pool' criado com sucesso!")
    except subprocess.CalledProcessError as e:
        if "already exists" in e.stderr:
            print("⚠️ Work pool 'embrapii-pool' já existe")
        else:
            print(f"❌ Erro ao criar work pool: {e.stderr}")

    # Aplicar deployments do arquivo prefect.yaml
    try:
        result = subprocess.run(
            ["prefect", "deploy", "--all", "--apply"], capture_output=True, text=True, check=True
        )
        print("✅ Deployments criados/atualizados com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar deployments:\n{e.stderr}")

    print("\n🚀 Ambiente Prefect configurado com sucesso!")
    print("Para iniciar o worker, execute: prefect worker start -p embrapii-pool")


if __name__ == "__main__":
    # Verificar se o servidor Prefect está rodando
    try:
        result = subprocess.run(
            ["prefect", "config", "view"], capture_output=True, text=True, check=True
        )

        # Executar a configuração do ambiente
        setup_prefect_environment()

    except subprocess.CalledProcessError:
        print("❌ O servidor Prefect não está rodando.")
        print("Inicie o servidor com: prefect server start")
        sys.exit(1)
