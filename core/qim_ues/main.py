from core.scripts_public.buscar_arquivos_sharepoint_qim import (
    buscar_arquivos_sharepoint_qim,
)
from core.scripts_public.webdriver import configurar_webdriver
from core.scripts_public.baixar_dados_srinfo_qim import baixar_dados_srinfo_qim
from core.scripts_public.manipulacoes_qim import pa_qim, resultados
from core.scripts_public.levar_arquivos_sharepoint_qim import (
    levar_arquivos_sharepoint_qim,
)


def qim_ues(buscar=False, baixar=False, manipular=False, levar=False):
    # buscando os valores existentes no SharePoint
    if buscar:
        buscar_arquivos_sharepoint_qim()
    # baixando os valores do SRInfo
    if baixar:
        driver = configurar_webdriver()
        baixar_dados_srinfo_qim(driver)

    # manipulando os valores para obter planilhas finais
    if manipular:
        pa, today = pa_qim()
        resultados(pa, today)

    # levando planilhas para sharepoint
    if levar:
        levar_arquivos_sharepoint_qim()


if __name__ == "__main__":
    qim_ues(buscar=True, baixar=True, manipular=True, levar=True)
