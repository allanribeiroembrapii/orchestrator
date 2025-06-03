import os
import sys
from dotenv import load_dotenv
from core.atualizar_google_sheets.puxar_planilhas_sharepoint import puxar_planilhas
from core.atualizar_google_sheets.atualizacao_gsheet import atualizar_gsheet

# Adicionar o caminho do diretório raiz ao sys.path para importar o logger
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

# carregar .env
load_dotenv()
ROOT = os.getenv("ROOT_GSHET")
if not ROOT:
    ROOT = current_dir

# Verificar e criar diretório de inputs se não existir
inputs_dir = os.path.join(ROOT, "inputs")
if not os.path.exists(inputs_dir):
    os.makedirs(inputs_dir)

PORTFOLIO = os.path.abspath(os.path.join(ROOT, "inputs", "portfolio.xlsx"))
PROJETOS_EMPRESAS = os.path.abspath(
    os.path.join(ROOT, "inputs", "projetos_empresas.xlsx")
)
INFORMACOES_EMPRESAS = os.path.abspath(
    os.path.join(ROOT, "inputs", "informacoes_empresas.xlsx")
)
INFO_UNIDADES_EMBRAPII = os.path.abspath(
    os.path.join(ROOT, "inputs", "info_unidades_embrapii.xlsx")
)
UE_LINHAS_ATUACAO = os.path.abspath(
    os.path.join(ROOT, "inputs", "ue_linhas_atuacao.xlsx")
)
MACROENTREGAS = os.path.abspath(os.path.join(ROOT, "inputs", "macroentregas.xlsx"))
NEGOCIACOES = os.path.abspath(
    os.path.join(ROOT, "inputs", "negociacoes_negociacoes.xlsx")
)
CLASSIFICACAO_PROJETO = os.path.abspath(
    os.path.join(ROOT, "inputs", "classificacao_projeto.xlsx")
)
PROJETOS = os.path.abspath(os.path.join(ROOT, "inputs", "projetos.xlsx"))
PROSPECCOES = os.path.abspath(
    os.path.join(ROOT, "inputs", "prospeccao_prospeccao.xlsx")
)
CNAE_IBGE = os.path.abspath(os.path.join(ROOT, "inputs", "cnae_ibge.xlsx"))
PEDIDOS_PI = os.path.abspath(os.path.join(ROOT, "inputs", "pedidos_pi.xlsx"))
PROPOSTAS_TECNICAS = os.path.abspath(os.path.join(ROOT, "inputs", "negociacoes_propostas_tecnicas.xlsx"))
QIM_UES = os.path.abspath(os.path.join(ROOT, "inputs", "qim.xlsx"))


def main():

    try:
        # Puxar planilhas do SharePoint
        puxar_planilhas()

        # Atualizar Google Sheets
        url = "https://docs.google.com/spreadsheets/d/1x7IUvZnXg2MH2k3QE9Kiq-_Db4eA-2xwFGuswbTDYjg/edit?usp=sharing"
        abas = {
            "raw_portfolio": PORTFOLIO,
            "raw_projetos_empresas": PROJETOS_EMPRESAS,
            "raw_informacoes_empresas": INFORMACOES_EMPRESAS,
            "raw_info_unidades_embrapii": INFO_UNIDADES_EMBRAPII,
            "raw_ue_linhas_atuacao": UE_LINHAS_ATUACAO,
            "raw_macroentregas": MACROENTREGAS,
            "raw_negociacoes_negociacoes": NEGOCIACOES,
            "raw_classificacao_projetos": CLASSIFICACAO_PROJETO,
            "raw_projetos": PROJETOS,
            "raw_prospeccao_prospeccao": PROSPECCOES,
            "raw_cnae_ibge": CNAE_IBGE,
            "raw_pedidos_pi": PEDIDOS_PI,
            "raw_negociacoes_propostas_tecnicas": PROPOSTAS_TECNICAS,
            "raw_qim_ues": QIM_UES,
        }

        for aba, caminho_arquivo in abas.items():
            try:
                atualizar_gsheet(url, aba, caminho_arquivo)
            except Exception as e:
                print(f"Erro ao atualizar aba {aba}: {str(e)}")


    except Exception as e:
        # Re-lançar a exceção para manter o comportamento original
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro na execução do módulo atualizar_google_sheets: {str(e)}")
        sys.exit(1)
