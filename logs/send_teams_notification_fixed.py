import os
import sys
import subprocess
import argparse
from datetime import datetime

# Adicionar o diretório raiz ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)  # Diretório raiz do projeto

# Configurar caminhos usando os.path para evitar problemas de escape
pipeline_path = os.path.join(root_dir, "core", "pipeline_embrapii_srinfo")
sys.path.append(pipeline_path)

# Importar a função comparar_excel usando importação relativa
sys.path.append(root_dir)
from core.pipeline_embrapii_srinfo.scripts_public.comparar_excel import comparar_excel

# Obter o último log
log_file = os.path.join(root_dir, "logs", "exec_20250415.log")
try:
    with open(log_file, "r") as f:
        last_log = f.read()
    print(f"Último log carregado de {log_file}")
except Exception as e:
    last_log = f"Erro ao ler o log: {str(e)}"
    print(last_log)


def main(
    status="success", error_msg=None, start_time=None, end_time=None, duration=None
):
    print("Iniciando envio de notificação para o Teams...")
    print(f"Diretório raiz: {root_dir}")
    print(f"Diretório do pipeline: {pipeline_path}")
    print(f"Status: {status}")

    try:
        # Construir o comando para enviar a notificação
        notification_script = os.path.join(
            root_dir, "logs", "send_teams_notification.py"
        )

        # Se não foram fornecidos horários, usar a data/hora atual
        if not start_time or not end_time:
            now = datetime.now()
            start_time = start_time or now.strftime("%d/%m/%Y %H:%M:%S")
            end_time = end_time or now.strftime("%d/%m/%Y %H:%M:%S")

        if status == "success":
            # Executar comparar_excel para obter estatísticas
            print("Executando comparar_excel()...")
            result = comparar_excel()
            novos_projetos, novas_empresas, projetos_sem_classificacao = result

            print(f"Estatísticas obtidas: {result}")
            print(f"- Novos projetos: {novos_projetos}")
            print(f"- Novas empresas: {novas_empresas}")
            print(f"- Projetos sem classificação: {projetos_sem_classificacao}")

            # Executar o script de notificação com os argumentos corretos para sucesso
            cmd = [
                sys.executable,
                notification_script,
                "--status",
                "success",
                "--start",
                start_time,
                "--end",
                end_time,
                "--duration",
                duration or "00:00:00",
                "--new-projects",
                str(novos_projetos),
                "--new-companies",
                str(novas_empresas),
                "--unclassified",
                str(projetos_sem_classificacao),
            ]
        else:
            # Executar o script de notificação com os argumentos corretos para erro
            cmd = [
                sys.executable,
                notification_script,
                "--status",
                "error",
                "--start",
                start_time,
                "--end",
                end_time,
                "--duration",
                duration or "00:00:00",
                "--error-msg",
                error_msg
                or "Erro na execução do pipeline. Verifique os logs para mais detalhes.",
            ]

        print(f"Executando comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("Notificação enviada com sucesso!")
            return True
        else:
            print(f"Erro ao enviar notificação: {result.stderr}")
            return False

    except Exception as e:
        print(f"Erro ao executar o script: {str(e)}")

        # Em caso de erro, enviar notificação de erro
        try:
            notification_script = os.path.join(
                root_dir, "logs", "send_teams_notification.py"
            )
            cmd = [
                sys.executable,
                notification_script,
                "--status",
                "error",
                "--error-msg",
                str(e),
            ]

            subprocess.run(cmd)
            print("Notificação de erro enviada.")
        except Exception as e2:
            print(f"Erro ao enviar notificação de erro: {str(e2)}")

        return False


if __name__ == "__main__":
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(
        description="Enviar notificação para o Microsoft Teams"
    )
    parser.add_argument(
        "--error", action="store_true", help="Indica que ocorreu um erro"
    )
    parser.add_argument("--error-msg", help="Mensagem de erro")
    parser.add_argument(
        "--start", help="Data/hora de início no formato DD/MM/YYYY HH:MM:SS"
    )
    parser.add_argument(
        "--end", help="Data/hora de término no formato DD/MM/YYYY HH:MM:SS"
    )
    parser.add_argument("--duration", help="Duração da execução no formato HH:MM:SS")

    args = parser.parse_args()

    if args.error:
        main("error", args.error_msg, args.start, args.end, args.duration)
    else:
        main("success", None, args.start, args.end, args.duration)
