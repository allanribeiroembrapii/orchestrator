import inspect
from querys.ws_projetos_modelo_embrapii.srinfo_project_contract import srinfo_project_contract


def ws_projetos_modelo_embrapii():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_project_contract()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")