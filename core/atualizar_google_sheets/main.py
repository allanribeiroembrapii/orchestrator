import os
from dotenv import load_dotenv
from puxar_planilhas_sharepoint import puxar_planilhas
from atualizacao_gsheet import atualizar_gsheet

# carregar .env 
load_dotenv()
ROOT = os.getenv('ROOT')
PORTFOLIO = os.path.abspath(os.path.join(ROOT, 'inputs', 'portfolio.xlsx'))#
PROJETOS_EMPRESAS = os.path.abspath(os.path.join(ROOT, 'inputs', 'projetos_empresas.xlsx'))#
INFORMACOES_EMPRESAS = os.path.abspath(os.path.join(ROOT, 'inputs', 'informacoes_empresas.xlsx'))
INFO_UNIDADES_EMBRAPII = os.path.abspath(os.path.join(ROOT, 'inputs', 'info_unidades_embrapii.xlsx'))
UE_LINHAS_ATUACAO = os.path.abspath(os.path.join(ROOT, 'inputs', 'ue_linhas_atuacao.xlsx'))
MACROENTREGAS = os.path.abspath(os.path.join(ROOT, 'inputs', 'macroentregas.xlsx'))
NEGOCIACOES = os.path.abspath(os.path.join(ROOT, 'inputs', 'negociacoes_negociacoes.xlsx'))
CLASSIFICACAO_PROJETO = os.path.abspath(os.path.join(ROOT, 'inputs', 'classificacao_projeto.xlsx'))
PROJETOS = os.path.abspath(os.path.join(ROOT, 'inputs', 'projetos.xlsx'))
PROSPECCOES = os.path.abspath(os.path.join(ROOT, 'inputs', 'prospeccao_prospeccao.xlsx'))
CNAE_IBGE = os.path.abspath(os.path.join(ROOT, 'inputs', 'cnae_ibge.xlsx'))
PEDIDOS_PI = os.path.abspath(os.path.join(ROOT, 'inputs', 'pedidos_pi.xlsx'))

def main():
    puxar_planilhas()
    url = "https://docs.google.com/spreadsheets/d/1x7IUvZnXg2MH2k3QE9Kiq-_Db4eA-2xwFGuswbTDYjg/edit?usp=sharing"
    abas = {'raw_portfolio': PORTFOLIO, 
            'raw_projetos_empresas': PROJETOS_EMPRESAS,
            'raw_informacoes_empresas': INFORMACOES_EMPRESAS,
            'raw_info_unidades_embrapii': INFO_UNIDADES_EMBRAPII,
            'raw_ue_linhas_atuacao': UE_LINHAS_ATUACAO,
            'raw_macroentregas': MACROENTREGAS,
            'raw_negociacoes_negociacoes': NEGOCIACOES,
            'raw_classificacao_projetos': CLASSIFICACAO_PROJETO,
            'raw_projetos': PROJETOS,
            'raw_prospeccao_prospeccao': PROSPECCOES,
            'raw_cnae_ibge': CNAE_IBGE,
            'raw_pedidos_pi': PEDIDOS_PI}
    print("🟡 atualizar_gsheet")
    for aba, caminho_arquivo in abas.items():
        atualizar_gsheet(url, aba, caminho_arquivo)
    print("🟢 atualizar_gsheet")
    

if __name__ == "__main__":
    main()
