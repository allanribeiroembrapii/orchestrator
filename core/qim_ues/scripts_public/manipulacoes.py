import pandas as pd
import os
import sys
import re
import locale
from datetime import datetime

locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

ARQUIVOS_BRUTOS = os.path.abspath(os.path.join(ROOT, 'arquivos_brutos'))
UP = os.path.abspath(os.path.join(ROOT, 'up'))

def pa_qim():
    # data de hoje
    today = datetime.now()

    # Ler o arquivo Excel
    df = pd.read_excel(os.path.join(ARQUIVOS_BRUTOS, 'pa_qim.xlsx'))
    df['pa_vigente'] = df['pa_vigente'].str.split(': ', n=1).str[1]
    df['data_inicio_pa'] = df['data_inicio_pa'].str.split(': ', n=1).str[1]
    df['data_inicio_pa'] = df['data_inicio_pa'].apply(lambda x: pd.Series(converte_data(x)))
    df['periodo_referencia'] = df['periodo_referencia'].str.split('\n', n=1).str[1]
    df[['data_inicio_ref', 'data_termino_ref']] = df['periodo_referencia'].apply(lambda x: pd.Series(extrair_datas(x)))
    df['nota_qim'] = df['nota_qim'].str.replace('%', '', regex=False).astype(int)/100
    
    pa = pd.DataFrame({
        'id_pa': df['Unnamed: 0'],
        'unidade_embrapii': df['unidade_embrapii'],
        'pa_vigente': df['pa_vigente'],
        'data_inicio_pa': pd.to_datetime(df['data_inicio_pa'], format='%d/%m/%Y', errors='coerce'),
    })

    pa = comparar_excel("pa.xlsx", pa, manter_duplicados = False)

    qim = pd.DataFrame({
        'unidade_embrapii': df['unidade_embrapii'],
        'pa_vigente': df['pa_vigente'],
        'data_inicio_pa': pd.to_datetime(df['data_inicio_pa'], format='%d/%m/%Y', errors='coerce'),
        'data_inicio_ref': pd.to_datetime(df['data_inicio_ref'], format='%d/%m/%Y', errors='coerce'),
        'data_termino_ref': pd.to_datetime(df['data_termino_ref'], format='%d/%m/%Y', errors='coerce'),
        'nota_qim': df['nota_qim'],
        'data_extracao': pd.to_datetime(today, format='%d/%m/%Y', errors='coerce')
        })
    
    qim_historico = comparar_excel("qim.xlsx", qim, manter_duplicados=True, pa = pa)[['id_pa', 'unidade_embrapii', 'pa_vigente', 'nota_qim',
                                                                                      'data_inicio_ref', 'data_termino_ref', 'data_extracao']]
    
    qim_atual = qim_historico.sort_values(['unidade_embrapii', 'data_extracao']).drop_duplicates(subset=['unidade_embrapii'], keep='last')[['id_pa', 'unidade_embrapii',
                                                                                                                                            'pa_vigente', 'nota_qim',
                                                                                                                                            'data_inicio_ref', 'data_termino_ref',
                                                                                                                                            'data_extracao']]


    with pd.ExcelWriter(os.path.join(UP, 'pa.xlsx'), engine="xlsxwriter") as writer:
        pa.to_excel(writer, index=False, sheet_name="Sheet1")
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        # Formato de data
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Aplicando o formato para a coluna de datas
        worksheet.set_column("D:D", None, date_format)

    with pd.ExcelWriter(os.path.join(UP, 'qim.xlsx'), engine="xlsxwriter") as writer:
        qim_historico.to_excel(writer, index=False, sheet_name="Sheet1")
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        # Formato de data
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Aplicando o formato para a coluna de datas
        worksheet.set_column("E:G", None, date_format)

    with pd.ExcelWriter(os.path.join(UP, 'qim_atual.xlsx'), engine="xlsxwriter") as writer:
        qim_atual.to_excel(writer, index=False, sheet_name="Sheet1")
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        # Formato de data
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Aplicando o formato para a coluna de datas
        worksheet.set_column("E:G", None, date_format)

    return pa, today

