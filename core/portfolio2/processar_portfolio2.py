import pandas as pd
from dotenv import load_dotenv
import os
import inspect
import win32com.client as win32

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv("ROOT_PORTFOLIO2")
SHAREPOINT_SITE = os.getenv("sharepoint_url_site")
SHAREPOINT_SITE_NAME = os.getenv("sharepoint_site_name")
SHAREPOINT_DOC = os.getenv("sharepoint_doc_library")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")
PORTFOLIO = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'portfolio.xlsx'))
MACROENTREGAS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'macroentregas.xlsx'))
NEGOCIACOES = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'negociacoes_negociacoes.xlsx'))
AGFIN_PROJETOS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'agfin_projetos_modelo_tradicional_classificacao_financeira.xlsx'))
PORTFOLIO2 = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, 'portfolio2.xlsx'))
MACROENTREGAS_AGREGADAS = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'macroentregas_agregadas.xlsx'))
NEGOCIACOES_AGREGADAS = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'negociacoes_agregadas.xlsx'))

def processar_portfolio2():

    ajustar_negociacoes()
    ajustar_macroentregas()
    
    # Ler os arquivos
    df_portfolio = pd.read_excel(PORTFOLIO)
    df_agfin_projetos = pd.read_excel(AGFIN_PROJETOS)
    df_negociacoes_agregadas = pd.read_excel(NEGOCIACOES_AGREGADAS)
    df_macroentregas_agregadas = pd.read_excel(MACROENTREGAS_AGREGADAS)

    # Merge entre os dois DataFrames (tipo left join, para agregar as colunas financeiras ao portfolio)
    df_novo_portfolio = df_portfolio.merge(
        df_agfin_projetos,
        left_on='codigo_projeto',
        right_on='codigo_projeto',
        how='left',
    )

    # Merge Negociações
    df_novo_portfolio = df_novo_portfolio.merge(
        df_negociacoes_agregadas,
        left_on='codigo_projeto',
        right_on='codigo_projeto',
        how='left',
    )

    # Merge Macroentregas
    df_novo_portfolio = df_novo_portfolio.merge(
        df_macroentregas_agregadas,
        left_on='codigo_projeto',
        right_on='codigo_projeto',
        how='left',
    )

    # Criar a coluna val_nominal_total (soma dos valores financeiros)
    df_novo_portfolio['val_nominal_total'] = (
        df_novo_portfolio['valor_embrapii'].fillna(0) +
        df_novo_portfolio['valor_empresa'].fillna(0) +
        df_novo_portfolio['valor_sebrae'].fillna(0) +
        df_novo_portfolio['valor_unidade_embrapii'].fillna(0)
    )

    #alterar o nome e a ordem das colunas -> seguir o apresentado em:
    nome_ordem_colunas = {
        'codigo_projeto': 'id_codigo_projeto',
        'projeto_rede': 'rede_projeto_codigo',
        'projeto_rede_papel': 'rede_projeto_papel_ue',
        'status': 'st_status_projeto',
        'codigo_negociacao': 'negociacao_id',
        '_negociacao': 'negociacao_negociacao',
        'data_prim_ver_prop_tec': 'dt_data_negociacao',
        'data_contrato': 'dt_data_projeto_contrato',
        'data_inicio': 'dt_data_projeto_inicio',
        'data_termino': 'dt_data_projeto_termino',
        'projeto': 'desc_projeto',
        'titulo': 'desc_titulo',
        'titulo_publico': 'desc_titulo_publico',
        'descricao_publica': 'desc_descricao_publica',
        'objetivo': 'desc_objetivo',
        'unidade_embrapii': 'ue_unidade_embrapii',
        'ue_status': 'ue_status',
        'ue_uf': 'ue_uf',
        'ue_tipo_instituicao': 'ue_tipo_instituicao',
        'ue_competencias_tecnicas': 'ue_competencias_tecnicas',
        'info_empresa': 'emp_empresas',
        'n_empresas': 'emp_n_empresas',
        'parceria_programa': 'fin_parceria_programa',
        'call': 'fin_call',
        'modalidade_financiamento': 'fin_modalidade_financiamento',
        'uso_recurso_obrigatorio': 'fin_uso_recurso',
        'id_parceiro': 'fin_parceiro_id',
        'parceiro': 'fin_parceiro',
        'contrato': 'fin_contrato',
        'contrato_eixo': 'fin_contrato_eixo',
        'contrato_eixo_regra': 'fin_contrato_eixo_regra',
        'macro_contrato': 'fin_macrocontrato',
        'sebrae': 'fin_sebrae',
        'sebrae_contrato': 'fin_sebrae_contrato',
        'sebrae_contrato_eixo': 'fin_sebrae_contrato_eixo',
        'sebrae_eixo_regra': 'fin_sebrae_eixo_regra',
        'sebrae_eixo_regra2': 'fin_sebrae_eixo_regra2',
        'sebrae_macro_contrato': 'fin_sebrae_macrocontrato',
        'tipo_projeto': 'class_tipo_projeto',
        'trl_inicial': 'class_trl_inicial',
        'trl_final': 'class_trl_final',
        'area_aplicacao': 'class_area_aplicacao',
        'tecnologia_habilitadora': 'class_tecnologia_habilitadora',
        'missoes_cndi': 'class_nib',
        'brasil_mais_produtivo': 'class_bmaisp',
        'valor_embrapii': 'val_nominal_embrapii',
        'valor_empresa': 'val_nominal_empresa',
        'valor_sebrae': 'val_nominal_sebrae',
        'valor_unidade_embrapii': 'val_nominal_unidade',
        'val_nominal_total': 'val_nominal_total',
        '_ipca_valor_embrapii': 'val_ipca_embrapii',
        '_ipca_valor_empresa': 'val_ipca_empresa',
        '_ipca_valor_sebrae': 'val_ipca_sebrae',
        '_ipca_valor_total': 'val_ipca_total',
        '_ipca_valor_unidade_embrapii': 'val_ipca_unidade',
        'macroentregas': 'macroentrega_numero',
        'pct_aceites': 'macroentrega_aceites',
        '_macroentrega': 'macroentrega_macroentregas',
        'n_pedidos_pi': 'pi_numero_pedidos',
        'nota_avaliacao': 'aval_nota',
        'data_avaliacao': 'aval_data_avaliacao',
        'cooperacao_internacional': 'outros_cooperacao_internacional',
        'observacoes': 'outros_observacoes',
        'tags': 'outros_tags',
        'data_extracao_dados': 'outros_data_extracao',
    }

    # Aplicar o renomeio
    df_novo_portfolio = df_novo_portfolio.rename(columns=nome_ordem_colunas)

    # Reordenar as colunas seguindo a nova ordem definida
    nova_ordem = list(nome_ordem_colunas.values())
    df_novo_portfolio = df_novo_portfolio[nova_ordem]

    # Exportar
    df_novo_portfolio.to_excel(PORTFOLIO2, index=False)

