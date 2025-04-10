import os
import sys
from dotenv import load_dotenv
import pandas as pd

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'unidade_embrapii', 'equipe_ue'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(SCRIPTS_PATH)

#Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta
from scripts_public.processar_excel import processar_excel
# from tratamento_dados import processar_dados
from criar_tabela_ue_linhas_atuacao import criar_tabela_ue_linhas_atuacao


STEP_1_DATA_RAW = os.path.abspath(os.path.join(CURRENT_DIR, 'step_1_data_raw'))
STEP_2_STAGE_AREA = os.path.abspath(os.path.join(CURRENT_DIR, 'step_2_stage_area'))
STEP_3_DATA_PROCESSED = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))

def main_equipe_ue(driver):
    apagar_arquivos_pasta(STEP_1_DATA_RAW)
    apagar_arquivos_pasta(STEP_2_STAGE_AREA)
    apagar_arquivos_pasta(STEP_3_DATA_PROCESSED)
    link = 'https://srinfo.embrapii.org.br/people/list/'
    nome_arquivo = 'equipe_ue'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    ajustar_equipe_ue()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'unidade_embrapii', 'equipe_ue', 'step_2_stage_area')
destino = os.path.join(ROOT, 'unidade_embrapii', 'equipe_ue', 'step_3_data_processed')
nome_arquivo = "equipe_ue.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade EMBRAPII",
    "CPF",
    "Nome",
    "Titulação",
    "Formação Acadêmica",
    "Link Lattes",
    "Atividade / Função",
    "Data de entrada",
    "Data de saída",
    "Disponibilidade (horas/mês)",
]

novos_nomes_e_ordem = {
    'CPF': 'cpf',
    'Unidade EMBRAPII': 'unidade_embrapii',
    'Nome': 'nome',
    'Titulação': 'titulacao',
    'Formação Acadêmica': 'formacao_academica',
    'Link Lattes': 'link_lattes',
    'Atividade / Função': 'atividade_funcao',
    'Data de entrada': 'data_entrada',
    'Data de saída': 'data_saida',
    'Disponibilidade (horas/mês)': 'disponibilidade_horas_mes',
}


def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)


def ajustar_equipe_ue(arquivo_destino=arquivo_destino):
    equipe_ue = pd.read_excel(arquivo_destino)

    nivel_titulacao = {
        'Ensino Médio': 1,
        'Nível Técnico': 2,
        'Graduação': 3,
        'Especialização': 4,
        'Mestrado': 5,
        'Doutorado': 6,
        'Pós-Doutorado': 7,
    }

    # Etapa 1: Criar a coluna 'ano_entrada' a partir da coluna 'data_entrada'
    equipe_ue['ano_entrada'] = pd.to_datetime(equipe_ue['data_entrada'], dayfirst=True, errors='coerce').dt.year

    # Etapa 2: Analisar os valores da coluna 'cpf' para cada ano e ajustar o nível de titulação
    def obter_maior_titulacao(grupo):
        idx_maior_titulacao = grupo['titulacao'].map(nivel_titulacao).idxmax()
        return grupo.loc[idx_maior_titulacao]

    equipe_ue = equipe_ue.groupby(['ano_entrada', 'cpf'], group_keys=False).apply(obter_maior_titulacao)
    equipe_ue['titulacao_maior'] = equipe_ue['titulacao']

    # Etapa 3: Criar a coluna 'titulacao_maior_simp'
    def simplificar_titulacao(titulacao):
        if titulacao in ['Ensino Médio', 'Nível Técnico']:
            return 'Médio/Técnico'
        elif titulacao == 'Graduação':
            return 'Graduação'
        else:
            return 'Pós-Graduação'

    equipe_ue['titulacao_maior_simp'] = equipe_ue['titulacao_maior'].apply(simplificar_titulacao)

    # Salvar o resultado no local parametrizado em "arquivo_destino"
    equipe_ue.to_excel(arquivo_destino, index=False)

if __name__ == "__main__":
    main_equipe_ue()