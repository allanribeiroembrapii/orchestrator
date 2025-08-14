import inspect
from core.clickhouse_saldo_bancario.querys.ws_agfinanceiro.saldo_bancario import clickhouse_saldo_bancario, clickhouse_saldo_bancario_historico

def ws_agfinanceiro():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        clickhouse_saldo_bancario()
        clickhouse_saldo_bancario_historico()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")