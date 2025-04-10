import pandas as pd
import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

def criar_tabela_projetos_empresas():

    # Caminho do arquivo Excel
    origem = os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_1_data_raw')
    nome_arquivo = 'raw_projetos_contratados.xlsx'
    arquivo_origem = os.path.join(origem, nome_arquivo)
    destino = os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed')
    arquivo_destino = os.path.join(destino, 'projetos_empresas.xlsx')

    # Ler o arquivo Excel
    df = pd.read_excel(arquivo_origem)

    # Selecionar as colunas desejadas
    colunas_desejadas = [
        "Código", 
        "CNPJ"]
    df_selecionado = df[colunas_desejadas]

    # Renomear as colunas
    df_renomeado = df_selecionado.rename(columns={
        "Código": "codigo_projeto",
        "CNPJ": "cnpj"
    })

    # Quebrar os valores da coluna "cnpj" por ";" e transformar em linhas separadas
    df_explodido = df_renomeado.assign(cnpj=df_renomeado['cnpj'].str.split(';')).explode('cnpj')

    # Remover espaços em branco no início e no final das células da coluna "cnpj"
    df_explodido['cnpj'] = df_explodido['cnpj'].str.strip()

    # Remover linhas onde "cnpj" está vazia
    df_explodido = df_explodido[df_explodido['cnpj'] != '']

    # Garantir que o diretório de destino existe
    os.makedirs(destino, exist_ok=True)

    # Salvar o arquivo resultante
    df_explodido.to_excel(arquivo_destino, index=False)

#Executar função
if __name__ == "__main__":
    criar_tabela_projetos_empresas()