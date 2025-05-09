from dotenv import load_dotenv
import os
import sys
from connection.query_clickhouse import query_clickhouse
from querys.ws_financeiro.processar_csv import processar_csv

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_2_STAGE_AREA = os.getenv('STEP_2_STAGE_AREA')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def repasses():
    query = """
                SELECT  U.name
        ,FT.request_date
        ,FT.transfer_type
        ,C.name
        ,FT.value
        ,FT.after_transfer_balance
        ,FT.embrapii_account_balance
        ,FT.investment_balance
        ,FT.period_interest
        ,PA.SaldoContasEMBRAPII
        ,PA.SaldoAplicacoesEMBRAPII
        ,PA.SaldoContasEmpresa
        ,PA.SaldoAplicacoesEmpresa
        ,FT.ticket_transfer
        ,FT.notes
FROM    db_bronze_srinfo.ue_unit                     U
JOIN    db_bronze_srinfo.financial_fundstransfer     FT  ON  U.id            = FT.ue_id
JOIN    db_bronze_srinfo.partnership_call            C   ON  FT.call_id      = C.id
LEFT JOIN    (
        SELECT  funds_transfer_id
                ,SUM(CASE WHEN PS.alias = 'EMBRAPII'   AND PA.account_type = '1'  THEN PA.balance ELSE 0 END) SaldoContasEMBRAPII
                ,SUM(CASE WHEN PS.alias = 'EMBRAPII'   AND PA.account_type = '2'  THEN PA.balance ELSE 0 END) SaldoAplicacoesEMBRAPII
                ,SUM(CASE WHEN PS.alias = 'Empresa'    AND PA.account_type = '1'  THEN PA.balance ELSE 0 END) SaldoContasEmpresa
                ,SUM(CASE WHEN PS.alias = 'Empresa'    AND PA.account_type = '2'  THEN PA.balance ELSE 0 END) SaldoAplicacoesEmpresa
        FROM    db_bronze_srinfo.financial_projectaccount    PA
        JOIN    db_bronze_srinfo.project_source              PS  ON PA.source_id     = PS.id
        WHERE   PA.data_inativacao         IS NULL
        AND     PS.data_inativacao         IS NULL
        GROUP BY funds_transfer_id
        )                           PA  ON  FT.id           = PA.funds_transfer_id
WHERE   U.data_inativacao           IS NULL
AND     FT.data_inativacao          IS NULL
AND     C.data_inativacao           IS NULL
    """
    nome_arquivo = "repasses"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    arquivo_origem = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW , nome_arquivo))
    arquivo_destino = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED , f"srinfo_{nome_arquivo}"))

    campos_interesse = [
            'U.name',
            'request_date',
            'transfer_type',
            'C.name',
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
            'U.name': 'unidade_embrapii',
            'request_date': 'data_solicitacao',
            'transfer_type': 'tipo_transferencia',
            'C.name': 'call',
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