import os
from dotenv import load_dotenv
import inspect
from core.atualizar_google_sheets.office365.download_files import get_file
from core.atualizar_google_sheets.connect_sharepoint import SharepointClient


# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_GSHEET")


# puxar planilhas do sharepoint
def puxar_planilhas():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    inputs = os.path.join(ROOT, "inputs")
    os.makedirs(inputs, exist_ok=True)
    apagar_arquivos_pasta(inputs)

    sp = SharepointClient()

    pasta_srinfo = "DWPII/srinfo"
    pasta_qim_ues = "DWPII/qim_ues"
    pasta_lookup = "DWPII/lookup_tables"
    pasta_dw_pii = "dw_pii"

    lista_arquivos = {
        pasta_srinfo: {
            "portfolio",
            "projetos_empresas",
            "informacoes_empresas",
            "info_unidades_embrapii",
            "pedidos_pi",
            "ue_linhas_atuacao",
            "macroentregas",
            "negociacoes_negociacoes",
            "classificacao_projeto",
            "projetos",
            "prospeccao_prospeccao",
            "negociacoes_propostas_tecnicas",
            "equipe_ue",
            "estudantes",
            "funil",
        },
        pasta_qim_ues: {
            "qim",
        },
        pasta_lookup: {
            "cnae_ibge",
        },
        pasta_dw_pii: {
            "portfolio2",
        }
    }

    lista_embrapii_raw = {
        pasta_srinfo: {
            "funil",
        }
    }

    baixar_arquivos(sp, lista_arquivos, inputs)
    baixar_arquivos(sp, lista_embrapii_raw, inputs)

    print("🟢 " + inspect.currentframe().f_code.co_name)

def baixar_arquivos(sp, lista, inputs):
    for pasta, nomes in lista.items():
        for nome in nomes:
            filename = f"{nome}.xlsx"
            remote_path = f"{pasta}/{filename}"
            local_file = os.path.join(inputs, filename)
            print(f"⬇️  Baixando: {remote_path} -> {local_file}")
            sp.download_file(remote_path, local_file)



def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é uma pasta; se não for, cria
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            return

        # Lista todos os arquivos na pasta
        arquivos = os.listdir(caminho_pasta)

        # Apaga cada arquivo na pasta
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
    except Exception as e:
        print(f"🔴 Ocorreu um erro ao apagar os arquivos: {e}")

