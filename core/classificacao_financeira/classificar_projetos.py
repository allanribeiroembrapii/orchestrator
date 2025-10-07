import pandas as pd
from dotenv import load_dotenv
import os
import inspect
import win32com.client as win32

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_CLASSIFICACAO_FINANCEIRA")
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")
PORTFOLIO = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'portfolio.xlsx'))
PORTFOLIO2 = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'portfolio2.xlsx'))
AGFIN_PROJETOS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'agfin_projetos_modelo_tradicional_classificacao_financeira.xlsx'))
AGFIN_REFERENCIA = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, '[GEPES25-038] Agenda de Dados Financeiros - Base Ouro.xlsx'))
PORTFOLIO_STAGE_AREA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'portfolio_stage_area.xlsx'))
NOVOS_PROJETOS_TAGS = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'novos_projetos_tags.xlsx'))
AGFIN_PROJETOS_PROCESSED = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, 'agfin_projetos_modelo_tradicional_classificacao_financeira.xlsx'))

def classificar_projetos():
    # Ler os DataFrames
    df_portfolio = pd.read_excel(PORTFOLIO)
    df_portfolio2 = pd.read_excel(PORTFOLIO2)
    df_portfolio_tags = df_portfolio2[['id_codigo_projeto', 'fin_parceiro', 'outros_tags']].copy()
    df_agfin_projetos = pd.read_excel(AGFIN_PROJETOS)
    df_agfin_referencia = pd.read_excel(AGFIN_REFERENCIA, sheet_name='referencia_class_projetos')
    df_fonte_prioritaria = pd.read_excel(AGFIN_REFERENCIA, sheet_name='unidades_prioritarias')

    # Encontrar os códigos de projetos que estão em df_portfolio mas não estão em df_agfin_projetos
    codigos_agfin_projetos = df_agfin_projetos['codigo_projeto'].astype(str).unique()
    codigos_novos = df_portfolio[~df_portfolio['codigo_projeto'].astype(str).isin(codigos_agfin_projetos)]['codigo_projeto']

    # Filtrar apenas os novos projetos no df_portfolio
    df_novos_projetos = df_portfolio[df_portfolio['codigo_projeto'].astype(str).isin(codigos_novos.astype(str))]
    
    # Manter somente as colunas desejadas
    colunas_desejadas = ['codigo_projeto', 'unidade_embrapii', 'parceria_programa', 'call', 'cooperacao_internacional', 'modalidade_financiamento', 'tags']
    df_novos_projetos = df_novos_projetos[colunas_desejadas]

    # Criar a coluna de concatenação dos parâmetros
    df_novos_projetos['srinfo_parametros_concatenados'] = (
        df_novos_projetos['parceria_programa'].fillna('') +
        df_novos_projetos['call'].fillna('') +
        df_novos_projetos['modalidade_financiamento'].fillna('')
    )
    df_novos_projetos = df_novos_projetos[['codigo_projeto', 'srinfo_parametros_concatenados', 'unidade_embrapii']]

    # trazer colunas
    df_novos_projetos = df_novos_projetos.merge(
    df_agfin_referencia[
            [
                'srinfo_parametros_concatenados',
                'ncf_aporte_embrapii_macro_contrato',
                'ncf_aporte_embrapii_contrato',
                'ncf_aporte_embrapii_contrato_eixo',
                'ncf_aporte_embrapii_eixo_regra',
                'ncf_sebrae',
                'ncf_sebrae_macro_contrato',
                'ncf_sebrae_contrato',
                'ncf_sebrae_contrato_eixo',
                'ncf_sebrae_eixo_regra',
                'ncf_sebrae_eixo_regra2',
                'id_parceiro',
                'parceiro'
            ]
        ],
        on='srinfo_parametros_concatenados',
        how='left'
    )
    df_novos_projetos.to_excel(PORTFOLIO_STAGE_AREA, index=False)


    alterar_nome_colunas = {
        'ncf_aporte_embrapii_macro_contrato': 'macro_contrato',
        'ncf_aporte_embrapii_contrato': 'contrato',
        'ncf_aporte_embrapii_contrato_eixo': 'contrato_eixo',
        'ncf_aporte_embrapii_eixo_regra': 'contrato_eixo_regra',
        'ncf_sebrae': 'sebrae',
        'ncf_sebrae_macro_contrato': 'sebrae_macro_contrato',
        'ncf_sebrae_contrato': 'sebrae_contrato',
        'ncf_sebrae_contrato_eixo': 'sebrae_contrato_eixo',
        'ncf_sebrae_eixo_regra': 'sebrae_eixo_regra',
        'ncf_sebrae_eixo_regra2': 'sebrae_eixo_regra2'
    }
    df_novos_projetos = df_novos_projetos.rename(columns=alterar_nome_colunas)
    df_agfin_projetos = pd.concat([df_agfin_projetos, df_novos_projetos], ignore_index=True)

    #Parceiro CG
    # Filtrar índices onde id_parceiro está vazio
    indices_sem_parceiro = df_agfin_projetos[df_agfin_projetos['id_parceiro'].isnull()].index

    # Criar dataframe temporário mantendo o índice original
    df_temp = df_agfin_projetos.loc[indices_sem_parceiro].merge(
        df_fonte_prioritaria[['unidade_embrapii', 'id_parceiro', 'parceiro', 'contrato_eixo']],
        on='unidade_embrapii',
        how='left',
        suffixes=('', '_novo')
    )

    # Garantir alinhamento: usar o índice original
    df_agfin_projetos.loc[indices_sem_parceiro, 'id_parceiro'] = df_temp['id_parceiro_novo'].values
    df_agfin_projetos.loc[indices_sem_parceiro, 'parceiro'] = df_temp['parceiro_novo'].values
    df_agfin_projetos.loc[indices_sem_parceiro, 'contrato_eixo'] = df_temp['contrato_eixo_novo'].values

    # Projetos MS
    codigos_ms = df_portfolio_tags[
        df_portfolio_tags['outros_tags'].str.contains('Ministério da Saúde', na=False)
    ][['id_codigo_projeto', 'fin_parceiro']].copy()
    codigos_ms = codigos_ms[codigos_ms['fin_parceiro'] != 'MS']
    df_agfin_projetos.loc[
        df_agfin_projetos['codigo_projeto'].astype(str).isin(codigos_ms['id_codigo_projeto'].astype(str)),
        ['id_parceiro', 'parceiro', 'contrato_eixo']
    ] = [5, 'MS', 'Saúde']

    df_agfin_projetos = df_agfin_projetos.drop(columns=['srinfo_parametros_concatenados', 'unidade_embrapii'])

    # Verificar se foi criada nova classificação no SRInfo
    projetos_sem_classificacao = df_agfin_projetos['macro_contrato'].isnull().sum()
    if projetos_sem_classificacao > 0:
        enviar_email(projetos_sem_classificacao)

    df_agfin_projetos.to_excel(AGFIN_PROJETOS_PROCESSED, index=False)


def enviar_email(projetos):
    print("🟡 " + inspect.currentframe().f_code.co_name)
    destinatarios = [
        "allan.ribeiro@embrapii.org.br",
        "nicolas.rodrigues@embrapii.org.br",
        "milena.goncalves@embrapii.org.br",
    ]

    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = ";".join(destinatarios)
    mail.Subject = "🤖 - Classificação Financeira | Nova Classificação"
    mail.HTMLBody = f'Projetos Sem Classificação Financeira: {projetos}'
    mail.Send()
    print("🟢 " + inspect.currentframe().f_code.co_name)