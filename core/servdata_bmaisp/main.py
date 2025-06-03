from core.servdata_bmaisp.connection.sharepoint import get_files_from_sharepoint, sharepoint_post
from core.servdata_bmaisp.start_clean import start_clean
import pandas as pd
from pathlib import Path
import win32com.client as win32
from datetime import datetime
import os
import inspect

BASE_DATA = Path(__file__).resolve().parent / 'data'

def gerar_planilhas():
    # Carrega o arquivo Excel
    df_classprojeto = pd.read_excel(BASE_DATA / 'step_1_data_raw' / 'classificacao_projeto.xlsx')
    df_classprojeto = df_classprojeto[['Código', 'Brasil Mais Produtivo']]
    lista_bmaisp = df_classprojeto[df_classprojeto['Brasil Mais Produtivo'] == 'Sim']['Código'].tolist()

    # PORTFÓLIO
    df_portfolio = pd.read_excel(BASE_DATA / 'step_1_data_raw' / 'portfolio.xlsx')    
    colunas_portfolio = [
        'codigo_projeto',
        'data_contrato',
        'status',
        'projeto',
        'titulo_publico',
        'descricao_publica',
        'tecnologia_habilitadora',
        'valor_embrapii',
        'valor_empresa',
        'valor_sebrae',
        'valor_unidade_embrapii',
        'data_extracao_dados'
    ]
    df_portfolio_bmaisp = df_portfolio[df_portfolio['codigo_projeto'].isin(lista_bmaisp)]
    df_portfolio_bmaisp = df_portfolio_bmaisp[colunas_portfolio]
    df_portfolio_bmaisp = df_portfolio_bmaisp[df_portfolio_bmaisp['status'] != 'Cancelado']
    df_portfolio_bmaisp.loc[df_portfolio_bmaisp['status'] == 'Atrasado', 'status'] = 'Em andamento'
    df_portfolio_bmaisp.to_excel(BASE_DATA / 'step_2_stage_area' / 'bmaisp_portfolio.xlsx', index=False)
    df_portfolio_naobmaisp = df_portfolio[~df_portfolio['codigo_projeto'].isin(lista_bmaisp)]
    df_portfolio_naobmaisp = df_portfolio_naobmaisp[colunas_portfolio]
    df_portfolio_naobmaisp['data_contrato'] = pd.to_datetime(df_portfolio_naobmaisp['data_contrato'], errors='coerce')
    df_portfolio_naobmaisp = df_portfolio_naobmaisp[df_portfolio_naobmaisp['data_contrato'] > pd.Timestamp('2023-10-31')]
    df_portfolio_naobmaisp.to_excel(BASE_DATA / 'step_3_data_processed' / 'naobmaisp_portfolio.xlsx', index=False)

    # PROJETOS EMPRESAS
    df_projetos_empresas = pd.read_excel(BASE_DATA / 'step_1_data_raw' / 'projetos_empresas.xlsx')   
    df_projetos_empresas = df_projetos_empresas[df_projetos_empresas['codigo_projeto'].isin(lista_bmaisp)]

    # EMPRESAS
    lista_empresas_bmaisp = df_projetos_empresas['cnpj'].dropna().unique().tolist()
    df_empresas = pd.read_excel(BASE_DATA / 'step_1_data_raw' / 'informacoes_empresas.xlsx')   
    df_cnae = pd.read_excel(BASE_DATA / 'step_1_data_raw' / 'cnae_ibge.xlsx')   
    df_empresas = df_empresas[df_empresas['cnpj'].isin(lista_empresas_bmaisp)]
    colunas_empresas = [
        'cnpj',
        'empresa',
        'uf',
        'municipio',
        'porte',
        'faixa_faturamento',
        'cnae_subclasse',
        # 'nome_secao',
        # 'nome_divisao',
    ]
    df_empresas = df_empresas[colunas_empresas]
    df_empresas = df_empresas.merge(
        df_cnae[['subclasse2', 'nome_secao', 'nome_divisao']],
        how='left',
        left_on='cnae_subclasse',
        right_on='subclasse2'
    ).drop(columns=['subclasse2'])
    df_empresas = df_empresas[df_empresas['porte'] != 'Grande']
    lista_empresas_final = df_empresas['cnpj'].dropna().unique().tolist()
    df_empresas.to_excel(BASE_DATA / 'step_2_stage_area' / 'bmaisp_empresas.xlsx', index=False )

    #PROJETOS EMPRESAS FINAL
    df_projetos_empresas = df_projetos_empresas[df_projetos_empresas['cnpj'].isin(lista_empresas_final)]
    df_projetos_empresas.to_excel(BASE_DATA / 'step_2_stage_area' / 'bmaisp_projetos_empresas.xlsx', index=False )

def juntar_planilhas():
    # Caminhos
    pasta_origem = BASE_DATA / 'step_2_stage_area'
    pasta_destino = BASE_DATA / 'step_3_data_processed'
    pasta_destino.mkdir(parents=True, exist_ok=True)


    # Arquivos e nomes das abas
    arquivos = {
        'bmaisp_portfolio': pasta_origem / 'bmaisp_portfolio.xlsx',
        'bmaisp_projetos_empresas': pasta_origem / 'bmaisp_projetos_empresas.xlsx',
        'bmaisp_empresas': pasta_origem / 'bmaisp_empresas.xlsx'
    }

    # Caminho do arquivo final
    caminho_saida = os.path.join(pasta_destino, 'bmaisp_embrapii.xlsx')

    # Escreve as planilhas em um único arquivo com múltiplas abas
    with pd.ExcelWriter(caminho_saida, engine='openpyxl') as writer:
        for aba, caminho in arquivos.items():
            df = pd.read_excel(caminho)
            df.to_excel(writer, sheet_name=aba, index=False)


