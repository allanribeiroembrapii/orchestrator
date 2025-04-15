import requests
from mover.dados_para_mensagem import projetos_acima_5mi
from dotenv import load_dotenv
import os
import inspect
from datetime import datetime

# Carregar as variáveis de ambiente
load_dotenv()
ROOT = os.getenv('ROOT')
PLANILHAS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'planilhas'))
ANTERIOR = os.path.abspath(os.path.join(ROOT, 'atrasos', 'anterior'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

data = datetime.now().strftime('%d/%m/%Y')


def mensagem_teams_mover():
    """
    Função para gerar a mensagem a ser enviada para o Teams, com imagens, textos e tabelas

    retorna o payload da mensagem
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        novos_acima_5mi = projetos_acima_5mi()

        # Criar lista de colunas formatadas para o Teams
        if novos_acima_5mi.empty:
            print("🟡 Não há novos projetos acima de R$ 5 milhões.")
            return None
        else:
            cards = [
                {
                    "type": "Container",
                    "style": "emphasis",
                    "size": "Stretch",
                    "wrap": True,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"📌 Projeto: {row['titulo']}",
                            "weight": "Bolder",
                            "color": "Accent",
                            "size": "Medium",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Código do Projeto:", "value": str(row["codigo_projeto"])},
                                {"title": "Código da Negociação:", "value": str(row["codigo_negociacao"])},
                                {"title": "Unidade Embrapii:", "value": str(row["unidade_embrapii"])},
                                {"title": "Data do Contrato:", "value": row["data_contrato"].strftime("%d/%m/%Y")},
                                {"title": "Modalidade de financiamento:", "value": str(row["modalidade_financiamento"])},
                                {"title": "Valor Total:", "value": f"R$ {row['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")},
                            ]
                        }
                    ],
                    "style": "emphasis",
                    "separator": True,
                    "spacing": "Large",
                }
                for _, row in novos_acima_5mi.iterrows()
            ]

            if len(novos_acima_5mi['codigo_projeto']) > 1:
                titulo = [
                    {
                        "type": "TextBlock",
                        "text": f"⚠️ **{len(novos_acima_5mi['codigo_projeto'])} novos projetos MOVER**",
                        "weight": "Bolder",
                        "size": "Large",
                        "wrap": True,
                        "horizontalAlignment": "Center"
                    },
                    {
                        "type": "TextBlock",
                        "text": "**acima de R$ 5 milhões**",
                        "weight": "Bolder",
                        "size": "Large",
                        "wrap": True,
                        "horizontalAlignment": "Center"
                    }
                ]
            elif len(novos_acima_5mi['codigo_projeto']) == 1:
                titulo = [
                    {
                        "type": "TextBlock",
                        "text": f"⚠️ **Um novo projeto MOVER**",
                        "weight": "Bolder",
                        "size": "Large",
                        "wrap": True,
                        "horizontalAlignment": "Center"
                    },
                    {
                        "type": "TextBlock",
                        "text": "**acima de R$ 5 milhões**",
                        "weight": "Bolder",
                        "size": "Large",
                        "wrap": True,
                        "horizontalAlignment": "Center"
                    }
                ]


            payload = {
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "Image",
                                "url": "https://i.imgur.com/Bw4dGHM.png",
                                "size": "Stretch",
                                "altText": "Banner Mover",
                                "horizontalAlignment": "Center"
                            },

                            {
                                "type": "TextBlock",
                                "text": f"Data: {data}",
                                "weight": "Bolder"
                            },

                            *titulo,
                            *cards,

                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": "🔗 Painel MOVER",
                                        "url": "https://app.powerbi.com/Redirect?action=OpenReport&appId=a545d987-6ef5-4df2-816d-df6e337bc2e8&reportObjectId=7c4d7ea7-9276-47c8-b24c-90d0399df3d5&ctid=8fb344f4-0740-4e5a-b2c1-53858c0c732f&reportPage=a191642d4504d5e26ffb&pbi_source=appShareLink&portalSessionId=8738083d-ca1b-446b-98a5-a06b7a02c39c"
                                    }
                                ]
                            },

                            {
                                "type": "Image",
                                "url": "https://i.imgur.com/M2cS1iy.png",
                                "size": "Stretch",
                                "altText": "Banner Mover",
                                "horizontalAlignment": "Center"
                            },
                        ]
                    }
                }
            ]
        }

        print("🟢 " + inspect.currentframe().f_code.co_name)

        return payload
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def enviar_mensagem_teams_mover(payload):
    """
    Função para enviar a mensagem para o Teams
        payload: dict - payload da mensagem
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        # Enviar para o Teams
        response = requests.post(WEBHOOK_URL, json=payload)

        # Verificar resposta
        tipo_resposta = "✅ Mensagem enviada com sucesso!" if response.status_code in [200, 202] else f"❌ Erro ao enviar: {response.text}"
        print(tipo_resposta)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")