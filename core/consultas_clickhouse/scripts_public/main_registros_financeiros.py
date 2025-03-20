from dotenv import load_dotenv
import os
import sys
from consultas_clickhouse.scripts_public.consulta_clickhouse import consulta_clickhouse
from consultas_clickhouse.scripts_public.processar_csv import processar_csv

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')

pasta = '1_data_raw'
nome_arquivo = 'registros_financeiros'

def processar_registros_financeiros():

        print("Gerando planilha de registros financeiros")
        # Definições dos caminhos e nomes de arquivos
        origem = os.path.join(ROOT, '1_data_raw')
        destino = os.path.join(ROOT, '2_data_processed')
        arquivo_origem = os.path.join(origem, nome_arquivo)
        arquivo_destino = os.path.join(destino, nome_arquivo)

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

def main_registros_financeiros():
    # Consulta ao ClickHouse
    query = """
            SELECT  UE.name                                     AS ue_name
        ,PC.name                                    AS call_name
        ,M.month_year                               AS ms_date
        ,FB.embrapii_account_balance                AS  SALDO_ContaMAEEMBRAPII
        ,FB.project_account_balance                 AS  SALDO_Totalprojetoembrapii
        ,FB.project_company_account                 AS  SALDO_Totalprojetoempresa
        ,IFNULL(SUM(MA.main_account_balance), 0)    AS  SALDO_Outrascontasespecificas
        ,IFNULL(SUM(MA.balance), 0)                 AS  SALDO_Totaloutrascontasprojeto
        ,IC.transferred_amounts                     AS  TRANSFERENCIAS
        ,EX.embrapii_amounts                        AS  DESPESAS_EMBRAPII
        ,EX.company_amounts                         AS  DESPESAS_Empresa
        ,EX.ue_financial_amounts                    AS  DESPESAS_financeirosUE
        ,EX.ue_economic_amounts                     AS  DESPESAS_economicosUE
        ,IFNULL(SUM(MA.expense_amount), 0)          AS  DESPESA_Recursosoutrasfontes
        ,'Totaloutrascontasprojeto'
        ,SEBRAE_SALDO_Totaloutrascontasprojeto
        ,PPI_SALDO_Totaloutrascontasprojeto
        ,ROTA2030_SALDO_Totaloutrascontasprojeto
        ,BNDES_SALDO_Totaloutrascontasprojeto
        ,'Outrascontasespecificas'
        ,SEBRAE_SALDO_Outrascontasespecificas
        ,PPI_SALDO_Outrascontasespecificas
        ,ROTA2030_SALDO_Outrascontasespecificas
        ,BNDES_SALDO_Outrascontasespecificas
        ,'Recursosoutrasfontes'
        ,SEBRAE_DESPESA_Recursosoutrasfontes
        ,PPI_DESPESA_Recursosoutrasfontes
        ,ROTA2030_DESPESA_Recursosoutrasfontes
        ,BNDES_DESPESA_Recursosoutrasfontes

FROM            db_bronze_srinfo.financial_monthlystatement M
LEFT OUTER JOIN db_bronze_srinfo.financial_msaccount        MA  ON M.id       = MA.reference_id AND M.data_inativacao IS NULL AND MA.data_inativacao IS NULL
INNER JOIN      db_bronze_srinfo.ue_unit                    UE  ON M.ue_id    = UE.id           AND UE.data_inativacao IS NULL
LEFT OUTER JOIN db_bronze_srinfo.partnership_call           PC  ON M.call_id  = PC.id           AND PC.data_inativacao IS NULL
LEFT OUTER JOIN db_bronze_srinfo.financial_balance          FB  ON M.id       = FB.reference_id AND FB.data_inativacao IS NULL
LEFT OUTER JOIN db_bronze_srinfo.financial_income           IC  ON M.id       = IC.reference_id AND IC.data_inativacao IS NULL
LEFT OUTER JOIN db_bronze_srinfo.financial_expense          EX  ON M.id       = EX.reference_id AND EX.data_inativacao IS NULL
LEFT JOIN       (
                SELECT  SMA.reference_id
                        ,SUMIf(SMA.balance               ,account = '3') AS SEBRAE_SALDO_Totaloutrascontasprojeto
                        ,SUMIf(SMA.main_account_balance  ,account = '3') AS SEBRAE_SALDO_Outrascontasespecificas
                        ,SUMIf(SMA.expense_amount        ,account = '3') AS SEBRAE_DESPESA_Recursosoutrasfontes
                        ,SUMIf(SMA.balance               ,account = '4') AS PPI_SALDO_Totaloutrascontasprojeto
                        ,SUMIf(SMA.main_account_balance  ,account = '4') AS PPI_SALDO_Outrascontasespecificas
                        ,SUMIf(SMA.expense_amount        ,account = '4') AS PPI_DESPESA_Recursosoutrasfontes
                        ,SUMIf(SMA.balance               ,account = '5') AS ROTA2030_SALDO_Totaloutrascontasprojeto
                        ,SUMIf(SMA.main_account_balance  ,account = '5') AS ROTA2030_SALDO_Outrascontasespecificas
                        ,SUMIf(SMA.expense_amount        ,account = '5') AS ROTA2030_DESPESA_Recursosoutrasfontes
                        ,SUMIf(SMA.balance               ,account = '7') AS BNDES_SALDO_Totaloutrascontasprojeto
                        ,SUMIf(SMA.main_account_balance  ,account = '7') AS BNDES_SALDO_Outrascontasespecificas
                        ,SUMIf(SMA.expense_amount        ,account = '7') AS BNDES_DESPESA_Recursosoutrasfontes
                FROM db_bronze_srinfo.financial_msaccount   SMA
                WHERE SMA.data_inativacao   IS NULL
                GROUP BY SMA.reference_id
                )                                           DMA ON  M.id       = DMA.reference_id

GROUP BY UE.name
        ,PC.name
        ,M.month_year
        ,FB.embrapii_account_balance
        ,FB.project_account_balance
        ,FB.project_company_account
        ,IC.transferred_amounts
        ,EX.embrapii_amounts
        ,EX.company_amounts
        ,EX.ue_financial_amounts
        ,EX.ue_economic_amounts
        ,SEBRAE_SALDO_Totaloutrascontasprojeto
        ,PPI_SALDO_Totaloutrascontasprojeto
        ,ROTA2030_SALDO_Totaloutrascontasprojeto
        ,BNDES_SALDO_Totaloutrascontasprojeto
        ,SEBRAE_SALDO_Outrascontasespecificas
        ,PPI_SALDO_Outrascontasespecificas
        ,ROTA2030_SALDO_Outrascontasespecificas
        ,BNDES_SALDO_Outrascontasespecificas
        ,SEBRAE_DESPESA_Recursosoutrasfontes
        ,PPI_DESPESA_Recursosoutrasfontes
        ,ROTA2030_DESPESA_Recursosoutrasfontes
        ,BNDES_DESPESA_Recursosoutrasfontes

ORDER BY UE.name                    ASC
        ,M.month_year               DESC
        ,PC.name                    ASC
    """

    consulta_clickhouse(HOST, PORT, USER, PASSWORD, query, pasta, nome_arquivo)
    processar_registros_financeiros()

if __name__== "__main__":
      main_registros_financeiros()
