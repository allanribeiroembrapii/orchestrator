import pandas as pd
import os
from dotenv import load_dotenv
import inspect

# Carregar as variáveis de ambiente
load_dotenv()
ROOT = os.getenv('ROOT')
PLANILHAS = os.path.abspath(os.path.join(ROOT, 'copy_sharepoint_atual'))
ANTERIOR = os.path.abspath(os.path.join(ROOT, 'copy_sharepoint_anterior'))


def projetos_acima_5mi():
    """
    Função para obter os dados necessários dos projetos para o envio da mensagem ao Teams.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        # Carregar as planilhas
        projetos_atual = pd.read_excel(os.path.join(PLANILHAS, "portfolio.xlsx"))  # Planilha de projetos (atual)
        projetos_anterior = pd.read_excel(os.path.join(ANTERIOR, "portfolio.xlsx"))  # Planilha de projetos (anterior)

        # Filtra apenas os projetos que estão em 'projetos_atual' e não em 'projetos_anterior'
        novos_projetos = projetos_atual[~projetos_atual['codigo_projeto'].isin(projetos_anterior['codigo_projeto'])]

        # Agora, filtra os que têm valor total acima de 5 milhões
        novos_projetos['valor_total'] = novos_projetos['valor_embrapii'] + novos_projetos['valor_empresa'] + novos_projetos['valor_unidade_embrapii'] + novos_projetos['valor_sebrae']
        novos_acima_5mi = novos_projetos[novos_projetos['valor_total'] >= 5000000]

        # Filtra por palavra-chave (ignora maiúsculas/minúsculas e trata valores ausentes)
        novos_filtrados = novos_acima_5mi[
            novos_acima_5mi['modalidade_financiamento'].str.contains('ROTA', case=False, na=False)
            ]

        print("🟢 " + inspect.currentframe().f_code.co_name)

        return novos_filtrados
    
    except Exception as e:
        print(f"🔴 Erro: {e}")

