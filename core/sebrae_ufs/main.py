from scripts.connect_vpn import connect_vpn, disconnect_vpn
from scripts.srinfo_sebrae_sourceamount import srinfo_sebrae_sourceamount
from scripts.srinfo_ue_unit import srinfo_ue_unit
from scripts.srinfo_company import srinfo_company
from scripts.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from scripts.apagar_arquivos_pasta import apagar_arquivos_pasta
from scripts.gerar_planilha_geral import gerar_planilha_geral, gerar_planilha_erros
from scripts.gerar_planilhas_ufs import gerar_planilhas_uf
from office365_api.upload_files import upload_files
import os
from dotenv import load_dotenv

load_dotenv()
ROOT = os.getenv('ROOT')
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))


def main():
    # Carregar arquivos do SharePoint
    print("Passo 1/4: Buscando arquivos do SharePoint")
    buscar_arquivos_sharepoint(gerar_novo=False)

    # Consulta clickhouse
    print("Passo 2/4: Consultando valores por fonte no ClickHouse")
    connect_vpn()
    srinfo_sebrae_sourceamount()
    srinfo_ue_unit()
    srinfo_company()
    disconnect_vpn()
    upload_files(STEP3, 'dw_pii')
    apagar_arquivos_pasta(STEP3)

    # # Gerando planilhas
    print("Passo 3/4: Gerando planilhas")
    planilha_geral, combinado, municipios, port_ue, proj_emp, port_emp, port_me = gerar_planilha_geral(gerar_novo=False, enviar_pasta_sebrae=False)
    gerar_planilha_erros(planilha_geral)
    gerar_planilhas_uf(planilha_geral, combinado, municipios, port_ue, proj_emp, port_emp, port_me, gerar_novo=False, enviar_pasta_sebrae=False)

    # Levando arquivos para o SharePoint
    print("Passo 4/4: Levando planilhas para o SharePoint")
    upload_files(STEP3, 'DWPII/sebrae_ufs')

if __name__ == "__main__":
    main()