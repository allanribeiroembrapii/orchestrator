import inspect
from querys.ws_unidades_embrapii.srinfo_unit import srinfo_unit
from querys.ws_unidades_embrapii.anexo8 import anexo8

def ws_unidades_embrapii():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_unit()
        anexo8(por_unidade = True, por_projeto = True, por_mes = True,
               mes_especifico = None, ano_especifico = None, tirar_desqualificados = True)

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")