def molde_email(dados, hoje):
    return f"""
    <div class="container">
        <div style="margin: 10px">
            <img src="https://imgur.com/V0Rj9tD.png" alt="Banner Brasil Mais Produtivo"
                style="max-width: 400px; width: 100%; height: auto; border-top-left-radius: 10px; border-top-right-radius: 10px;">
        </div>

        <div style="margin: 10px">
            <b>Resultados da última atualização: {hoje}</b>
            <ul>
                <li>Projetos: {dados['semana_projetos']}</li>
                <li>Empresas: {dados['semana_empresas']}</li>
                <li>Projetos Não B+P: {dados['semana_projetos_nao_bmaisp']}</li>
            </ul>
        </div>

        <div style="margin: 10px">
            <b>Resultados Totais (desde 11/2023)</b>
            <ul>
                <li>Projetos: {dados['total_projetos']}</li>
                <li>Empresas: {dados['total_empresas']}</li>
                <li>Projetos Não B+P: {dados['total_projetos_nao_bmaisp']}</li>
            </ul>
        </div>


        <div style="margin: 10px">
            <img src="https://imgur.com/iBZDIHM.png" alt="Banner Embrapii"
                style="max-width: 400px; width: 100%; height: auto; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
        </div>
    </div>
    """


def alerta_email():
    PASTA_STEP_1 = BASE_DATA / 'step_1_data_raw'
    PASTA_STEP_2 = BASE_DATA / 'step_2_stage_area'
    PASTA_STEP_3 = BASE_DATA / 'step_3_data_processed'

    # Leitura dos dados
    df_portfolio_antigo = pd.read_excel(PASTA_STEP_1 / 'bmaisp_embrapii.xlsx', sheet_name="bmaisp_portfolio")
    df_portfolio_novo = pd.read_excel(PASTA_STEP_2 / 'bmaisp_portfolio.xlsx')

    df_empresas_antigo = pd.read_excel(PASTA_STEP_1 / 'bmaisp_embrapii.xlsx', sheet_name="bmaisp_empresas")
    df_empresas = pd.read_excel(PASTA_STEP_2 / 'bmaisp_projetos_empresas.xlsx')

    df_naobmaisp_antigo = pd.read_excel(PASTA_STEP_1 / 'naobmaisp_portfolio.xlsx')
    df_naobmaisp_novo = pd.read_excel(PASTA_STEP_3 / 'naobmaisp_portfolio.xlsx')

    # Projetos BMAISP
    total_projetos = df_portfolio_novo['codigo_projeto'].nunique()
    total_projetos_antigo = df_portfolio_antigo['codigo_projeto'].nunique()
    semana_projetos = total_projetos - total_projetos_antigo

    # Empresas BMAISP
    total_empresas = df_empresas['cnpj'].nunique()
    total_empresas_antigo = df_empresas_antigo['cnpj'].nunique()
    semana_empresas = total_empresas - total_empresas_antigo

    # Projetos NÃO BMAISP
    total_naobmaisp = df_naobmaisp_novo['codigo_projeto'].nunique()
    total_naobmaisp_antigo = df_naobmaisp_antigo['codigo_projeto'].nunique()
    semana_naobmaisp = total_naobmaisp - total_naobmaisp_antigo

    # Dados finais para o email
    dados = {
        'semana_projetos': semana_projetos,
        'semana_empresas': semana_empresas,
        'semana_projetos_nao_bmaisp': semana_naobmaisp,
        'total_projetos': total_projetos,
        'total_empresas': total_empresas,
        'total_projetos_nao_bmaisp': total_naobmaisp,
    }

    data_formatada = datetime.today().strftime('%d/%m/%Y')
    # Gera HTML e envia
    html = molde_email(dados, data_formatada)
    enviar_email(html)



def enviar_email(html):
    print("🟡 " + inspect.currentframe().f_code.co_name)
    destinatarios = [
        "allan.ribeiro@embrapii.org.br",
        "rafael.wandrey@embrapii.org.br",
        "milena.goncalves@embrapii.org.br",
        "nicolas.rodrigues@embrapii.org.br",
        "emanoel.querette@embrapii.org.br"
    ]

    anexos = [
        BASE_DATA / 'step_3_data_processed' / 'bmaisp_embrapii.xlsx',
        BASE_DATA / 'step_3_data_processed' / 'naobmaisp_portfolio.xlsx'
    ]


    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = ";".join(destinatarios)
    mail.Subject = "🤖 - Brasil Mais Produtivo | Alerta de Atualização"
    mail.HTMLBody = html
    for anexo in anexos:
        caminho_absoluto = os.path.abspath(anexo)
        if os.path.exists(caminho_absoluto):
            mail.Attachments.Add(caminho_absoluto)
        else:
            print(f"⚠️ Anexo não encontrado: {caminho_absoluto}")
    mail.Send()
    print("🟢 " + inspect.currentframe().f_code.co_name)

def main_bmaisp():

    #Start clean
    start_clean()

    #Get files
    get_files_from_sharepoint()

    #bmaisp
    gerar_planilhas()
    juntar_planilhas()

    #levar arquivos
    sharepoint_post()

    #enviar email
    alerta_email()

if __name__ == "__main__":
    main_bmaisp()
