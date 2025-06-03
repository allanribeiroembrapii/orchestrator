import os
import inspect
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import requests
from datetime import datetime
from core.api_datapii.connection.query_clickhouse import query_clickhouse, query_clickhouse_com_retorno
from core.api_datapii.connection.connect_vpn import connect_vpn, disconnect_vpn

# Obter o diretório atual e o diretório raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente do .env
load_dotenv()
ROOT = os.getenv("ROOT_DATAPII")
if not ROOT:
    ROOT = parent_dir

STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
if not STEP_1_DATA_RAW:
    STEP_1_DATA_RAW = "data/step_1_data_raw"

STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
if not STEP_2_STAGE_AREA:
    STEP_2_STAGE_AREA = "data/step_2_stage_area"


# Função para verificar e criar diretórios se não existirem
def verificar_criar_diretorio(caminho):
    """
    Verifica se um diretório existe e o cria se não existir.

    Args:
        caminho: Caminho do diretório a ser verificado/criado
    """
    diretorio = os.path.dirname(caminho)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

# Definir caminhos dos arquivos
PORTFOLIO = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "portfolio.xlsx"))
UNIDADES = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "info_unidades_embrapii.xlsx"))
EMPRESAS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "projetos_empresas.xlsx"))
IPCA = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "ipca_ibge.xlsx"))
EQUIPE_UE = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "equipe_ue.xlsx"))
PORTFOLIO_IPCA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, "portfolio_ipca.xlsx"))

# Verificar e criar diretórios necessários
for caminho in [PORTFOLIO, UNIDADES, EMPRESAS, IPCA, PORTFOLIO_IPCA]:
    verificar_criar_diretorio(caminho)

# Rota da API
ROUTE_ROOT = os.getenv("ROUTE_ROOT")
if ROUTE_ROOT is None:
    ROUTE_ROOT = "https://datapii.embrapii.org.br"

API_TOKEN = os.getenv("API_TOKEN")
if API_TOKEN is None:
    API_TOKEN = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # Valor padrão caso a variável de ambiente não esteja definida

#ACESSO CLICKHOUSE
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')

def corrigir_valor_ipca(ipca_df, ano_contrato, mes_contrato, valor):
    """
    Corrige um valor monetário com base na variação do IPCA entre o mês anterior ao início do contrato
    e o último mês disponível no IPCA, conforme metodologia do IBGE.

    Se o contrato for posterior ao último IPCA disponível, retorna o valor original (sem correção).

    https://www.ibge.gov.br/explica/inflacao.php
    """
    ipca_df["Mês (Código)"] = ipca_df["Mês (Código)"].astype(str)

    # Definir o mês anterior ao contrato
    if mes_contrato == 1:
        mes_anterior = 12
        ano_anterior = ano_contrato - 1
    else:
        mes_anterior = mes_contrato - 1
        ano_anterior = ano_contrato

    mes_anterior_str = f"{ano_anterior}{mes_anterior:02d}"

    # Verifica o último mês disponível na base do IPCA
    ultimo_mes_ipca = ipca_df["Mês (Código)"].iloc[-1]

    # Se o mês anterior ao contrato for posterior ao último IPCA, não corrige
    if mes_anterior_str > ultimo_mes_ipca:
        return valor  # valor nominal

    try:
        ipca_base = float(
            ipca_df.loc[ipca_df["Mês (Código)"] == mes_anterior_str, "Valor"].values[0]
        )
        ipca_final = float(
            ipca_df.loc[ipca_df["Mês (Código)"] == ultimo_mes_ipca, "Valor"].values[0]
        )

        if ipca_base == 0:
            return None

        fator = ipca_final / ipca_base
        return valor * fator
    except IndexError:
        return None

def processar_dados():
    # Buscar dados
    df_portfolio = pd.read_excel(PORTFOLIO)
    df_ipca = pd.read_excel(IPCA)

    # Garantir que a data está no formato datetime
    df_portfolio["data_contrato"] = pd.to_datetime(df_portfolio["data_contrato"])

    # Aplicar correção
    colunas_valores = [
        "valor_embrapii",
        "valor_empresa",
        "valor_unidade_embrapii",
        "valor_sebrae",
    ]
    for col in colunas_valores:
        nova_col = f"_ipca_{col}"
        df_portfolio[nova_col] = df_portfolio.apply(
            lambda row: corrigir_valor_ipca(
                df_ipca, row["data_contrato"].year, row["data_contrato"].month, row[col]
            ),
            axis=1,
        )

    # Criar a coluna _ipca_valor_total com a soma das colunas corrigidas
    colunas_ipca = [f"_ipca_{col}" for col in colunas_valores]
    df_portfolio["_ipca_valor_total"] = df_portfolio[colunas_ipca].sum(axis=1)

    # Garantir que o diretório existe antes de salvar o arquivo
    verificar_criar_diretorio(PORTFOLIO_IPCA)
    df_portfolio.to_excel(PORTFOLIO_IPCA, index=False)

