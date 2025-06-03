import inspect
from core.clickhouse_querys.querys.ws_financeiro.repasses import repasses
from core.clickhouse_querys.querys.ws_financeiro.registros_financeiros import registros_financeiros

def ws_financeiro():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        repasses()
        registros_financeiros()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")