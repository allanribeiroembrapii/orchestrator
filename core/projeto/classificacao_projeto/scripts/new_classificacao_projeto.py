import pandas as pd
import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

def new_classificacao_projeto():

    # Define os caminhos das planilhas
    path_projetos_empresas = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw', 'projetos_empresas.xlsx')
    path_projetos_contratados = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw', 'raw_projetos_contratados.xlsx')
    path_informacoes_empresas = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw', 'informacoes_empresas.xlsx')
    path_cnae = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw', 'raw_cnae_divisao.xlsx')
    path_ues = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw', 'raw_competencias_ues.xlsx')
    path_destino = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_2_stage_area', 'new_classificacao_projeto.xlsx')

    # Ler as planilhas
    df_projetos_empresas = pd.read_excel(path_projetos_empresas)
    df_projetos_contratados = pd.read_excel(path_projetos_contratados)
    df_informacoes_empresas = pd.read_excel(path_informacoes_empresas)
    df_cnae = pd.read_excel(path_cnae)
    df_ues = pd.read_excel(path_ues)
    
    #buscar informações das empresas
    df_informacoes_empresas = df_informacoes_empresas[['cnpj', 'empresa', 'faixa_faturamento', 'cnae_subclasse', 'porte']]
    df_merged = df_projetos_empresas.merge(df_informacoes_empresas, on='cnpj', how='left')

    def extrair_dois_primeiros_digitos(cnae):
        if isinstance(cnae, str):
            return int(cnae[:2]) if cnae else None
        return None
    
    df_merged['cnae_divisao'] = df_merged['cnae_subclasse'].apply(extrair_dois_primeiros_digitos)
    df_merged = df_merged.merge(df_cnae, on='cnae_divisao', how='left')

    #contar número de empresas
    numero_empresas = df_merged['codigo_projeto'].value_counts()
    df_merged = df_merged.merge(numero_empresas, on='codigo_projeto', how='left')

    # Agregar os dados pelo Código
    df_aggregated = df_merged.groupby('codigo_projeto').agg({
        'cnpj': lambda x: '; '.join(x.dropna().astype(str)),
        'cnae_subclasse': lambda x: '; '.join(x.dropna().astype(str)),
        'cnae_divisao': lambda x: '; '.join(x.dropna().astype(str)),
        'empresa': lambda x: '; '.join(x.dropna().astype(str)),
        'faixa_faturamento': lambda x: '; '.join(x.dropna().astype(str)),
        'agrupamento': lambda x: '; '.join(x.dropna().astype(str)),
        'nomenclatura': lambda x: '; '.join(x.dropna().astype(str)),
        'porte': lambda x: '; '.join(x.dropna().astype(str)),
        'count': 'first',
    }).reset_index()

    df_aggregated = df_aggregated.merge(
        df_projetos_contratados[['Código', 'Unidade EMBRAPII', 'Projeto', 'Título público', 'Objetivo', 'Descrição pública',
                                 'Tipo de projeto', 'Call', 'Data do contrato', 'Nível de maturidade inicial',
                                 'Nível de maturidade final', 'Valor total', 'Valor aportado EMBRAPII',
                                 'Valor aportado Empresa', 'Valor aportado Unidade']],
        left_on='codigo_projeto',
        right_on='Código',
        how='left')

    #buscar os dados de competências das UEs
    df_aggregated = df_aggregated.merge(
        df_ues[['unidade_embrapii', 'grande_area_competencia', 'competencia']],
            left_on='Unidade EMBRAPII',
            right_on='unidade_embrapii',
            how='left'
    )

    # # Criar novas colunas
    # df_aggregated["tecnologia_habilitadora"] = ""
    # df_aggregated["area_aplicacao"] = ""
    # df_aggregated["missoes"] = ""
    # df_aggregated["amazonia"] = ""
    # df_aggregated["descarbonizacao"] = ""

    # Renomear as colunas
    df_aggregated = df_aggregated.rename(columns={
        'Código': 'Código',
        'Unidade EMBRAPII': 'Unidade EMBRAPII',
        'empresa': 'Empresas',
        'porte': 'Porte da Empresa',
        'count': 'Número de Empresas no Projeto',
        'agrupamento': 'Agrupamento Div CNAE',
        'cnae_divisao': 'CNAE Divisão',
        'nomenclatura': 'Nomenclatura CNAE Divisão',
        'grande_area_competencia': 'Grande Área de Competência',
        'competencia': 'Competência UE',
        # 'tecnologia_habilitadora': 'Tecnologias Habilitadoras',
        # 'area_aplicacao': 'Áreas de Aplicação',
        # 'missoes': 'Missões - CNDI final',
        'Projeto': 'Projeto',
        'Título público': 'Título público',
        'Objetivo': 'Objetivo',
        'Descrição pública': 'Descrição pública',
        'Tipo de projeto': 'Tipo de projeto',
        'Call': 'Call',
        'Data do contrato': 'Data do contrato',
        'Nível de maturidade inicial': 'Nível de maturidade inicial',
        'Nível de maturidade final': 'Nível de maturidade final',
        'Valor total': 'Valor total',
        'Valor aportado EMBRAPII': 'Valor aportado EMBRAPII',
        'Valor aportado Empresa': 'Valor aportado Empresa',
        'Valor aportado Unidade': 'Valor aportado pela Unidade',

        # 'amazonia': 'Amazônia',
        # 'descarbonizacao': 'Descarbonização'
    })

    # Ajustar campo de data: 'Data do contrato'
    df_aggregated['Data do contrato'] = pd.to_datetime(df_aggregated['Data do contrato'], format='%d/%m/%Y')

    # Função para converter valores monetários de texto para formato numérico
    def converter_valores(valor):
        try:
            return float(valor.replace('.', '').replace(',', '.'))
        except ValueError:
            return None

    # Ajustar os campos de valores
    campos_valores = ['Valor total', 'Valor aportado EMBRAPII', 'Valor aportado Empresa', 'Valor aportado pela Unidade']
    for campo in campos_valores:
        df_aggregated[campo] = df_aggregated[campo].apply(converter_valores)

    
    # Salvar em Excel com formatação
    with pd.ExcelWriter(path_destino, engine='xlsxwriter') as writer:
        df_aggregated.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Formatos
        format_date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        format_currency = workbook.add_format({'num_format': 'R$ #,##0.00'})

        # Aplicar formatação
        worksheet.set_column('U:U', None, format_date)
        for col in ['W', 'X', 'Y', 'Z']:
            worksheet.set_column(f'{col}:{col}', None, format_currency)

#Executar função
if __name__ == "__main__":
    new_classificacao_projeto()