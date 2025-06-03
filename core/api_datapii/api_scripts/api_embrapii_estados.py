import os
import inspect
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import requests
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

STEP_1_DATA_RAW = "data/step_1_data_raw"
STEP_2_STAGE_AREA = "data/step_2_stage_area"
STEP_3_DATA_PROCESSED = "data/step_3_data_processed"

# Definir caminhos dos arquivos
PORTFOLIO = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "portfolio.xlsx"))
UNIDADES = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "info_unidades_embrapii.xlsx"))
PROJETOS_EMPRESAS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "projetos_empresas.xlsx"))
INFO_EMPRESAS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, "info_empresas.xlsx"))
PROJETOS_EMPRESAS_PRO = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, "projetos_empresas_pro.xlsx"))

API_TOKEN = os.getenv("API_TOKEN")
if API_TOKEN is None:
    API_TOKEN = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

#ACESSO CLICKHOUSE
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')

def criar_planilha_projetos_empresas_pro():    
    # Dataframes
    df_portfolio = pd.read_excel(PORTFOLIO)
    df_projetos_empresas = pd.read_excel(PROJETOS_EMPRESAS)
    df_info_empresas = pd.read_excel(INFO_EMPRESAS)

    # Merge para trazer a UF da empresa
    df_projetos_empresas = df_projetos_empresas.merge(
        df_info_empresas[['cnpj', 'endereco_uf']].rename(columns={'endereco_uf': 'uf_empresa'}),
        on='cnpj',
        how='left'
    )

    # Preparar dataframe auxiliar com o _ipca_valor_total ajustado
    df_ipca = df_portfolio[['codigo_projeto', '_ipca_valor_total', 'n_empresas']].copy()
    df_ipca['_ipca_valor_total_por_empresa'] = df_ipca['_ipca_valor_total'] / df_ipca['n_empresas']

    # Merge para adicionar a coluna ajustada
    df_projetos_empresas = df_projetos_empresas.merge(
        df_ipca[['codigo_projeto', '_ipca_valor_total_por_empresa']],
        on='codigo_projeto',
        how='left'
    )

    # Renomear a coluna conforme desejado
    df_projetos_empresas = df_projetos_empresas.rename(
        columns={'_ipca_valor_total_por_empresa': '_ipca_valor_total'}
    )

    # Merge para trazer a Área de Aplicação e Nº de Pedidos de PI
    df_projetos_empresas = df_projetos_empresas.merge(
        df_portfolio[['codigo_projeto', 'area_aplicacao', 'n_pedidos_pi']],
        on='codigo_projeto',
        how='left'
    )

    # Exportar dados
    df_projetos_empresas.to_excel(PROJETOS_EMPRESAS_PRO, index=False)

def calcular_valores_por_uf():
    df_projetos_empresas_pro = pd.read_excel(PROJETOS_EMPRESAS_PRO)
    df_unidades = pd.read_excel(UNIDADES)

    lista_ufs = [
        "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", 
        "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", 
        "RO", "RR", "RS", "SC", "SE", "SP", "TO"
    ]

    dict_dados = {}

    for uf in lista_ufs:
        # Filtrar pela UF
        df_projetos_empresas_filtrado = df_projetos_empresas_pro[df_projetos_empresas_pro['uf_empresa'] == uf]
        df_unidades_filtrado = df_unidades[(df_unidades['uf'] == uf) & (df_unidades['status_credenciamento'] == "Ativado")]

        # Calcular áreas de aplicação
        areas_aplicacao = calcular_areas_aplicacao(df_projetos_empresas_filtrado)
        impacto_uf = calcular_impacto_uf(df_projetos_empresas_filtrado, df_unidades_filtrado)
        unidades = listar_unidades(df_unidades_filtrado)
        dados = {
            'area_aplicacao': areas_aplicacao,
            'impacto_uf': impacto_uf,
            'unidades': unidades,
        }
        dict_dados[uf] = dados
    
    return dict_dados

