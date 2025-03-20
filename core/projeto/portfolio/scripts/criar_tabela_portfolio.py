import os
import pandas as pd
from datetime import datetime
import numpy as np

def criar_tabela_portfolio():
    # Caminhos dos arquivos Excel
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    raw_projetos_path = os.path.join(base_dir, 'projeto', 'portfolio', 'step_1_data_raw', 'raw_projetos.xlsx')
    raw_contratos_path = os.path.join(base_dir, 'projeto', 'portfolio', 'step_1_data_raw', 'raw_contratos.xlsx')
    raw_classificacao_projeto_path = os.path.join(base_dir, 'projeto', 'portfolio', 'step_1_data_raw', 'raw_classificacao_projeto.xlsx')
    raw_relatorio_projetos_contratados_path = os.path.join(base_dir, 'projeto', 'portfolio', 'step_1_data_raw', 'raw_relatorio_projetos_contratados_1.xlsx')
    raw_sebrae_path = os.path.join(base_dir, 'projeto', 'portfolio', 'step_1_data_raw', 'raw_sebrae.xlsx')
    raw_sebrae_srinfo_path = os.path.join(base_dir, 'projeto', 'portfolio', 'step_1_data_raw', 'raw_sebrae_srinfo.xlsx')
    destino = os.path.join(base_dir, 'projeto', 'portfolio', 'step_3_data_processed')
    arquivo_destino = os.path.join(destino, 'portfolio.xlsx')

    # Ler os arquivos Excel
    df_projetos = pd.read_excel(raw_projetos_path)
    df_contratos = pd.read_excel(raw_contratos_path)
    df_classificacao_projeto = pd.read_excel(raw_classificacao_projeto_path)
    df_relatorio_projetos_contratados = pd.read_excel(raw_relatorio_projetos_contratados_path)
    df_sebrae = pd.read_excel(raw_sebrae_path)
    df_sebrae_srinfo = pd.read_excel(raw_sebrae_srinfo_path)

    # Escolher somente colunas desejadas sebrae
    df_sebrae = df_sebrae[['Código', 'Valor aportado SEBRAE', 'Valor aportado Empresa (SEBRAE)', 'Valor aportado pela Unidade', 'Valor aportado EMBRAPII']]
    df_sebrae = df_sebrae.rename(columns={'Valor aportado SEBRAE': 'valor_sebrae',
                                          'Valor aportado Empresa (SEBRAE)': 'valor_empresa',
                                          'Valor aportado pela Unidade': 'valor_unidade_embrapii',
                                          'Valor aportado EMBRAPII': 'valor_embrapii'})


    # juntar negociacao com valores sebrae para os que não estão na base do nicolas
    df_subset = df_relatorio_projetos_contratados[df_relatorio_projetos_contratados['Parcerias'].str.contains('SEBRAE', case=False, na=False)]
    df_comparacao = df_subset[~df_subset['Código'].isin(df_sebrae['Código'])]
    df_merge = df_comparacao.merge(df_sebrae_srinfo, left_on = 'Negociação', right_on = 'codigo_negociacao', how = 'left')
    df_final = df_merge[['Código', 'valor_sebrae', 'valor_empresa', 'valor_unidade_embrapii', 'valor_embrapii', 'codigo_negociacao']]
    df_combinado = pd.concat([df_sebrae, df_final])

    # Selecionar apenas as colunas de interesse
    colunas_contratos = [
        "codigo_projeto",
        "unidade_embrapii",
        "data_contrato",
        "data_inicio",
        "data_termino",
        "parceria_programa",
        "call",
        "cooperacao_internacional",
        "modalidade_financiamento",
        "uso_recurso_obrigatorio",
        "projeto",
        "trl_inicial",
        "trl_final",
        "valor_embrapii",
        "valor_empresa",
        "valor_unidade_embrapii",
    ]
    df_contratos_selecionado = df_contratos[colunas_contratos]

    colunas_projetos = [
        "codigo_projeto",
        "status",
        "tipo_projeto",
        "titulo",
        "titulo_publico",
        "objetivo",
        "descricao_publica",
        "data_avaliacao",
        "nota_avaliacao",
        "observacoes",
        "tags",
    ]
    df_projetos_selecionado = df_projetos[colunas_projetos]

    colunas_classificacao_projeto = [
        "Código",
        "Tecnologias Habilitadoras",
        "Áreas de Aplicação",
        "Missões - CNDI final",
        "Brasil Mais Produtivo",
    ]
    df_classificacao_projeto_selecionado = df_classificacao_projeto[colunas_classificacao_projeto]

    colunas_projetos_contratados = [
        "Código",
        "Negociação",
        "Macroentregas",
        "% de Aceites"
    ]
    df_relatorio_projetos_contratados = df_relatorio_projetos_contratados[colunas_projetos_contratados]
    df_relatorio_projetos_contratados['% de Aceites'] = (
    df_relatorio_projetos_contratados['% de Aceites']
    .str.replace(' %', '', regex=False)  # Remove o " %"
    .str.replace(',', '.', regex=False)  # Substitui a vírgula por ponto
    .astype(float)  # Converte para float
)
    df_relatorio_projetos_contratados['% de Aceites'] = df_relatorio_projetos_contratados['% de Aceites']/100

    # Mesclar os dados com base na chave "codigo_projeto"
    df_portfolio = df_contratos_selecionado.merge(df_projetos_selecionado, on='codigo_projeto', how='left')
    df_portfolio = df_portfolio.merge(df_classificacao_projeto_selecionado, left_on='codigo_projeto', right_on='Código', how='left')
    df_portfolio = df_portfolio.merge(df_relatorio_projetos_contratados, left_on = 'codigo_projeto', right_on = 'Código', how = 'left')
    # df_portfolio = df_portfolio.merge(df_projetos_contratados_selecionados, on='codigo_projeto', how='left')
    df_portfolio = df_portfolio.merge(df_combinado, left_on = 'codigo_projeto', right_on = 'Código', how = 'left')
    df_portfolio = df_portfolio.drop_duplicates(subset='codigo_projeto', keep='first')

    # Adicionar a coluna "data_extracao_dados" com a data de hoje
    df_portfolio['data_extracao_dados'] = datetime.now()

    df_portfolio = df_portfolio.rename(columns={
        'Tecnologias Habilitadoras': 'tecnologia_habilitadora',
        'Áreas de Aplicação': 'area_aplicacao',
        'Missões - CNDI final': 'missoes_cndi',
        'Brasil Mais Produtivo': 'brasil_mais_produtivo',
        'codigo_negociacao': 'cn',
        'Negociação': 'codigo_negociacao',
        'Macroentregas': 'macroentregas', 
        '% de Aceites': 'pct_aceites'
    })

    df_portfolio['valor_empresa'] = np.where(
        df_portfolio['valor_empresa_y'].isna(), 
        df_portfolio['valor_empresa_x'], 
        df_portfolio['valor_empresa_y']
    )

    df_portfolio['valor_unidade_embrapii'] = np.where(
        df_portfolio['valor_unidade_embrapii_y'].isna(), 
        df_portfolio['valor_unidade_embrapii_x'], 
        df_portfolio['valor_unidade_embrapii_y']
    )

    df_portfolio['valor_embrapii'] = np.where(
        df_portfolio['valor_embrapii_y'].isna(), 
        df_portfolio['valor_embrapii_x'], 
        df_portfolio['valor_embrapii_y']
    )

    # Reordenar as colunas conforme especificado
    colunas_finais = [
        "codigo_projeto",
        "unidade_embrapii",
        "data_contrato",
        "data_inicio",
        "data_termino",
        "status",
        "tipo_projeto",
        "parceria_programa",
        "call",
        "cooperacao_internacional",
        "modalidade_financiamento",
        "uso_recurso_obrigatorio",
        "tecnologia_habilitadora",
        "missoes_cndi",
        "area_aplicacao",
        "projeto",
        "trl_inicial",
        "trl_final",
        "valor_embrapii",
        "valor_empresa",
        "valor_unidade_embrapii",
        "titulo",
        "titulo_publico",
        "objetivo",
        "descricao_publica",
        "data_avaliacao",
        "nota_avaliacao",
        "observacoes",
        "tags",
        "data_extracao_dados",
        "brasil_mais_produtivo",
        "valor_sebrae",
        "codigo_negociacao",
        "macroentregas",
        "pct_aceites"
    ]
    df_portfolio = df_portfolio[colunas_finais]

    # Tratar campos de data e valores
    campos_data = [
        "data_contrato",
        "data_inicio",
        "data_termino",
        "data_avaliacao",
        "data_extracao_dados",
    ]
    campos_valores = [
        "valor_embrapii",
        "valor_empresa",
        "valor_unidade_embrapii",
        "valor_sebrae"
    ]

    for campo in campos_data:
        df_portfolio[campo] = pd.to_datetime(df_portfolio[campo], errors='coerce', format = '%d/%m/%Y %H:%M:%S')

    for campo in campos_valores:
        df_portfolio[campo] = df_portfolio[campo].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Garantir que o diretório de destino existe
    os.makedirs(destino, exist_ok=True)

    # Salvar o arquivo resultante
    with pd.ExcelWriter(arquivo_destino, engine='xlsxwriter') as writer:
        df_portfolio.to_excel(writer, index=False, sheet_name='Portfolio')

        # Acessar o workbook e worksheet
        workbook = writer.book
        worksheet = writer.sheets['Portfolio']

        # Definir largura das colunas
        for i, coluna in enumerate(df_portfolio.columns):
            col_idx = i
            worksheet.set_column(col_idx, col_idx, 20)

        # Aplicar formatação de data
        format_date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        for campo in campos_data:
            if campo in df_portfolio.columns:
                col_idx = df_portfolio.columns.get_loc(campo)
                worksheet.set_column(col_idx, col_idx, 20, format_date)

        # Aplicar formatação numérica
        format_currency = workbook.add_format({'num_format': '#,##0.00'})
        for campo in campos_valores:
            if campo in df_portfolio.columns:
                col_idx = df_portfolio.columns.get_loc(campo)
                worksheet.set_column(col_idx, col_idx, 20, format_currency)

# Exemplo de chamada da função
if __name__ == "__main__":
    criar_tabela_portfolio()
