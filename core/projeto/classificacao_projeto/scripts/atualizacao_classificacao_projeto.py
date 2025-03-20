import pandas as pd
import openpyxl
import os
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

def atualizacao_classificao_projeto():
    # Define os caminhos das planilhas
    # base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    caminho_atual = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw', 'atual_classificacao_projeto.xlsx')
    caminho_new = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_2_stage_area', 'new_classificacao_projeto.xlsx')
    caminho_destino = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_3_data_processed', 'classificacao_projeto.xlsx')

    # Ler as planilhas
    df_atual = pd.read_excel(caminho_atual, sheet_name='Planilha1')
    df_new = pd.read_excel(caminho_new)

    # Merge
    classificacoes = ['Tecnologias Habilitadoras', 'Áreas de Aplicação', 'Missões - CNDI final',
                      'Amazônia', 'Descarbonização', 'Brasil Mais Produtivo',
                      'Biocombustíveis', 'Energia Renovável', 'saude_pdil_mdpts', 'NIB5_Modificado',
                      'Energia Eólica', 'Fertilizantes', 'Tecnologias Verdes', 'Descarbonizacao_Cimento_Siderurgia',
                      'Sistema de Alerta Climático']
    classificacoes_com_codigo = classificacoes + ['Código']
    df_merge = df_new.merge(df_atual[classificacoes_com_codigo], on='Código', how='left')

    # Colocar não definido registros vazios
    df_merge[classificacoes] = df_merge[classificacoes].fillna('Não definido')

    # Ordenando as colunas
    colunas_ordenadas = [
        'Código',
        'Unidade EMBRAPII',
        'Empresas',
        'Porte da Empresa',
        'Número de Empresas no Projeto',
        'Agrupamento Div CNAE',
        'CNAE Divisão',
        'Nomenclatura CNAE Divisão',
        'Grande Área de Competência',
        'Competência UE',
        'Tecnologias Habilitadoras',
        'Áreas de Aplicação',
        'Missões - CNDI final',
        'Projeto',
        'Título público',
        'Objetivo',
        'Descrição pública',
        'Tipo de projeto',
        'Call',
        'Data do contrato',
        'Nível de maturidade inicial',
        'Nível de maturidade final',
        'Valor total',
        'Valor aportado EMBRAPII',
        'Valor aportado Empresa',
        'Valor aportado pela Unidade',
        'Amazônia',
        'Descarbonização',
        'Brasil Mais Produtivo',
        'Biocombustíveis',
        'Energia Renovável',
        'saude_pdil_mdpts',
        'NIB5_Modificado',
        'Energia Eólica',
        'Fertilizantes',
        'Tecnologias Verdes',
        'Descarbonizacao_Cimento_Siderurgia',
        'Sistema de Alerta Climático'
    ]

    df_merge = df_merge[colunas_ordenadas]

    # Criar colunas auxiliares para priorizar "Não definido"
    clas_prioridade = ['THP', 'APP', 'MCP', 'AP', 'DP', 'BMP', 'BIOP']
    
    # Itera sobre as colunas de classificações e classificações de prioridade ao mesmo tempo
    for class_col, priority_col in zip(classificacoes, clas_prioridade):
        df_merge[priority_col] = df_merge[class_col].apply(lambda x: 0 if x == "Não definido" else 1)



    # Ordenar priorizando "Não definido"
    df_final = df_merge.sort_values(by=clas_prioridade)

    # Remover colunas auxiliares
    df_final = df_final.drop(columns=clas_prioridade)

    # Salvar a planilha reordenada no caminho de destino
    df_final.to_excel(caminho_destino, index=False, sheet_name='Planilha1')

    # Ajustar as larguras das colunas
    wb_final = openpyxl.load_workbook(caminho_destino)
    ws_final = wb_final['Planilha1']

    for col in ws_final.columns:
        max_length = 30  # Largura desejada
        col_letter = col[0].column_letter  # Obter a letra da coluna
        ws_final.column_dimensions[col_letter].width = max_length

    wb_final.save(caminho_destino)