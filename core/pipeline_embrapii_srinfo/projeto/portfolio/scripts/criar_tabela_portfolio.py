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
    raw_ibge_ipca = os.path.join(base_dir, 'DWPII_copy', 'ipca_ibge.xlsx')
    raw_projetos_empresas = os.path.join(base_dir, 'projeto', 'projetos_empresas', 'step_3_data_processed', 'projetos_empresas.xlsx')
    raw_info_empresas = os.path.join(base_dir, 'projeto', 'projetos_empresas', 'step_3_data_processed', 'informacoes_empresas.xlsx')
    raw_unidade_embrapii = os.path.join(base_dir, 'unidade_embrapii', 'info_unidades', 'step_3_data_processed', 'info_unidades_embrapii.xlsx')
    raw_pedidos_pi = os.path.join(base_dir, 'projeto', 'pedidos_pi', 'step_3_data_processed', 'pedidos_pi.xlsx')
    destino = os.path.join(base_dir, 'projeto', 'portfolio', 'step_3_data_processed')
    arquivo_destino = os.path.join(destino, 'portfolio.xlsx')

    # Ler os arquivos Excel
    df_projetos = pd.read_excel(raw_projetos_path)
    df_contratos = pd.read_excel(raw_contratos_path)
    df_classificacao_projeto = pd.read_excel(raw_classificacao_projeto_path)
    df_relatorio_projetos_contratados = pd.read_excel(raw_relatorio_projetos_contratados_path)
    df_sebrae = pd.read_excel(raw_sebrae_path)
    df_sebrae_srinfo = pd.read_excel(raw_sebrae_srinfo_path)
    df_ipca = pd.read_excel(raw_ibge_ipca)
    df_projetos_empresas = pd.read_excel(raw_projetos_empresas)
    df_info_empresas = pd.read_excel(raw_info_empresas)
    df_unidade_embrapii = pd.read_excel(raw_unidade_embrapii)
    df_pedidos_pi = pd.read_excel(raw_pedidos_pi)

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
        "projeto_rede",
        "projeto_rede_papel",
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
        "pct_aceites",
        "projeto_rede",
        "projeto_rede_papel",
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
    
    # Aplicar correção
    colunas_valores = [
        "valor_embrapii",
        "valor_empresa",
        "valor_unidade_embrapii",
        "valor_sebrae",
    ]
    for col in colunas_valores:
        nova_col = f"_ipca_{col}"
        df_portfolio[nova_col] = df_portfolio.apply(
            lambda row: corrigir_valor_ipca(
                df_ipca, row["data_contrato"].year, row["data_contrato"].month, row[col]
            ),
            axis=1,
        )
    # Criar a coluna _ipca_valor_total com a soma das colunas corrigidas
    colunas_ipca = [f"_ipca_{col}" for col in colunas_valores]
    df_portfolio["_ipca_valor_total"] = df_portfolio[colunas_ipca].sum(axis=1)

    # Empresas
    df_info_empresas['info_empresa'] = df_info_empresas.apply(
        lambda x: f"[{x['cnpj']}] {x['empresa']} [{x['uf']}] [{x['porte']}] [CNAE: {x['cnae_subclasse']}]",
        axis=1
    )
    df_projetos_empresas = df_projetos_empresas.merge(
        df_info_empresas[['cnpj', 'info_empresa']],
        on='cnpj',
        how='left'
    )
    df_empresas_agregadas_por_projeto = (
        df_projetos_empresas.groupby('codigo_projeto')['info_empresa']
        .apply(lambda x: '; '.join(x.dropna().astype(str)))
        .reset_index()
    )
    df_portfolio = df_portfolio.merge(
        df_empresas_agregadas_por_projeto,
        on='codigo_projeto',
        how='left'
    )
    df_portfolio['n_empresas'] = df_portfolio['info_empresa'].apply(
        lambda x: len(x.split(';')) if pd.notnull(x) else 0
    )

    # Unidades Embrapii
    df_unidade_embrapii_renomeado = df_unidade_embrapii.rename(columns={
        'uf': 'ue_uf',
        'tipo_instituicao': 'ue_tipo_instituicao',
        'competencias_tecnicas': 'ue_competencias_tecnicas',
        'status_credenciamento': 'ue_status'
    })
    df_portfolio = df_portfolio.merge(
        df_unidade_embrapii_renomeado[['unidade_embrapii', 'ue_uf', 'ue_tipo_instituicao', 'ue_competencias_tecnicas', 'ue_status']],
        on='unidade_embrapii',
        how='left'
    )

    # Pedidos de PI
    df_pedidos_pi_count = (
        df_pedidos_pi.groupby('codigo_projeto')
        .size()
        .reset_index(name='n_pedidos_pi')
    )
    df_portfolio = df_portfolio.merge(
        df_pedidos_pi_count,
        on='codigo_projeto',
        how='left'
    )
    df_portfolio['n_pedidos_pi'] = df_portfolio['n_pedidos_pi'].fillna(0).astype(int)

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


def corrigir_valor_ipca(ipca_df, ano_contrato, mes_contrato, valor):
    """
    Corrige um valor monetário com base na variação do IPCA entre o mês anterior ao início do contrato
    e o último mês disponível no IPCA, conforme metodologia do IBGE.

    Se o contrato for posterior ao último IPCA disponível, retorna o valor original (sem correção).

    https://www.ibge.gov.br/explica/inflacao.php
    """
    ipca_df["Mês (Código)"] = ipca_df["Mês (Código)"].astype(str)

    # Definir o mês anterior ao contrato
    if mes_contrato == 1:
        mes_anterior = 12
        ano_anterior = ano_contrato - 1
    else:
        mes_anterior = mes_contrato - 1
        ano_anterior = ano_contrato

    mes_anterior_str = f"{ano_anterior}{mes_anterior:02d}"

    # Verifica o último mês disponível na base do IPCA
    ultimo_mes_ipca = ipca_df["Mês (Código)"].iloc[-1]

    # Se o mês anterior ao contrato for posterior ao último IPCA, não corrige
    if mes_anterior_str > ultimo_mes_ipca:
        return valor  # valor nominal

    try:
        ipca_base = float(
            ipca_df.loc[ipca_df["Mês (Código)"] == mes_anterior_str, "Valor"].values[0]
        )
        ipca_final = float(
            ipca_df.loc[ipca_df["Mês (Código)"] == ultimo_mes_ipca, "Valor"].values[0]
        )

        if ipca_base == 0:
            return None

        fator = ipca_final / ipca_base
        return valor * fator
    except IndexError:
        return None


# Exemplo de chamada da função
if __name__ == "__main__":
    criar_tabela_portfolio()
