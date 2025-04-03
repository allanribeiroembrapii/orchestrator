import inspect
from querys.ws_empresas.srinfo_company_company import srinfo_company_company

def ws_empresas():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_company_company()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")