def resultados(pa, today):
    # Ler o arquivo Excel
    df = pd.read_excel(os.path.join(ARQUIVOS_BRUTOS, 'resultados.xlsx'))
    df['num_meta'] = df['num_meta'].astype(int)
    df['peso_meta'] = df['peso_meta'].astype(int)
    df['resultado'] = df['resultado'].str.replace(',', '.', regex=False).astype(float)/100
    df['pa_vigente'] = df['pa_vigente'].str.split(': ', n=1).str[1]
    df['data_inicio_pa'] = df['data_inicio_pa'].str.split(': ', n=1).str[1]
    df['data_inicio_pa'] = df['data_inicio_pa'].apply(lambda x: pd.Series(converte_data(x)))
    df['periodo_referencia'] = df['periodo_referencia'].str.split('\n', n=1).str[1]
    df[['data_inicio_ref', 'data_termino_ref']] = df['periodo_referencia'].apply(lambda x: pd.Series(extrair_datas(x)))

    # Criar o dicionário de mapeamento com base nos dados da imagem
    mapeamento_titulos = {
        "Número Empresas Prospectadas": "Empresas prospectadas",
        "Contratação de Projetos": "Projetos contratados",
        "Pedidos de Propriedade Intelectual": "Pedidos de Propriedade intelectual (PI)",
        "Taxa de Sucessos de Propostas Técnicas": "Taxa de sucesso de propostas técnicas",
        "Participação Financeira das Empresas no Portfólio": "Participação financeira das empresas nos projetos contratados",
        "Participação de alunos(as) em projetos de PD&I": "Participação de alunos em projetos de PD&I",
        "Satisfação das Empresas": "Satisfação das empresas",
        "Propostas Técnicas": "Propostas técnicas",
        "Empresas Contratadas": "Empresas contratantes",
        "Empresas em Eventos": "Eventos com empresas",
    }

    # Renomear a coluna 'titulo_meta' no dataframe 'resultados'
    df['titulo_meta'] = df['titulo_meta'].replace(mapeamento_titulos)

    resultados = pd.DataFrame({
        'unidade_embrapii': df['unidade_embrapii'],
        'pa_vigente': df['pa_vigente'],
        'data_inicio_pa': pd.to_datetime(df['data_inicio_pa'], format='%d/%m/%Y', errors='coerce'),
        'data_inicio_ref': pd.to_datetime(df['data_inicio_ref'], format='%d/%m/%Y', errors='coerce'),
        'data_termino_ref': pd.to_datetime(df['data_termino_ref'], format='%d/%m/%Y', errors='coerce'),
        'num_meta': df['num_meta'],
        'titulo_meta': df['titulo_meta'],
        'peso': df['peso_meta'],
        'pct_resultado': df['resultado'],
        'data_extracao': pd.to_datetime(today, format='%d/%m/%Y', errors='coerce')
    })

    resultados = comparar_excel("resultados.xlsx", resultados, manter_duplicados=True, pa = pa)[['id_pa', 'unidade_embrapii', 'pa_vigente', 'num_meta', 'titulo_meta',
                                                                                                 'peso', 'pct_resultado', 'data_inicio_ref', 'data_termino_ref', 'data_extracao']]

    with pd.ExcelWriter(os.path.join(UP, 'resultados.xlsx'), engine="xlsxwriter") as writer:
        resultados.to_excel(writer, index=False, sheet_name="Sheet1")
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        # Formato de data
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Aplicando o formato para a coluna de datas
        worksheet.set_column("H:J", None, date_format)

    # resultados.to_excel('up/resultados.xlsx', date_format='%d/%m/%Y', index=False)



# Função para converter datas do formato "dd de mês de yyyy" para "dd/mm/yyyy"
def converte_data(data):
    try:
        # Tentar converter o formato "5 de março de 2024" para "05/03/2024"
        return datetime.strptime(data, "%d de %B de %Y").strftime("%d/%m/%Y")
    except ValueError:
        try:
            # Caso já esteja no formato "dd/mm/yyyy"
            return datetime.strptime(data, "%d/%m/%Y").strftime("%d/%m/%Y")
        except ValueError:
            return None  # Retorna None caso o formato seja inválido

# Função para extrair e formatar as datas
def extrair_datas(periodo):
    # Regular expression para identificar ambos os formatos
    regex = r'(\d{1,2} de \w+ de \d{4}|\d{1,2}/\d{1,2}/\d{4})\s*(?:a|até)\s*(\d{1,2} de \w+ de \d{4}|\d{1,2}/\d{1,2}/\d{4})'
    
    # Procurar o padrão na string
    match = re.match(regex, periodo)
    
    if match:
        data_inicial, data_final = match.groups()
        
        # Verificar se é necessário converter o formato "dd de mês de yyyy"
        data_inicial_formatada = converte_data(data_inicial)
        data_final_formatada = converte_data(data_final)
        
        return data_inicial_formatada, data_final_formatada
    else:
        return None, None
    

def comparar_excel(arquivo_antigo, arquivo_novo, manter_duplicados=False, pa = None):
    # Caminhos dos arquivos
    COPY = os.path.abspath(os.path.join(ROOT, 'copy'))

    # Leitura da planilha
    copy = pd.read_excel(os.path.abspath(os.path.join(COPY, arquivo_antigo)))

    if not manter_duplicados:
        # Encontrar o último valor de 'id_pa' no arquivo antigo
        ultimo_id_pa = copy['id_pa'].max() if not copy['id_pa'].empty else 0

        # Identificar as linhas únicas no arquivo_novo (não presentes no arquivo_antigo)
        # Compara todas as colunas, exceto 'id_pa'
        colunas_comparacao = arquivo_novo.columns.difference(['id_pa'])
        novo_unico = arquivo_novo.loc[~arquivo_novo[colunas_comparacao].apply(tuple, 1).isin(copy[colunas_comparacao].apply(tuple, 1))]

        # Atualizar 'id_pa' para as linhas únicas no arquivo_novo, começando do próximo valor
        novo_unico['id_pa'] = range(ultimo_id_pa + 1, ultimo_id_pa + 1 + len(novo_unico))

        # Concatenar os DataFrames
        combined = pd.concat([copy, novo_unico], ignore_index=False)

    elif pa is not None and not pa.empty:
        combined = pd.merge(arquivo_novo, pa[['id_pa', 'unidade_embrapii', 'pa_vigente', 'data_inicio_pa']],
                            on=['unidade_embrapii', 'pa_vigente', 'data_inicio_pa'], how='left')
        combined = pd.concat([copy, combined], ignore_index=False)

    return combined