from dotenv import load_dotenv
import os
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


def repasses():
    query = f"""
        SELECT *
        FROM db_ouro.srinfo_repasses_financeiros
        WHERE dt_atualizacao = (
        SELECT MAX(dt_atualizacao)
        FROM db_ouro.srinfo_repasses_financeiros
        )
    """
    nome_arquivo = "repasses"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    arquivo_origem = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW , nome_arquivo))
    arquivo_destino = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED , f"srinfo_{nome_arquivo}"))

    campos_interesse = [
            'ue_name',
            'request_date',
            'transfer_type',
            'call_name',
            'value',
            'after_transfer_balance',
            'embrapii_account_balance',
            'investment_balance',
            'period_interest',
            'SaldoContasEMBRAPII',
            'SaldoAplicacoesEMBRAPII',
            'SaldoContasEmpresa',
            'SaldoAplicacoesEmpresa',
            'ticket_transfer',
            'notes',
    ]

    novos_nomes_e_ordem = {
            'ue_name': 'unidade_embrapii',
            'request_date': 'data_solicitacao',
            'transfer_type': 'tipo_transferencia',
            'call_name': 'call',
            'value': 'valor',
            'after_transfer_balance':
            'saldo_apos_transferencia',
            'embrapii_account_balance': 'saldo_conta_especifica_embrapii',
            'investment_balance': 'saldo_aplicacoes_conta_especifica_embrapii',
            'period_interest': 'rendimento_periodo',
            'SaldoContasEMBRAPII': 'saldo_contas_embrapii',
            'SaldoAplicacoesEMBRAPII': 'saldo_aplicacoes_embrapii',
            'SaldoContasEmpresa': 'saldo_contas_empresa',
            'SaldoAplicacoesEmpresa': 'saldo_aplicacoes_empresa',
            'ticket_transfer': 'ticket_repasse',
            'notes': 'observacoes',
    }

    campos_valor = ['valor', 'saldo_apos_transferencia', 'saldo_conta_especifica_embrapii',
                    'saldo_aplicacoes_conta_especifica_embrapii', 'rendimento_periodo',
                    'saldo_contas_embrapii', 'saldo_aplicacoes_embrapii',
                    'saldo_contas_empresa', 'saldo_aplicacoes_empresa']
    
    campos_data = ['data_solicitacao']


    processar_csv(arquivo_origem = arquivo_origem, campos_interesse = campos_interesse, novos_nomes_e_ordem = novos_nomes_e_ordem,
                    arquivo_destino = arquivo_destino, campos_valor = campos_valor, campos_data=campos_data)