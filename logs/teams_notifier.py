import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def enviar_notificacao_teams(stats):
    """
    Envia uma notificação para o Microsoft Teams com informações sobre a execução do pipeline.

    Args:
        stats (dict): Dicionário contendo estatísticas da execução do pipeline
            - inicio: Data/hora de início
            - fim: Data/hora de término
            - duracao: Duração total da execução
            - novos_projetos: Número de novos projetos
            - novas_empresas: Número de novas empresas
            - projetos_sem_classificacao: Número de projetos sem classificação
            - status: Status da execução ('success' ou 'error')
            - error_msg: Mensagem de erro (opcional, apenas se status='error')

    Returns:
        bool: True se a notificação foi enviada com sucesso, False caso contrário
    """
    # Obter URL do webhook do arquivo .env
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    if not WEBHOOK_URL:
        print("URL do webhook não encontrada no arquivo .env")
        return False

    # Determinar status e cor com base no resultado da execução
    if stats.get("status") == "success":
        status_text = "✅ Sucesso"
        status_color = "Good"
        title = "🚀 Pipeline EMBRAPII SRInfo Concluído com Sucesso!"
    else:
        status_text = "❌ Erro"
        status_color = "Attention"
        title = "⚠️ Pipeline EMBRAPII SRInfo Interrompido com Erro"

    # Construir o Adaptive Card
    message = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": title,
                            "size": "ExtraLarge",
                            "weight": "Bolder",
                            "color": status_color,
                            "wrap": True,
                            "horizontalAlignment": "Center",
                        },
                        {
                            "type": "Image",
                            "url": "https://placehold.co/600x200/3F51B5/FFFFFF.png?text=EMBRAPII+Pipeline+SRInfo",
                            "size": "Stretch",
                            "altText": "Banner EMBRAPII Pipeline",
                            "horizontalAlignment": "Center",
                        },
                        {
                            "type": "TextBlock",
                            "text": f"**Execução finalizada em {stats['fim']}**",
                            "size": "Medium",
                            "weight": "Bolder",
                            "color": "Accent",
                            "wrap": True,
                            "spacing": "Medium",
                        },
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "🔧 Detalhes da Execução:",
                                            "weight": "Bolder",
                                            "size": "Medium",
                                        },
                                        {
                                            "type": "FactSet",
                                            "facts": [
                                                {
                                                    "title": "Status:",
                                                    "value": status_text,
                                                },
                                                {
                                                    "title": "Início:",
                                                    "value": stats["inicio"],
                                                },
                                                {
                                                    "title": "Fim:",
                                                    "value": stats["fim"],
                                                },
                                                {
                                                    "title": "Duração:",
                                                    "value": stats["duracao"],
                                                },
                                            ],
                                        },
                                    ],
                                }
                            ],
                        },
                    ],
                },
            }
        ],
    }

    # Adicionar estatísticas de projetos e empresas se a execução foi bem-sucedida
    if stats.get("status") == "success":
        # Adicionar estatísticas de projetos e empresas
        stats_block = {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "📊 Estatísticas:",
                            "weight": "Bolder",
                            "size": "Medium",
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "title": "Novos Projetos:",
                                    "value": str(stats["novos_projetos"]),
                                },
                                {
                                    "title": "Novas Empresas:",
                                    "value": str(stats["novas_empresas"]),
                                },
                                {
                                    "title": "Projetos sem Classificação:",
                                    "value": str(stats["projetos_sem_classificacao"]),
                                },
                            ],
                        },
                    ],
                }
            ],
        }
        message["attachments"][0]["content"]["body"].append(stats_block)

        # Adicionar links para documentação e relatórios
        actions_block = {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "🔗 Acessar Classificação de Projetos",
                    "url": "https://embrapii.sharepoint.com/:x:/r/sites/GEPES/Documentos%20Compartilhados/DWPII/srinfo/classificacao_projeto.xlsx?d=wb7a7a439310f4d52a37728b9f1833961&csf=1&web=1&e=qXpfgA",
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "🌐 Acessar Relatórios",
                    "url": "https://embrapii.sharepoint.com/:f:/r/sites/GEPES/Documentos%20Compartilhados/Reports?csf=1&web=1&e=aVdkyL",
                },
            ],
            "horizontalAlignment": "Center",
        }
        message["attachments"][0]["content"]["body"].append(actions_block)
    else:
        # Adicionar mensagem de erro se a execução falhou
        error_block = {
            "type": "TextBlock",
            "text": f"**Erro:** {stats.get('error_msg', 'Erro desconhecido')}",
            "color": "Attention",
            "wrap": True,
            "spacing": "Medium",
        }
        message["attachments"][0]["content"]["body"].append(error_block)

    # Enviar a requisição
    try:
        response = requests.post(
            url=WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(message),
        )

        # Verificar resposta
        # Códigos 200 (OK) e 202 (Accepted) são considerados sucesso
        if response.status_code in [200, 202]:
            print("Notificação enviada para o Microsoft Teams com sucesso!")
            return True
        else:
            print(
                f"Erro ao enviar notificação para o Microsoft Teams: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print(f"Erro ao enviar notificação para o Microsoft Teams: {str(e)}")
        return False


# Função para uso pelo script batch
def enviar_notificacao_final(
    status="success",
    error_msg=None,
    novos_projetos=0,
    novas_empresas=0,
    projetos_sem_classificacao=0,
):
    """
    Função para ser chamada ao final do pipeline para enviar notificação.

    Args:
        status (str): 'success' ou 'error'
        error_msg (str): Mensagem de erro (opcional)
        novos_projetos (int): Número de novos projetos
        novas_empresas (int): Número de novas empresas
        projetos_sem_classificacao (int): Número de projetos sem classificação

    Returns:
        bool: True se a notificação foi enviada com sucesso, False caso contrário
    """
    # Calcular tempo de execução total
    agora = datetime.now()
    inicio_str = agora.strftime(
        "%d/%m/%Y %H:%M:%S"
    )  # Exemplo simplificado, idealmente vem de um log
    fim_str = agora.strftime("%d/%m/%Y %H:%M:%S")

    # Preparar estatísticas
    stats = {
        "inicio": inicio_str,
        "fim": fim_str,
        "duracao": "00:05:00",  # Exemplo estático, idealmente calculado
        "novos_projetos": novos_projetos,
        "novas_empresas": novas_empresas,
        "projetos_sem_classificacao": projetos_sem_classificacao,
        "status": status,
    }

    if error_msg:
        stats["error_msg"] = error_msg

    # Enviar notificação
    return enviar_notificacao_teams(stats)


if __name__ == "__main__":
    # Teste da função com parâmetros de exemplo
    enviar_notificacao_final(
        status="success",
        novos_projetos=5,
        novas_empresas=3,
        projetos_sem_classificacao=2,
    )