def safe_format_date(col):
    return pd.to_datetime(col, errors='coerce').dt.strftime('%d/%m/%Y').fillna('')
    
def ajustar_macroentregas():
    # Ler os dados
    df_macroentregas = pd.read_excel(MACROENTREGAS)

    df_macroentregas['valor_total_me'] = (
        df_macroentregas['valor_embrapii_me'].fillna(0) +
        df_macroentregas['valor_empresa_me'].fillna(0) +
        df_macroentregas['valor_unidade_embrapii_me'].fillna(0)
    )

    # Criar a coluna '_macroentrega' replicando a concatenação da fórmula do Excel
    df_macroentregas['_macroentrega'] = (
        "[" +
        "codigo_projeto: " + df_macroentregas['codigo_projeto'].fillna('').astype(str) + "; " +
        "num_macroentrega: " + df_macroentregas['num_macroentrega'].fillna('').astype(str) + "; " +
        "titulo: " + df_macroentregas['titulo'].fillna('Não informado').astype(str) + "; " +
        "descricao_macroentrega: " + df_macroentregas['descricao_macroentrega'].fillna('Não informado').astype(str) + "; " +
        "valor_embrapii_me: " + df_macroentregas['valor_embrapii_me'].fillna(0).map('{:,.2f}'.format).str.replace('.', ',').str.replace(',', '.', 1) + "; " +
        "valor_empresa_me: " + df_macroentregas['valor_empresa_me'].fillna(0).map('{:,.2f}'.format).str.replace('.', ',').str.replace(',', '.', 1) + "; " +
        "valor_unidade_embrapii_me: " + df_macroentregas['valor_unidade_embrapii_me'].fillna(0).map('{:,.2f}'.format).str.replace('.', ',').str.replace(',', '.', 1) + "; " +
        "valor_total_me: " + df_macroentregas['valor_total_me'].fillna(0).map('{:,.2f}'.format).str.replace('.', ',').str.replace(',', '.', 1) + "; " +
        "data_inicio_planejado: " + safe_format_date(df_macroentregas['data_inicio_planejado']) + "; " +
        "data_termino_planejado: " + safe_format_date(df_macroentregas['data_termino_planejado']) + "; " +
        "data_inicio_real: " + safe_format_date(df_macroentregas['data_inicio_real']) + "; " +
        "data_termino_real: " + safe_format_date(df_macroentregas['data_termino_real']) + "; " +
        "versao: Não informado; " +
        "percentual_executado: " + df_macroentregas['percentual_executado'].fillna('').astype(str) + "; " +
        "me_atrasada: " + df_macroentregas['me_atrasada'].fillna('Não informado').astype(str) + "; " +
        "data_aceitacao: " + safe_format_date(df_macroentregas['data_aceitacao']) + "; " +
        "observacoes: " + df_macroentregas['observacoes'].fillna('Não informado').astype(str) +
        "]"
    )

    # Manter apenas as colunas desejadas
    df_macroentregas = df_macroentregas[['codigo_projeto', '_macroentrega']]

    # Agregar por código_projeto (concatenando as macroentregas separadas por pipe "|")
    df_macroentregas['_macroentrega'] = df_macroentregas['_macroentrega'].fillna('').astype(str)
    df_macroentregas_agregadas = df_macroentregas.groupby('codigo_projeto')['_macroentrega'].apply(lambda x: '; \n \n'.join(x)).reset_index()

    # Exportar
    df_macroentregas_agregadas.to_excel(MACROENTREGAS_AGREGADAS, index=False)

