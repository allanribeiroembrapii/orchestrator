import pandas as pd
import os
import sys
import openpyxl
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

def determinar_porte(faixa):
    if faixa == "Até R$ 360 mil":
        return "Microempresa"
    elif faixa == "Entre R$ 360 mil e R$ 4,8 milhões":
        return "Pequena"
    elif faixa == "Entre R$ 4,8 e R$ 300 milhões":
        return "Média"
    elif faixa == "Maior que R$ 300 milhões":
        return "Grande"
    elif faixa == "Não Informado":
        return "Não Informado"
    else:
        return "Não informado"

def criar_tabela_informacoes_empresas():

    # Caminho do arquivo Excel
    origem = os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed')
    nome_arquivo = 'projetos_empresas.xlsx'
    arquivo_origem = os.path.join(origem, nome_arquivo)
    destino = os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed')
    arquivo_destino = os.path.join(destino, 'informacoes_empresas.xlsx')

    # Ler o arquivo Excel
    df_novo = pd.read_excel(arquivo_origem) #projetos_empresas
    df_atual = pd.read_excel(os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_1_data_raw', 'raw_informacoes_empresas.xlsx')) #informacoes_empresas atual
    df_atual['novo'] = 'Não'
    df_atual.to_excel(os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_1_data_raw', 'raw_informacoes_empresas.xlsx'), index=False)
    info_empresas = pd.read_excel(os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_1_data_raw', 'raw_empresas.xlsx')) #info_empresas novo
    empresas_contratantes = pd.read_excel(os.path.join(ROOT, 'analises_relatorios', 'empresas_contratantes',
                                                       'step_1_data_raw', 'raw_relatorio_empresas_contratantes_1.xlsx')) #empresas_contratantes

    # Selecionar os cnpjs e retirar duplicadas
    df_selecionado = df_novo['cnpj'].drop_duplicates()


    # Identificar novos registros
    novos_registros = df_selecionado[~df_selecionado.isin(df_atual['cnpj'])]
    novos_registros = novos_registros.to_frame(name='cnpj')

    # Mesclar com empresas
    novos_registros = pd.merge(novos_registros, empresas_contratantes, how = 'left', left_on = 'cnpj', right_on='CNPJ')
    novos_registros = pd.merge(novos_registros, info_empresas, how = 'left', on='cnpj')
    novos_registros['porte'] = novos_registros['Faixa de faturamento declarada'].apply(determinar_porte)
    novos_registros['novo'] = 'Sim'
    novos_registros = novos_registros[['cnpj', 'Empresa', 'endereco_uf', 'endereco_municipio', 'porte', 'Faixa de faturamento declarada', 'CNAE', 'novo']]

    # Renomear as colunas
    novos_registros = novos_registros.rename(columns={
        "Empresa": "empresa",
        "endereco_uf": "uf",
        "endereco_municipio": "municipio",
        "Faixa de faturamento declarada": "faixa_faturamento",
        "CNAE": "cnae_subclasse"
    })

    # Carregar a planilha atual com openpyxl
    wb = openpyxl.load_workbook(os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_1_data_raw', 'raw_informacoes_empresas.xlsx'))
    ws = wb['Sheet1']

    # Adicionar novos registros ao final da planilha atual
    for _, row in novos_registros.iterrows():
        ws.append(list(row))

    # Salvar a nova planilha temporariamente para manipulação com pandas
    caminho_temp = os.path.join(ROOT, 'projeto', 'projetos_empresas', 'temp_informacoes_empresas.xlsx')
    wb.save(caminho_temp)

    # Recarregar a planilha temporária com pandas para reordenar
    df_final = pd.read_excel(caminho_temp, sheet_name='Sheet1')

    # Criar colunas auxiliares para priorizar "Não definido"
    df_final['Novo Prioridade'] = df_final['novo'].apply(lambda x: 0 if x == "Sim" else 1)

    # Ordenar priorizando "Não definido"
    df_final_sorted = df_final.sort_values(by=['Novo Prioridade', 'novo'])

    # Remover colunas auxiliares
    df_final_sorted = df_final_sorted.drop(columns=['Novo Prioridade'])

    # Salvar a planilha reordenada no caminho de destino
    df_final_sorted.to_excel(arquivo_destino, index=False, sheet_name='Planilha1')

    # Remover o arquivo temporário
    os.remove(caminho_temp)

#Executar função
if __name__ == "__main__":
    criar_tabela_informacoes_empresas()