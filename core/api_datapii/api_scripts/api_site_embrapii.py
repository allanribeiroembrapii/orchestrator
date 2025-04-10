import os
import inspect
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente do .env
load_dotenv()
ROOT = os.getenv('ROOT')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_2_STAGE_AREA = os.getenv('STEP_2_STAGE_AREA')

PORTFOLIO = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'portfolio.xlsx'))
UNIDADES = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'info_unidades_embrapii.xlsx'))
EMPRESAS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'projetos_empresas.xlsx'))
IPCA = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'ipca_ibge.xlsx'))
PORTFOLIO_IPCA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'portfolio_ipca.xlsx'))

# Rota da API
ROUTE_ROOT = os.getenv('ROUTE_ROOT')
API_TOKEN = os.getenv('API_TOKEN')


def corrigir_valor_ipca(ipca_df, ano_contrato, mes_contrato, valor):
    """
    Corrige um valor monetário com base na variação do IPCA entre o mês anterior ao início do contrato
    e o último mês disponível no IPCA, conforme metodologia do IBGE.

    Se o contrato for posterior ao último IPCA disponível, retorna o valor original (sem correção).

    https://www.ibge.gov.br/explica/inflacao.php
    """
    ipca_df['Mês (Código)'] = ipca_df['Mês (Código)'].astype(str)

    # Definir o mês anterior ao contrato
    if mes_contrato == 1:
        mes_anterior = 12
        ano_anterior = ano_contrato - 1
    else:
        mes_anterior = mes_contrato - 1
        ano_anterior = ano_contrato

    mes_anterior_str = f"{ano_anterior}{mes_anterior:02d}"

    # Verifica o último mês disponível na base do IPCA
    ultimo_mes_ipca = ipca_df['Mês (Código)'].iloc[-1]

    # Se o mês anterior ao contrato for posterior ao último IPCA, não corrige
    if mes_anterior_str > ultimo_mes_ipca:
        return valor  # valor nominal

    try:
        ipca_base = float(ipca_df.loc[ipca_df['Mês (Código)'] == mes_anterior_str, 'Valor'].values[0])
        ipca_final = float(ipca_df.loc[ipca_df['Mês (Código)'] == ultimo_mes_ipca, 'Valor'].values[0])

        if ipca_base == 0:
            return None

        fator = ipca_final / ipca_base
        return valor * fator
    except IndexError:
        return None



def processar_dados():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Buscar dados
    df_portfolio = pd.read_excel(PORTFOLIO)
    df_ipca = pd.read_excel(IPCA)

    # Garantir que a data está no formato datetime
    df_portfolio['data_contrato'] = pd.to_datetime(df_portfolio['data_contrato'])

    # Aplicar correção
    colunas_valores = ['valor_embrapii', 'valor_empresa', 'valor_unidade_embrapii', 'valor_sebrae']
    for col in colunas_valores:
        nova_col = f"_ipca_{col}"
        df_portfolio[nova_col] = df_portfolio.apply(
            lambda row: corrigir_valor_ipca(
                df_ipca,
                row['data_contrato'].year,
                row['data_contrato'].month,
                row[col]
            ),
            axis=1
        )
    
    # Criar a coluna _ipca_valor_total com a soma das colunas corrigidas
    colunas_ipca = [f"_ipca_{col}" for col in colunas_valores]
    df_portfolio['_ipca_valor_total'] = df_portfolio[colunas_ipca].sum(axis=1)

    df_portfolio.to_excel(PORTFOLIO_IPCA, index=False)
    print("🟢 " + inspect.currentframe().f_code.co_name)


def calcular_kpis():
    # Bases de dados
    df_portfolio = pd.read_excel(PORTFOLIO_IPCA)
    df_unidades = pd.read_excel(UNIDADES)
    df_empresas = pd.read_excel(EMPRESAS)

    # KPIs
    projetos = df_portfolio['codigo_projeto'].nunique()
    valor_total = df_portfolio['_ipca_valor_total'].sum()
    unidades = df_unidades[df_unidades['status_credenciamento'] == 'Ativado']['unidade_embrapii'].nunique()
    empresas = df_empresas['cnpj'].nunique()

    dados = {
        'projetos': projetos,
        'valor_total': valor_total,
        'unidades': unidades,
        'empresas': empresas
    }

    return dados

import requests

import requests
from datetime import datetime

def post_api_site_embrapii(dados):
    """
    Envia os dados de indicadores para a API do site da Embrapii.

    Parâmetros:
        dados (dict): Exemplo:
            {
                'projetos': 1234,
                'valor_total': 5996842298.24,
                'unidades': 95,
                'empresas': 812
            }
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    rota = ROUTE_ROOT + "/records"
    data_hoje = datetime.now().isoformat()  # formato ISO: "2025-04-10T19:12:24.760Z"
    token = API_TOKEN

    dados_descricao = {
        'projetos': {
            'name': 'Projetos Contratados',
            'descricao': 'Nº de Projetos Contratados pela Embrapii até a data de referência.'
        },
        'valor_total': {
            'name': 'Valor Total Corrigido',
            'descricao': 'Valor Total dos Projetos Contratados corrigidos pelo IPCA disponível até a data de referência.'
        },
        'unidades': {
            'name': 'Unidades Ativas',
            'descricao': 'Nº de Unidades Embrapii ativas na data de referência.'
        },
        'empresas': {
            'name': 'Empresas Atendidas',
            'descricao': 'Nº de Empresas que contrataram projetos Embrapii até a data de referência (CNPJs únicos).'
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    for chave, valor in dados.items():
        dado = {
            "dt_referencia": data_hoje,
            "no_indice": dados_descricao[chave]['name'],
            "vl_indice": valor,
            "ds_indice": dados_descricao[chave]['descricao']
        }

        response = requests.post(rota, json=dado, headers=headers)

        print("🟢 " + inspect.currentframe().f_code.co_name)


def api_site_embrapii():
    processar_dados()
    dados = calcular_kpis()
    post_api_site_embrapii(dados)