def calcular_kpis():
    # Bases de dados
    df_portfolio = pd.read_excel(PORTFOLIO_IPCA)
    df_unidades = pd.read_excel(UNIDADES)
    df_empresas = pd.read_excel(EMPRESAS)
    df_equipe_ue = pd.read_excel(EQUIPE_UE)

    # KPIs
    projetos = df_portfolio["codigo_projeto"].nunique()
    valor_total = df_portfolio["_ipca_valor_total"].sum()
    unidades = df_unidades[df_unidades["status_credenciamento"] == "Ativado"]["unidade_embrapii"].nunique()
    empresas = df_empresas["cnpj"].nunique()
    pessoas_envolvidas = df_equipe_ue["cpf"].nunique()

    dados = {
        "projetos": projetos,
        "valor_total": valor_total,
        "unidades": unidades,
        "empresas": empresas,
        "pessoas_envolvidas": pessoas_envolvidas,
    }

    return dados

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
    rota = ROUTE_ROOT + "site-embrapii/"
    data_hoje = datetime.now().isoformat()  # formato ISO: "2025-04-10T19:12:24.760Z"
    token = API_TOKEN
    dados_descricao = {
        "projetos": {
            "name": "Projetos Contratados",
            "descricao": "Nº de Projetos Contratados pela Embrapii até a data de referência.",
        },
        "valor_total": {
            "name": "Valor Total IPCA",
            "descricao": "Valor Total dos Projetos Contratados corrigidos pelo IPCA disponível até a data de referência.",
        },
        "unidades": {
            "name": "Unidades Ativas",
            "descricao": "Nº de Unidades Embrapii ativas na data de referência.",
        },
        "empresas": {
            "name": "Empresas Atendidas",
            "descricao": "Nº de Empresas que contrataram projetos Embrapii até a data de referência (CNPJs únicos).",
        },
        "pessoas_envolvidas": {
            "name": "Pessoas Envolvidas",
            "descricao": "Nº de pessoas envolvidas nos projetos Embrapii desde o início (CPFs únicos).",
        },
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for chave, valor in dados.items():
        dado = {
            "dt_referencia": data_hoje,
            "no_indice": dados_descricao[chave]["name"],
            "vl_indice": valor,
            "ds_indice": dados_descricao[chave]["descricao"],
        }
        response = requests.post(rota, json=dado, headers=headers)

def enviar_banco_dados(dict_dados):
    connect_vpn()
    dt_carga = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    id_atual = obter_ultimo_id() + 1
    sql = construir_sql(dict_dados, dt_carga, id_atual)
    if sql:
        query_clickhouse(HOST, PORT, USER, PASSWORD, sql)
    disconnect_vpn()

def construir_sql(dados, dt_carga, id_inicial):
    sql_linhas = []
    id_atual = id_inicial
    conjunto = "Números Gerais"
    subconjunto = "-"
    ds_indicador = "-"

    for chave, valor in dados.items():
        if chave == "valor_total":
            ds_valor = formatar_milhar(round(valor))
        else:
            ds_valor = formatar_milhar(valor)

        linha = (
            f"({id_atual}, '{dt_carga}', '{conjunto}', '{subconjunto}', "
            f"'{ds_indicador}', '{chave}', '{ds_valor}')"
        )
        sql_linhas.append(linha)
        id_atual += 1

    if not sql_linhas:
        return None

    sql = (
        "INSERT INTO data_pii.db_api_site_embrapii"
        "(id, dt_carga, ds_conjunto, ds_subconjunto, ds_indicador, ds_item, ds_valor) VALUES\n"
        + ",\n".join(sql_linhas)
        + ";"
    )
    return sql

def formatar_valor_percentual(valor):
    if isinstance(valor, (int, float)):
        return f"{format(valor, '.1f').replace('.', ',')}%"
    return valor

def formatar_milhar(valor):
    if isinstance(valor, (int, float)):
        return format(int(valor), ",").replace(",", ".")
    return valor

def obter_ultimo_id():
    query = "SELECT max(id) FROM data_pii.db_api_site_embrapii"
    resultado = query_clickhouse_com_retorno(HOST, PORT, USER, PASSWORD, query)
    if resultado and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def api_site_embrapii():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    processar_dados()
    dados = calcular_kpis()
    enviar_banco_dados(dados)
    post_api_site_embrapii(dados)
    print("🟢 " + inspect.currentframe().f_code.co_name)
    return
