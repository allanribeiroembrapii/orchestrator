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
            'ue_name',
            'call_name',
            'ms_date',
            'SALDO_ContaMAEEMBRAPII',
            'SALDO_Totalprojetoembrapii',
            'SALDO_Totalprojetoempresa',
            'SALDO_Outrascontasespecificas',
            'SALDO_Totaloutrascontasprojeto',
            'TRANSFERENCIAS', 'DESPESAS_EMBRAPII',
            'DESPESAS_Empresa', 'DESPESAS_financeirosUE',
            'DESPESAS_economicosUE', 'DESPESA_Recursosoutrasfontes',
            'SEBRAE_SALDO_Totaloutrascontasprojeto',
            'PPI_SALDO_Totaloutrascontasprojeto',
            'ROTA2030_SALDO_Totaloutrascontasprojeto',
            'BNDES_SALDO_Totaloutrascontasprojeto',
            'SEBRAE_SALDO_Outrascontasespecificas',
            'PPI_SALDO_Outrascontasespecificas',
            'ROTA2030_SALDO_Outrascontasespecificas',
            'BNDES_SALDO_Outrascontasespecificas',
            'SEBRAE_DESPESA_Recursosoutrasfontes',
            'PPI_DESPESA_Recursosoutrasfontes',
            'ROTA2030_DESPESA_Recursosoutrasfontes',
            'BNDES_DESPESA_Recursosoutrasfontes', 
    ]

    novos_nomes_e_ordem = {
            'ue_name': 'unidade_embrapii',
            'call_name': 'call',
            'ano': 'ano',
            'mes': 'mes',
            'SALDO_ContaMAEEMBRAPII': 'saldo_conta_mae_embrapii',
            'SALDO_Totalprojetoembrapii': 'saldo_total_projeto_embrapii',
            'SALDO_Totalprojetoempresa': 'saldo_total_projeto_empresa',
            'SALDO_Outrascontasespecificas': 'saldo_outras_contas',
            'SEBRAE_SALDO_Outrascontasespecificas': 'sebrae_saldo_outras_contas',
            'PPI_SALDO_Outrascontasespecificas': 'ppi_saldo_outras_contas',
            'ROTA2030_SALDO_Outrascontasespecificas': 'rota_saldo_outras_contas',
            'BNDES_SALDO_Outrascontasespecificas': 'bndes_saldo_outras_contas',
            'SALDO_Totaloutrascontasprojeto': 'saldo_total_outras_contas',
            'SEBRAE_SALDO_Totaloutrascontasprojeto': 'sebrae_saldo_total_outras_contas',
            'PPI_SALDO_Totaloutrascontasprojeto': 'ppi_saldo_total_outras_contas',
            'ROTA2030_SALDO_Totaloutrascontasprojeto': 'rota_saldo_total_outras_contas',
            'BNDES_SALDO_Totaloutrascontasprojeto': 'bndes_saldo_total_outras_contas',
            'TRANSFERENCIAS': 'transferencias',
            'DESPESAS_EMBRAPII': 'despesas_embrapii',
            'DESPESAS_Empresa': 'despesas_empresa',
            'DESPESAS_financeirosUE': 'despesas_financeiros_unidade',
            'DESPESAS_economicosUE': 'despesas_economicos_unidade',
            'DESPESA_Recursosoutrasfontes': 'despesas_outras_fontes',
            'SEBRAE_DESPESA_Recursosoutrasfontes': 'sebrae_despesas_outras_fontes',
            'PPI_DESPESA_Recursosoutrasfontes': 'ppi_despesas_outras_fontes',
            'ROTA2030_DESPESA_Recursosoutrasfontes': 'rota_despesas_outras_fontes',
            'BNDES_DESPESA_Recursosoutrasfontes': 'bndes_despesas_outras_fontes',
    }

    campos_valor = ['saldo_conta_mae_embrapii', 'saldo_total_projeto_embrapii', 'saldo_total_projeto_empresa',
                    'saldo_outras_contas', 'saldo_total_outras_contas', 'transferencias', 'despesas_embrapii',
                    'despesas_empresa', 'despesas_financeiros_unidade', 'despesas_economicos_unidade', 'despesas_outras_fontes',
                    'sebrae_saldo_total_outras_contas', 'ppi_saldo_total_outras_contas', 'rota_saldo_total_outras_contas',
                    'bndes_saldo_total_outras_contas', 'sebrae_saldo_outras_contas', 'ppi_saldo_outras_contas', 'rota_saldo_outras_contas',
                    'bndes_saldo_outras_contas', 'sebrae_despesas_outras_fontes', 'ppi_despesas_outras_fontes', 'rota_despesas_outras_fontes',
                    'bndes_despesas_outras_fontes', ]

    processar_csv(arquivo_origem = arquivo_origem, campos_interesse = campos_interesse, novos_nomes_e_ordem = novos_nomes_e_ordem,
                    arquivo_destino = arquivo_destino, campos_valor = campos_valor, mes_ano = ['ms_date'])