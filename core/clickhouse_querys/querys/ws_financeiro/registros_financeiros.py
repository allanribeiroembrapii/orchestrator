from dotenv import load_dotenv
import os
import sys
from core.clickhouse_querys.connection.query_clickhouse import query_clickhouse
from core.clickhouse_querys.querys.ws_financeiro.processar_csv import processar_csv

load_dotenv()

ROOT = os.getenv('ROOT_CLICKHOUSE_QUERYS')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_2_STAGE_AREA = os.getenv('STEP_2_STAGE_AREA')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def registros_financeiros():
    query = """
        SELECT * FROM db_ouro.srinfo_registros_financeiros
                WHERE data_extracao = (
                        SELECT MAX(data_extracao) FROM db_ouro.srinfo_registros_financeiros
                )
    """
    nome_arquivo = "registros_financeiros"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)


    arquivo_origem = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW , nome_arquivo))
    arquivo_destino = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED , f"srinfo_{nome_arquivo}"))

    campos_interesse = [
        'unidade_embrapii',
        'call',
        'ano',
        'mes',
        'saldo_conta_mae_embrapii',
        'saldo_total_projeto_embrapii',
        'saldo_total_projeto_empresa',
        'saldo_outras_contas',
        'sebrae_saldo_outras_contas',
        'ppi_saldo_outras_contas',
        'rota_saldo_outras_contas',
        'bndes_saldo_outras_contas',
        'saldo_total_outras_contas',
        'sebrae_saldo_total_outras_contas',
        'ppi_saldo_total_outras_contas',
        'rota_saldo_total_outras_contas',
        'bndes_saldo_total_outras_contas',
        'transferencias',
        'despesas_embrapii',
        'despesas_empresa',
        'despesas_financeiros_unidade',
        'despesas_economicos_unidade',
        'despesas_outras_fontes',
        'sebrae_despesas_outras_fontes',
        'ppi_despesas_outras_fontes',
        'rota_despesas_outras_fontes',
        'bndes_despesas_outras_fontes',
        'data_extracao'
    ]

    novos_nomes_e_ordem = {
        'unidade_embrapii': 'unidade_embrapii',
        'call': 'call',
        'ano': 'ano',
        'mes': 'mes',
        'saldo_conta_mae_embrapii': 'saldo_conta_mae_embrapii',
        'saldo_total_projeto_embrapii': 'saldo_total_projeto_embrapii',
        'saldo_total_projeto_empresa': 'saldo_total_projeto_empresa',
        'saldo_outras_contas': 'saldo_outras_contas',
        'sebrae_saldo_outras_contas': 'sebrae_saldo_outras_contas',
        'ppi_saldo_outras_contas': 'ppi_saldo_outras_contas',
        'rota_saldo_outras_contas': 'rota_saldo_outras_contas',
        'bndes_saldo_outras_contas': 'bndes_saldo_outras_contas',
        'saldo_total_outras_contas': 'saldo_total_outras_contas',
        'sebrae_saldo_total_outras_contas': 'sebrae_saldo_total_outras_contas',
        'ppi_saldo_total_outras_contas': 'ppi_saldo_total_outras_contas',
        'rota_saldo_total_outras_contas': 'rota_saldo_total_outras_contas',
        'bndes_saldo_total_outras_contas': 'bndes_saldo_total_outras_contas',
        'transferencias': 'transferencias',
        'despesas_embrapii': 'despesas_embrapii',
        'despesas_empresa': 'despesas_empresa',
        'despesas_financeiros_unidade': 'despesas_financeiros_unidade',
        'despesas_economicos_unidade': 'despesas_economicos_unidade',
        'despesas_outras_fontes': 'despesas_outras_fontes',
        'sebrae_despesas_outras_fontes': 'sebrae_despesas_outras_fontes',
        'ppi_despesas_outras_fontes': 'ppi_despesas_outras_fontes',
        'rota_despesas_outras_fontes': 'rota_despesas_outras_fontes',
        'bndes_despesas_outras_fontes': 'bndes_despesas_outras_fontes',
        'data_extracao': 'data_extracao',
    }

    campos_valor = ['saldo_conta_mae_embrapii', 'saldo_total_projeto_embrapii', 'saldo_total_projeto_empresa',
                    'saldo_outras_contas', 'saldo_total_outras_contas', 'transferencias', 'despesas_embrapii',
                    'despesas_empresa', 'despesas_financeiros_unidade', 'despesas_economicos_unidade', 'despesas_outras_fontes',
                    'sebrae_saldo_total_outras_contas', 'ppi_saldo_total_outras_contas', 'rota_saldo_total_outras_contas',
                    'bndes_saldo_total_outras_contas', 'sebrae_saldo_outras_contas', 'ppi_saldo_outras_contas', 'rota_saldo_outras_contas',
                    'bndes_saldo_outras_contas', 'sebrae_despesas_outras_fontes', 'ppi_despesas_outras_fontes', 'rota_despesas_outras_fontes',
                    'bndes_despesas_outras_fontes', ]

    processar_csv(arquivo_origem = arquivo_origem, campos_interesse = campos_interesse, novos_nomes_e_ordem = novos_nomes_e_ordem,
                    arquivo_destino = arquivo_destino, campos_valor = campos_valor)