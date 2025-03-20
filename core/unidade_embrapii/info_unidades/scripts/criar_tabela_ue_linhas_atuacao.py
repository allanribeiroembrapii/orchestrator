import os
import pandas as pd
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

def criar_tabela_ue_linhas_atuacao():
    # Caminho do arquivo Excel
    origem = os.path.join(ROOT, 'unidade_embrapii', 'info_unidades', 'step_2_stage_area')
    nome_arquivo = 'info_unidades_embrapii.xlsx'
    arquivo_origem = os.path.join(origem, nome_arquivo)
    destino = os.path.join(ROOT, 'unidade_embrapii', 'info_unidades', 'step_3_data_processed')
    arquivo_destino = os.path.join(destino, 'ue_linhas_atuacao.xlsx')

    # Ler o arquivo Excel
    df = pd.read_excel(arquivo_origem)

    # Selecionar apenas as colunas de interesse
    colunas_interesse = ["Unidade EMBRAPII", "Linhas de Atuação"]
    df_selecionado = df[colunas_interesse]

    # Renomear as colunas
    df_renomeado = df_selecionado.rename(columns={
        "Unidade EMBRAPII": "unidade_embrapii",
        "Linhas de Atuação": "linha_atuacao"
    })

    # Quebrar os valores da coluna "linha_atuacao" por ";" e transformar em linhas separadas
    df_explodido = df_renomeado.assign(linha_atuacao=df_renomeado['linha_atuacao'].str.split(';')).explode('linha_atuacao')

    # Remover espaços em branco no início e no final das células da coluna "linha_atuacao"
    df_explodido['linha_atuacao'] = df_explodido['linha_atuacao'].str.strip()

    # Remover linhas onde "linha_atuacao" está vazia
    df_explodido = df_explodido[df_explodido['linha_atuacao'] != '']

    # Garantir que o diretório de destino existe
    os.makedirs(destino, exist_ok=True)

    # Salvar o arquivo resultante
    df_explodido.to_excel(arquivo_destino, index=False)

# Exemplo de chamada da função
if __name__ == "__main__":
    criar_tabela_ue_linhas_atuacao()
