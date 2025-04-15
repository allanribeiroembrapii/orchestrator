import os
import sys
import argparse
from datetime import datetime

# Adicionar o diretório raiz ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Importar a função para enviar notificação
from logs.teams_notifier import enviar_notificacao_teams


def main():
    """
    Script para enviar notificação ao Microsoft Teams a partir de linha de comando.
    Usado principalmente para ser chamado a partir de scripts batch.

    Exemplo de uso:
    python send_teams_notification.py --status success --start "10/04/2025 08:00:00" --end "10/04/2025 08:30:00" --duration "00:30:00" --new-projects 5 --new-companies 3 --unclassified 2
    """
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(
        description="Enviar notificação para o Microsoft Teams"
    )

    parser.add_argument(
        "--status",
        choices=["success", "error"],
        default="success",
        help="Status da execução: success ou error",
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Data/hora de início no formato DD/MM/YYYY HH:MM:SS",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="Data/hora de término no formato DD/MM/YYYY HH:MM:SS",
    )
    parser.add_argument(
        "--duration", default=None, help="Duração da execução no formato HH:MM:SS"
    )
    parser.add_argument(
        "--new-projects", type=int, default=0, help="Número de novos projetos"
    )
    parser.add_argument(
        "--new-companies", type=int, default=0, help="Número de novas empresas"
    )
    parser.add_argument(
        "--unclassified",
        type=int,
        default=0,
        help="Número de projetos sem classificação",
    )
    parser.add_argument(
        "--error-msg", default=None, help='Mensagem de erro, caso o status seja "error"'
    )

    # Parsear os argumentos
    args = parser.parse_args()

    # Se não foram fornecidos horários, usar a data/hora atual
    now = datetime.now()
    start_time = args.start or now.strftime("%d/%m/%Y %H:%M:%S")
    end_time = args.end or now.strftime("%d/%m/%Y %H:%M:%S")

    # Preparar as estatísticas
    stats = {
        "status": args.status,
        "inicio": start_time,
        "fim": end_time,
        "duracao": args.duration or "00:00:00",
        "novos_projetos": args.new_projects,
        "novas_empresas": args.new_companies,
        "projetos_sem_classificacao": args.unclassified,
    }

    # Adicionar mensagem de erro se o status for 'error'
    if args.status == "error" and args.error_msg:
        stats["error_msg"] = args.error_msg

    # Enviar a notificação
    success = enviar_notificacao_teams(stats)

    # Definir código de saída
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
