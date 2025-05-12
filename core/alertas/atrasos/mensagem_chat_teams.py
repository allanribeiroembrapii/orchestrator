import requests
from atrasos.dados_para_mensagem import dados_projetos, dados_macroentregas
from datetime import date
from dotenv import load_dotenv
import os
import inspect
import pandas as pd
import win32com.client as win32

# Carregar as variáveis de ambiente
load_dotenv()
ROOT = os.getenv('ROOT')
PLANILHAS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'planilhas'))
ANTERIOR = os.path.abspath(os.path.join(ROOT, 'atrasos', 'anterior'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def truncate_text(text, max_length=15):
    """
    Função para truncar o texto e adicionar '...' se o texto for maior que o limite
        text: str - texto a ser truncado
        max_length: int - limite de caracteres
    """
    try:

        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    except Exception as e:
        print(f"🔴 Erro: {e}")
    

def mensagem_atrasos(destinatarios):
    """
    Função para gerar a mensagem a ser enviada para o Teams, com imagens, textos e tabelas

    retorna o payload da mensagem
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        novos, proj_concluidos, novos_concluidos, novos2, proj_atrasados, novos_atrasados, total_projetos, total_projetos_anterior, novos_projetos = dados_projetos()
        novas_macro, macro_atrasadas, novas_macro_atrasadas, macro_sem_termo_60, macro_sem_termo_60_novas, total_macroentregas, total_macroentregas_anterior, novas_macroentregas = dados_macroentregas()

        #### TABELA GERAL ####
        tabela_geral = {
            'Indicador': ['Projetos', 'Projetos Concluídos', 'Projetos Atrasados', 'Macroentregas (ME)', 'ME Atrasadas', 'ME sem Termo (+60)'],
            'Total': [total_projetos, proj_concluidos, proj_atrasados, total_macroentregas, macro_atrasadas, len(macro_sem_termo_60)],
            'Última semana': [novos_projetos, novos_concluidos, novos_atrasados, novas_macroentregas, novas_macro_atrasadas, len(macro_sem_termo_60_novas)]
        }


        # Criar lista de colunas formatadas para o Teams
        column_set_tabela = {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {"type": "TextBlock", "text": "Indicador", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True},
                        *[
                            {"type": "TextBlock", "text": indicador, "wrap": True}
                            for indicador in tabela_geral["Indicador"]
                        ]
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {"type": "TextBlock", "text": "Total", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Center"},
                        *[
                            {"type": "TextBlock", "text": str(valor), "wrap": True, "horizontalAlignment": "Center"}
                            for valor in tabela_geral["Total"]
                        ]
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {"type": "TextBlock", "text": "Nesta semana", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Center"},
                        *[
                            {"type": "TextBlock", "text": str(valor), "wrap": True, "horizontalAlignment": "Center"}
                            for valor in tabela_geral["Última semana"]
                        ]
                    ]
                }
            ]
        }



        # Criar lista de colunas formatadas para o Teams
        if macro_sem_termo_60_novas.empty:
            column_set = {
                "type": "TextBlock",
                "text": "Nenhuma",
                "weight": "Bolder",
                "size": "Medium",
                "color": "attention",
                "wrap": True,
                "horizontalAlignment": "Left"
            }
        else:
            column_set = {
                "type": "ColumnSet",
                "columns": [
                    # {
                    #     "type": "Column",
                    #     "width": "stretch",
                    #     "items": [
                    #         {"type": "TextBlock", "text": "UE", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                    #         # Adicionando os TextBlocks para cada código de projeto
                    #         *[
                    #             {"type": "TextBlock", "text": truncate_text(str(row["unidade_embrapii"]), max_length=10), "wrap": True, "horizontalAlignment": "Left"}
                    #             for _, row in macro_sem_termo_60_novas.iterrows()
                    #         ]
                    #     ]
                    # },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Código", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["codigo_projeto"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in macro_sem_termo_60_novas.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "ME", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Center"},
                            # Adicionando os TextBlocks para cada número de macroentrega
                            *[
                                {"type": "TextBlock", "text": str(row["num_macroentrega"]), "wrap": True, "horizontalAlignment": "Center"}
                                for _, row in macro_sem_termo_60_novas.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Prazo", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Center"},
                            # Adicionando os TextBlocks para cada número de macroentrega
                            *[
                                {"type": "TextBlock", "text": str(row["prazo"]), "wrap": True, "horizontalAlignment": "Center"}
                                for _, row in macro_sem_termo_60_novas.iterrows()
                            ]
                        ]
                    }
                ]
            }


        # Lista projetos concluidos
        if novos.empty:
            column_set_proj_concluidos = {
                "type": "TextBlock",
                "text": "Nenhum",
                "weight": "Bolder",
                "size": "Medium",
                "color": "attention",
                "wrap": True,
                "horizontalAlignment": "Left"
            }
        else:
            column_set_proj_concluidos = {
                "type": "ColumnSet",
                "columns": [
                    # {
                    #     "type": "Column",
                    #     "width": "stretch",
                    #     "items": [
                    #         {"type": "TextBlock", "text": "UE", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                    #         # Adicionando os TextBlocks para cada código de projeto
                    #         *[
                    #             {"type": "TextBlock", "text": truncate_text(str(row["unidade_embrapii"]), max_length=10), "wrap": True, "horizontalAlignment": "Left"}
                    #             for _, row in novos.iterrows()
                    #         ]
                    #     ]
                    # },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Código", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["codigo_projeto"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novos.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Modalidade", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["modalidade"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novos.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Duração", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": f"{row["duracao_dias"]} dias", "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novos.iterrows()
                            ]
                        ]
                    }
                ]
            }


        # Lista projetos atrasados
        if novos2.empty:
            column_set_proj_atrasados = {
                "type": "TextBlock",
                "text": "Nenhum",
                "weight": "Bolder",
                "size": "Medium",
                "color": "attention",
                "wrap": True,
                "horizontalAlignment": "Left"
            }
        else:
            column_set_proj_atrasados = {
                "type": "ColumnSet",
                "columns": [
                    # {
                    #     "type": "Column",
                    #     "width": "stretch",
                    #     "items": [
                    #         {"type": "TextBlock", "text": "UE", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                    #         # Adicionando os TextBlocks para cada código de projeto
                    #         *[
                    #             {"type": "TextBlock", "text": truncate_text(str(row["unidade_embrapii"]), max_length=10), "wrap": True, "horizontalAlignment": "Left"}
                    #             for _, row in novos2.iterrows()
                    #         ]
                    #     ]
                    # },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Código", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["codigo_projeto"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novos2.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Data de término", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": pd.to_datetime(row["data_termino"]).strftime("%d/%m/%Y"), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novos2.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Prazo", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["prazo"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novos2.iterrows()
                            ]
                        ]
                    }
                ]
            }


        # Lista macroentregas atrasadas
        if novas_macro.empty:
            column_set_macro_atrasadas = {
                "type": "TextBlock",
                "text": "Nenhuma",
                "weight": "Bolder",
                "size": "Medium",
                "color": "attention",
                "wrap": True,
                "horizontalAlignment": "Left"
            }
        else:
            column_set_macro_atrasadas = {
                "type": "ColumnSet",
                "columns": [
                    # {
                    #     "type": "Column",
                    #     "width": "stretch",
                    #     "items": [
                    #         {"type": "TextBlock", "text": "UE", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                    #         # Adicionando os TextBlocks para cada código de projeto
                    #         *[
                    #             {"type": "TextBlock", "text": truncate_text(str(row["unidade_embrapii"]), max_length=10), "wrap": True, "horizontalAlignment": "Left"}
                    #             for _, row in novas_macro.iterrows()
                    #         ]
                    #     ]
                    # },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Código", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["codigo_projeto"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novas_macro.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "ME", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["num_macroentrega"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novas_macro.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Término plan.", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": pd.to_datetime(row["data_termino_planejado"]).strftime("%d/%m/%Y"), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novas_macro.iterrows()
                            ]
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [
                            {"type": "TextBlock", "text": "Prazo", "weight": "Bolder", "size": "Medium", "color": "accent", "wrap": True, "horizontalAlignment": "Left"},
                            # Adicionando os TextBlocks para cada código de projeto
                            *[
                                {"type": "TextBlock", "text": str(row["prazo"]), "wrap": True, "horizontalAlignment": "Left"}
                                for _, row in novas_macro.iterrows()
                            ]
                        ]
                    }
                ]
            }

        data = date.today().strftime("%d/%m/%Y")


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
                                "url": "https://i.imgur.com/aCPi0n8.png",
                                "size": "Stretch",
                                "altText": "Banner Monitoramento de Projetos",
                                "horizontalAlignment": "Center"
                            },

                            {
                                "type": "TextBlock",
                                "text": f"Data: {data}",
                                "weight": "Bolder"
                            },

                            {
                                "type": "Container",
                                "style": "emphasis",
                                "wrap": True,
                                "items": [
                                    { "type": "TextBlock", "text": "📌 **Números Gerais**", "size": "Large", "weight": "Bolder" },
                                    column_set_tabela
                                ]
                            },

                            {
                                "type": "Container",
                                "style": "emphasis",
                                "wrap": True,
                                "items": [
                                    { "type": "TextBlock", "text": "📌 **Projetos Concluídos nesta semana**", "size": "Large", "weight": "Bolder" },
                                    column_set_proj_concluidos
                                ]
                            },

                            {
                                "type": "Container",
                                "style": "emphasis",
                                "wrap": True,
                                "items": [
                                    { "type": "TextBlock", "text": "📌 **Projetos Atrasados nesta semana**", "size": "Large", "weight": "Bolder" },
                                    column_set_proj_atrasados
                                ]
                            },

                            {
                                "type": "Container",
                                "style": "emphasis",
                                "wrap": True,
                                "items": [
                                    { "type": "TextBlock", "text": "📌 **Macroentregas Atrasadas nesta semana**", "size": "Large", "weight": "Bolder" },
                                    column_set_macro_atrasadas
                                ]
                            },

                            {
                                "type": "Container",
                                "style": "emphasis",
                                "wrap": True,
                                "items": [
                                    { "type": "TextBlock", "text": "📌 **Macroentregas sem Termo nesta semana**", "size": "Large", "weight": "Bolder" },
                                    { "type": "TextBlock", "text": "(+60 dias)", "size": "Medium" },
                                    column_set
                                ]
                            },

                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": "🔗 Painel de Monitoramento",
                                        "url": "https://app.powerbi.com/Redirect?action=OpenReport&appId=a545d987-6ef5-4df2-816d-df6e337bc2e8&reportObjectId=ee865143-b695-4537-97f6-f74173d6c652&ctid=8fb344f4-0740-4e5a-b2c1-53858c0c732f&reportPage=739ea8bad70e0d06a51a&pbi_source=appShareLink&portalSessionId=7b6e6f68-585d-4a14-9441-fab46f2d0267"
                                    }
                                ]
                            },

                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": "🔗 Contato das Unidades",
                                        "url": "https://app.powerbi.com/groups/me/apps/ccbb1664-f0e2-439f-b607-12a98a3341e2/reports/da2a702a-8877-4eb1-a09a-76904e572776/be085ea1a58ee560d08a?ctid=8fb344f4-0740-4e5a-b2c1-53858c0c732f&experience=power-bi"
                                    }
                                ]
                            },

                            {
                                "type": "Image",
                                "url": "https://i.imgur.com/lhEXiPg.png",
                                "size": "Stretch",
                                "altText": "Banner Monitoramento de Projetos final",
                                "horizontalAlignment": "Center"
                            },
                        ]
                    }
                }
            ]
        }


        # EMAIL
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
                .titulo {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 20px;
                text-align: center;
                }}
                .subtitulo {{
                border-top: 1px solid #ccc;
                font-size: 18px;
                font-weight: bold;
                padding-top: 15px;
                margin-top: 15px;
                color: #0078D4;
                }}
                .tabela {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                }}
                .tabela th, .tabela td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: center;
                }}
                .tabela th {{
                background-color: #f4f4f4;
                }}
                .botao {{
                display: inline-block;
                background-color: #0078D4;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 80px;
                }}
                .imagem-banner {{
                width: 100%;
                height: auto;
                }}
            </style>
            </head>
            <body>
            <div class="container">
                <img src="https://i.imgur.com/aCPi0n8.png" alt="Banner Monitoramento de Projetos" class="imagem-banner">

                <p><strong>Data: </strong>{data}</p>

                <div class="subtitulo">📌 Números Gerais</div>
                <table class="tabela">
                <thead>
                    <tr>
                    <th>Indicador</th>
                    <th>Total</th>
                    <th>Nesta semana</th>
                    </tr>
                </thead>
                <tbody>
                """
        
        for i in range(len(tabela_geral["Indicador"])):
            html += f"""
                <tr>
                    <td>{ tabela_geral["Indicador"][i] }</td>
                    <td>{ tabela_geral["Total"][i] }</td>
                    <td>{ tabela_geral["Última semana"][i] }</td>
                    </tr>
                """

        html += f"""
        </tbody>
                </table>
                    <div class="subtitulo">📌 Projetos Concluídos nesta semana</div>
        """

        if novos.empty:
            html += """
            <p>Nenhum.</p>
            """
        else:
            html += f"""
            <table class="tabela">
            <thead>
                <tr>
                <th>Código</th>
                <th>Modalidade</th>
                <th>Duração</th>
                </tr>
            </thead>
            <tbody>
            """
            for _, row in novos.iterrows():
                html += f"""
                <tr>
                    <td>{row["codigo_projeto"]}</td>
                    <td>{row["modalidade"]}</td>
                    <td>{row["duracao_dias"]} dias</td>
                </tr>
                """

        html += f"""
        </tbody>
                </table>
        <div class="subtitulo">📌 Projetos Atrasados nesta semana</div>
        """

        if novos2.empty:
            html += """
            <p>Nenhum.</p>
            """
        else:
            html += f"""
            <table class="tabela">
            <thead>
                <tr>
                <th>Código</th>
                <th>Data de término</th>
                <th>Prazo</th>
                </tr>
            </thead>
            <tbody>
            """
            for _, row in novos2.iterrows():
                html += f"""
                <tr>
                    <td>{row["codigo_projeto"]}</td>
                    <td>{row["data_termino"]}</td>
                    <td>{row["prazo"]} dias</td>
                </tr>
                """


        html += """
        </tbody>
                </table>
        <div class="subtitulo">📌 Macroentregas Atrasadas nesta semana</div>
        """

        if novas_macro.empty:
            html += """
            <p>Nenhuma.</p>
            """
        else:
            html += f"""
            <table class="tabela">
            <thead>
                <tr>
                <th>Código</th>
                <th>ME</th>
                <th>Data de término planejada</th>
                <th>Prazo</th>
                </tr>
            </thead>
            <tbody>
            """
            for _, row in novas_macro.iterrows():
                html += f"""
                <tr>
                    <td>{row["codigo_projeto"]}</td>
                    <td>{row["num_macroentrega"]}</td>
                    <td>{pd.to_datetime(row["data_termino_planejado"]).strftime("%d/%m/%Y")}</td>
                    <td>{row["prazo"]} dias</td>
                </tr>
                """
        
        html += f"""
        </tbody>
                </table>
        <div class="subtitulo">📌 Macroentregas sem Termo (+60 dias) nesta semana</div>
        """

        if macro_sem_termo_60_novas.empty:
            html += """
            <p>Nenhuma.</p>
            """

        else:
            html += f"""
            <table class="tabela">
            <thead>
                <tr>
                <th>Código</th>
                <th>ME</th>
                <th>Prazo</th>
                </tr>
            </thead>
            <tbody>
            """
            for _, row in macro_sem_termo_60_novas.iterrows():
                html += f"""
                <tr>
                    <td>{row["codigo_projeto"]}</td>
                    <td>{row["num_macroentrega"]}</td>
                    <td>{row["prazo"]} dias</td>
                </tr>
                """
        html += """
        </tbody>
                </table>
                <div style="text-align: center; margin-top: 50px;">
                <a href="https://app.powerbi.com/Redirect?action=OpenReport&appId=a545d987-6ef5-4df2-816d-df6e337bc2e8&reportObjectId=ee865143-b695-4537-97f6-f74173d6c652&ctid=8fb344f4-0740-4e5a-b2c1-53858c0c732f&reportPage=739ea8bad70e0d06a51a&pbi_source=appShareLink"
                class="botao"
                style="display: inline-block; margin: 10px; padding: 10px 20px; background-color: #0078d4; color: white; text-decoration: none; border-radius: 5px;">
                🔗 Painel de Monitoramento
                </a>

                <a href="https://app.powerbi.com/groups/me/apps/ccbb1664-f0e2-439f-b607-12a98a3341e2/reports/da2a702a-8877-4eb1-a09a-76904e572776/be085ea1a58ee560d08a?ctid=8fb344f4-0740-4e5a-b2c1-53858c0c732f&experience=power-bi"
                class="botao"
                style="display: inline-block; margin: 10px; padding: 10px 20px; background-color: #0078d4; color: white; text-decoration: none; border-radius: 5px;">
                🔗 Contato das Unidades
                </a>
            </div>


                <img src="https://i.imgur.com/lhEXiPg.png" alt="Banner Final" class="imagem-banner" style="margin-top: 40px;">
            </div>
            </body>
        </html>
        """

        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = ";".join(destinatarios)
        mail.Subject = "🔔 Monitoramento de Projetos | Alerta Semanal"
        mail.HTMLBody = html
        mail.Send()

        print("🟢 " + inspect.currentframe().f_code.co_name)

        return payload, html
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def enviar_mensagem_teams_atrasos(payload):
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