from qim_ues.scripts_public.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from qim_ues.scripts_public.webdriver import configurar_webdriver
from qim_ues.scripts_public.baixar_dados_srinfo import baixar_dados_srinfo
from qim_ues.scripts_public.manipulacoes import pa_qim, resultados
from qim_ues.scripts_public.levar_arquivos_sharepoint import levar_arquivos_sharepoint
import inspect


def qim_ues():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # buscando os valores existentes no SharePoint
    buscar_arquivos_sharepoint()
    
    # baixando os valores do SRInfo
    driver = configurar_webdriver()
    baixar_dados_srinfo(driver)

    # manipulando os valores para obter planilhas finais
    pa, today = pa_qim()
    resultados(pa, today)

    # levando planilhas para sharepoint
    levar_arquivos_sharepoint()

    print("🟢 " + inspect.currentframe().f_code.co_name)

if __name__ == "__main__":
    qim_ues()