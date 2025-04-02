import inspect
from querys.ws_unidades_embrapii.srinfo_unit import srinfo_unit

def ws_unidades_embrapii():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_unit()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")