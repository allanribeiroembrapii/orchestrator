import os
import sys
import pandas as pd
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#sys.path
SCRIPTS_PUBLIC = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
STEP1 = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw'))
STEP2 = os.path.abspath(os.path.join(ROOT, 'step_2_stage_area'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))
sys.path.append(SCRIPTS_PUBLIC)

from processar_excel import processar_excel

# Definindo as categorias de porte e fonte
def classificar_porte(porte):
    if porte in ["Grande", "Média"]:
        return "empresas_maior_porte"
    elif porte in ["Pequena", "Microempresa"]:
        return "empresas_menor_porte"
    else:
        return "empresas_menor_porte"
    
def classificar_fonte(fonte):
    if fonte in ["EMBRAPII"]:
        return "valor_embrapii2"
    elif fonte in ["Unidade EMBRAPII"]:
        return "valor_unidade_embrapii2"
    elif fonte in ["SEBRAE"]:
        return "valor_sebrae2"
    elif fonte in ["Empresa"]:
        return "valor_empresa2_nao_sebrae"
    elif fonte in ["Micro e Pequena Empresa"]:
        return "valor_micro_pequena_empresa"
    elif fonte in ["Média e Grande Empresa"]:
        return "valor_media_grande_empresa"
    else:
        return "outra_fonte"

# Gerando a planilha geral
def gerando_planilha():

    # lendo as planilhas
    port = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'portfolio.xlsx')))
    proj_emp = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'projetos_empresas.xlsx')))
    emp = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'informacoes_empresas.xlsx')))
    ppi = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'pedidos_pi.xlsx')))
    me = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'macroentregas.xlsx')))
    source = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'srinfo_sebrae_sourceamount.xlsx')))

    ## COLUNAS CALCULADAS

    # valor_total
    port['valor_total'] = port['valor_embrapii'] + port['valor_empresa'] + port['valor_unidade_embrapii'] + port['valor_sebrae']

    # pedidos_pi
    contagem_ppi = ppi.groupby('codigo_projeto').size().reset_index(name = 'pedidos_pi')
    port_pedidos = pd.merge(port, contagem_ppi, on = 'codigo_projeto', how = 'left')

    # macroentregas
    contagem_mes = me.groupby('codigo_projeto').size().reset_index(name = 'num_macroentregas')
    port_mes = pd.merge(port_pedidos, contagem_mes, on = 'codigo_projeto', how = 'left')

    # numero de MPEs e MGEs
    # juntando projetos_empresas e informacoes_empresas
    combinado = pd.merge(proj_emp, emp, on = 'cnpj', how = 'left')
    # contando numero de empresas por porte em cada projeto
    contagem_empresas = combinado.groupby(['codigo_projeto', 'porte']).size().reset_index(name = 'num_empresas')
    contagem_empresas["categoria"] = contagem_empresas["porte"].apply(classificar_porte)
    contagem_empresas = contagem_empresas.groupby(['codigo_projeto', 'categoria'])['num_empresas'].sum().unstack(fill_value=0).reset_index()
    port_empresas = pd.merge(port_mes, contagem_empresas, on = 'codigo_projeto', how = 'left')

    # valores por fonte (MPEs, MGEs, SEBRAE, EMBRAPII, Unidade EMBRAPII)
    source["categoria"] = source["fonte"].apply(classificar_fonte)
    source_grouped = source.groupby(['codigo_negociacao', 'categoria'])['valor'].sum().unstack(fill_value=0).reset_index()
    port_fonte = pd.merge(port_empresas, source_grouped, on = 'codigo_negociacao', how = 'left')

    # filtrando apenas os projetos SEBRAE
    planilha_geral = port_fonte[port_fonte['parceria_programa'].str.contains('SEBRAE')]

    # salvando a planilha em step_2_stage_area
    planilha_geral.to_excel(os.path.abspath(os.path.join(STEP2, 'planilha_geral.xlsx')), index = False)

# Processando a planilha geral
def processar_BD_portfolio():
    # Definições dos caminhos e nome do arquivo
    origem = os.path.join(ROOT, 'step_2_stage_area')
    destino = os.path.join(ROOT, 'step_3_data_processed')
    nome_arquivo = "planilha_geral.xlsx"
    arquivo_origem = os.path.join(origem, nome_arquivo)
    arquivo_destino = os.path.join(destino, 'BD_portfolio.xlsx')

    # Campos de interesse e novos nomes das colunas
    campos_interesse = [
        'codigo_projeto',
        'codigo_negociacao',
        'unidade_embrapii',
        'data_contrato',
        'valor_total',
        'titulo_publico',
        'descricao_publica',
        'tipo_projeto',
        'tecnologia_habilitadora',
        'macroentregas',
        'num_macroentregas',
        'status',
        'pct_aceites',
        'trl_inicial',
        'trl_final',
        'valor_unidade_embrapii',
        'valor_micro_pequena_empresa',
        'valor_media_grande_empresa',
        'valor_sebrae',
        'valor_embrapii',
        'modalidade_financiamento',
        'empresas_menor_porte',
        'empresas_maior_porte',
        'pedidos_pi',
    ]

    novos_nomes_e_ordem = {
        'codigo_projeto': 'codigo_projeto',
        'codigo_negociacao': 'codigo_negociacao',
        'unidade_embrapii': 'unidade_embrapii',
        'data_contrato': 'data_contrato',
        'valor_total': 'valor_total',
        'titulo_publico': 'titulo_publico',
        'descricao_publica': 'descricao_publica',
        'tipo_projeto': 'tipo_projeto',
        'tecnologia_habilitadora': 'tecnologia_habilitadora',
        'macroentregas': 'macroentregas_contratos',
        'num_macroentregas': 'num_macroentregas_me',
        'status': 'status',
        'pct_aceites': 'percentual_projeto',
        'trl_inicial': 'trl_inicial',
        'trl_final': 'trl_final',
        'valor_unidade_embrapii': 'valor_unidade_embrapii',
        'valor_micro_pequena_empresa': 'valor_micro_pequena_empresa',
        'valor_media_grande_empresa': 'valor_media_grande_empresa',
        'valor_sebrae': 'valor_sebrae',
        'valor_embrapii': 'valor_embrapii',
        'modalidade_financiamento': 'modalidade_financiamento',
        'empresas_menor_porte': 'empresas_menor_porte',
        'empresas_maior_porte': 'empresas_maior_porte',
        'pedidos_pi': 'pedidos_pi',
    }

    # Campos de data e valor
    campos_data = ['data_contrato']
    campos_valor = ['valor_total', 'valor_unidade_embrapii', 'valor_micro_pequena_empresa', 'valor_media_grande_empresa', 'valor_sebrae', 'valor_embrapii']

    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)