def ajustar_negociacoes():
    # Ler os dados
    df_negociacoes = pd.read_excel(NEGOCIACOES)

    # Criar a coluna _negociacao
    df_negociacoes['_negociacao'] = (
        "[" +
        "codigo_projeto: " + df_negociacoes['codigo_projeto'].fillna('').astype(str) + "; " +
        "codigo_negociacao: " + df_negociacoes['codigo_negociacao'].fillna('').astype(str) + "; " +
        "unidade_embrapii: " + df_negociacoes['unidade_embrapii'].fillna('Não informado').astype(str) + "; " +
        "parceria_programa: " + df_negociacoes['parceria_programa'].fillna('Não informado').astype(str) + "; " +
        "call: " + df_negociacoes['call'].fillna('').astype(str) + "; " +
        "cooperacao_internacional: " + df_negociacoes['cooperacao_internacional'].fillna('Não informado').astype(str) + "; " +
        "modalidade_financiamento: " + df_negociacoes['modalidade_financiamento'].fillna('Não informado').astype(str) + "; " +
        "data_prim_ver_prop_tec: " + safe_format_date(df_negociacoes['data_prim_ver_prop_tec']) + "; " +
        "valor_total_plano_trabalho: " + df_negociacoes['valor_total_plano_trabalho'].fillna(0).map('{:,.2f}'.format).str.replace('.', ',').str.replace(',', '.', 1) + "; " +
        "possibilidade_contratacao: " + df_negociacoes['possibilidade_contratacao'].fillna('Não informado').astype(str) + "; " +
        "status: " + df_negociacoes['status'].fillna('Não informado').astype(str) + "; " +
        "objetivos_prop_tec: " + df_negociacoes['objetivos_prop_tec'].fillna('Não informado').astype(str) + "; " +
        "ver_prop_tec: " + df_negociacoes['ver_prop_tec'].fillna('Não informado').astype(str) + "; " +
        "ver_plano_trabalho: " + df_negociacoes['ver_plano_trabalho'].fillna('Não informado').astype(str) + "; " +
        "observacoes: " + df_negociacoes['observacoes'].fillna('Sem observações.').astype(str) + 
        "]"
    )

    # Manter apenas as colunas desejadas
    df_negociacoes = df_negociacoes[['codigo_projeto', 'data_prim_ver_prop_tec', '_negociacao']]

    # Exportar
    df_negociacoes.to_excel(NEGOCIACOES_AGREGADAS, index=False)