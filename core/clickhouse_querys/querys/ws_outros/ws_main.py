import inspect
from querys.ws_outros.srinfo_communication import srinfo_communication
from querys.ws_outros.srinfo_event import srinfo_event

def ws_outros():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_communication()
        srinfo_event()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")