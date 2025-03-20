import os
import sys
import pandas as pd
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'projeto', 'projetos'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

#Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.processar_excel import processar_excel
# from tratamento_dados import processar_dados

#Definição da função
def main_projetos(driver):
    link = 'https://srinfo.embrapii.org.br/projects/list/'
    nome_arquivo = 'projetos'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'projeto', 'projetos', 'step_2_stage_area')
destino = os.path.join(ROOT, 'projeto', 'projetos', 'step_3_data_processed')
nome_arquivo = "projetos.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Código Interno",
    "Unidade EMBRAPII",
    "Código EMBRAPII",
    "Tipo de projeto",
    "Status",
    "Título",
    "Título público",
    "Objetivo",
    "Descrição pública",
    "Data da Avaliação",
    "Nota da Avaliação",
    "Observações ou comentários",
    "Tags",
]

novos_nomes_e_ordem = {
    'Código EMBRAPII':'codigo_projeto',
    'Código Interno':'codigo_interno',
    'Unidade EMBRAPII':'unidade_embrapii',
    'Tipo de projeto':'tipo_projeto',
    'Status':'status',
    'Título':'titulo',
    'Título público':'titulo_publico',
    'Objetivo':'objetivo',
    'Descrição pública':'descricao_publica',
    'Data da Avaliação':'data_avaliacao',
    'Nota da Avaliação':'nota_avaliacao',
    'Observações ou comentários':'observacoes',
    'Tags':'tags',
}

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)
    filtrar_projetos(arquivo_destino)


def filtrar_projetos(caminho):
    df = pd.read_excel(caminho)
    df_filtrado = df[df['status'] != 'Desqualificado']
    df_filtrado.to_excel(caminho, index=False)

#Executar função
if __name__ == "__main__":
    main_projetos()