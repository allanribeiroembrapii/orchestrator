import requests
from mover.dados_para_mensagem import projetos_acima_5mi
from dotenv import load_dotenv
import os
import inspect
from datetime import datetime
import win32com.client as win32

# Carregar as variáveis de ambiente
load_dotenv()
ROOT = os.getenv('ROOT')
PLANILHAS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'planilhas'))
ANTERIOR = os.path.abspath(os.path.join(ROOT, 'atrasos', 'anterior'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

data = datetime.now().strftime('%d/%m/%Y')


def mensagem_mover(destinatarios):
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
            return None, None
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
            


        # Enviar e-mail com as mesmas informações
        if not novos_acima_5mi.empty:
            # Corpo do e-mail (HTML)
            html = f"""
            <html>
            <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: auto;
                    padding: 20px;
                }}
                .projeto {{
                    border-top: 1px solid #ccc;
                    padding-top: 15px;
                    margin-top: 15px;
                }}
                .titulo {{
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .subtitulo {{
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .botao {{
                    display: inline-block;
                    background-color: #0078D4;
                    color: white;
                    padding: 12px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 30px auto;
                    text-align: center;
                }}
            </style>
            </head>
            <body>
            <div class="container">
                <div style="text-align: center;">
                <img src="https://i.imgur.com/Bw4dGHM.png" alt="Banner Mover" style="width: 100%;">
                </div>

                <p><b>Data:</b> {data}</p>

                <!-- Título dinâmico -->
                {"<div class='titulo'>⚠️ Um novo projeto MOVER</div><div class='subtitulo'>acima de R$ 5 milhões</div>" if len(novos_acima_5mi) == 1 else f"<div class='titulo'>⚠️ {len(novos_acima_5mi)} novos projetos MOVER</div><div class='subtitulo'>acima de R$ 5 milhões</div>"}
            """

            # Adiciona cada projeto ao HTML
            for _, row in novos_acima_5mi.iterrows():
                html += f"""
                <div class="projeto">
                <h4>📌 Projeto: {row['titulo']}</h4>
                <ul>
                    <li><b>Código do Projeto:</b> {row['codigo_projeto']}</li>
                    <li><b>Código da Negociação:</b> {row['codigo_negociacao']}</li>
                    <li><b>Unidade Embrapii:</b> {row['unidade_embrapii']}</li>
                    <li><b>Data do Contrato:</b> {row['data_contrato'].strftime('%d/%m/%Y')}</li>
                    <li><b>Modalidade de financiamento:</b> {row['modalidade_financiamento']}</li>
                    <li><b>Valor Total:</b> {formatar_valor(row['valor_total'])}</li>
                </ul>
                </div>
                """


            # Botão e imagem final
            html += """
                <div style="text-align: center;">
                <a href="https://app.powerbi.com/Redirect?action=OpenReport&appId=a545d987-6ef5-4df2-816d-df6e337bc2e8&reportObjectId=7c4d7ea7-9276-47c8-b24c-90d0399df3d5&ctid=8fb344f4-0740-4e5a-b2c1-53858c0c732f&reportPage=a191642d4504d5e26ffb&pbi_source=appShareLink&portalSessionId=8738083d-ca1b-446b-98a5-a06b7a02c39c"
                    class="botao"
                    style="display: inline-block; background-color: #006ba7; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">🔗 Acessar Painel MOVER</a>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                <img src="https://i.imgur.com/M2cS1iy.png" alt="Rodapé" style="width: 100%;">
                </div>
            </div>
            </body>
            </html>
            """

            # Definição do título com base na quantidade
            if len(novos_acima_5mi) > 1:
                titulo = f"<h2 style='text-align:center;'>⚠️ <b>{len(novos_acima_5mi)} novos projetos MOVER</b><br>acima de R$ 5 milhões</h2>"
            else:
                titulo = "<h2 style='text-align:center;'>⚠️ <b>Um novo projeto MOVER</b><br>acima de R$ 5 milhões</h2>"


            outlook = win32.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = ";".join(destinatarios)
            mail.Subject = "⚠️ Alerta de Novos Projetos MOVER acima de R$ 5 milhões"
            mail.HTMLBody = html
            mail.Send()


        print("🟢 " + inspect.currentframe().f_code.co_name)

        return payload, html
    
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


def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
