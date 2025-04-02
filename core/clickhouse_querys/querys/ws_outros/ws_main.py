import inspect
from querys.ws_outros.srinfo_communication import srinfo_communication

def ws_outros():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_communication()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")