def calcular_areas_aplicacao(dataframe):
    df = dataframe

    # Agrupar e somar o _ipca_valor_total por area_aplicacao
    df_agrupado = (
        df.groupby('area_aplicacao')['_ipca_valor_total']
        .sum()
        .reset_index()
        .rename(columns={'_ipca_valor_total': 'valor_total'})
    )

    # Calcular o percentual
    soma_total = df_agrupado['valor_total'].sum()
    df_agrupado['percentual'] = (df_agrupado['valor_total'] / soma_total) * 100

    # Ordenar pelo percentual decrescente
    df_agrupado = df_agrupado.sort_values(by='percentual', ascending=False)

    # Pegar os 5 maiores
    df_top5 = df_agrupado.head(5)

    # Transformar em dicionário no formato { 'Área': percentual, ... }
    resultado = dict(
        zip(df_top5['area_aplicacao'], df_top5['percentual'].round(1))
    )

    return resultado

def calcular_impacto_uf(dataframe_projetos_empresas, dataframe_unidades):
    df_projetos_empresas = dataframe_projetos_empresas
    df_unidades = dataframe_unidades

    # Contagem única de projetos
    total_projetos = df_projetos_empresas['codigo_projeto'].nunique()
    total_valor = df_projetos_empresas['_ipca_valor_total'].sum()
    total_empresas = df_projetos_empresas['cnpj'].nunique()
    total_pi = df_projetos_empresas.drop_duplicates(subset='codigo_projeto')['n_pedidos_pi'].sum()
    total_unidades = df_unidades['unidade_embrapii'].nunique()

    return {
        'projetos_contratados': int(total_projetos),
        'valor_total': round(float(total_valor), 0),
        'empresas': int(total_empresas),
        'pedidos_pi': int(total_pi),
        'unidades_embrapii': int(total_unidades)
    }

def listar_unidades(dataframe):
    df = dataframe.copy()
    df['municipio_uf'] = df['municipio'] + '-' + df['uf']
    resultado = dict(zip(df['unidade_embrapii'], df['municipio_uf']))
    return resultado

def enviar_banco_dados(dict_dados):
    connect_vpn()
    dt_carga = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    id_atual = obter_ultimo_id() + 1

    for uf, dados_uf in dict_dados.items():
        sql, novo_id = construir_sql(uf, dados_uf, dt_carga, id_atual)
        if sql:
            query_clickhouse(HOST, PORT, USER, PASSWORD, sql)
            id_atual = novo_id
    disconnect_vpn()

def construir_sql(uf, dados, dt_carga, id_inicial):
    sql_linhas = []
    id_atual = id_inicial
    conjunto = "Embrapii nos Estados"

    for chave, grupo in dados.items():
        if chave == "area_aplicacao":
            for item, valor in grupo.items():
                ds_valor = formatar_valor_percentual(valor)
                sql_linhas.append(
                    f"({id_atual}, '{dt_carga}', '{conjunto}', '{uf}', 'Área de Aplicação', '{item}', '{ds_valor}')"
                )
                id_atual += 1
        elif chave == "impacto_uf":
            for item, valor in grupo.items():
                ds_valor = formatar_milhar(valor)
                sql_linhas.append(
                    f"({id_atual}, '{dt_carga}', '{conjunto}', '{uf}', 'Impacto na UF', '{item}', '{ds_valor}')"
                )
                id_atual += 1
        elif chave == "unidades":
            for unidade, local in grupo.items():
                sql_linhas.append(
                    f"({id_atual}, '{dt_carga}', '{conjunto}', '{uf}', 'Unidades Embrapii', '{unidade}', '{local}')"
                )
                id_atual += 1

    if not sql_linhas:
        return None, id_atual

    sql = (
        "INSERT INTO data_pii.db_api_site_embrapii"
        "(id, dt_carga, ds_conjunto, ds_subconjunto, ds_indicador, ds_item, ds_valor) VALUES\n"
        + ",\n".join(sql_linhas)
        + ";"
    )
    return sql, id_atual

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

def api_embrapii_nos_estados():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    criar_planilha_projetos_empresas_pro()
    dados = calcular_valores_por_uf()
    enviar_banco_dados(dados)
    print("🟢 " + inspect.currentframe().f_code.co_name)
