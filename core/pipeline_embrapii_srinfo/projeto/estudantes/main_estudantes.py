import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'projeto', 'estudantes'))
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
# from scripts.tratamento_dados import processar_dados

#Definição da função
def main_estudantes(driver):
    link = 'https://srinfo.embrapii.org.br/projects/student/list'
    nome_arquivo = 'estudantes'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)



# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'projeto', 'estudantes', 'step_2_stage_area')
destino = os.path.join(ROOT, 'projeto', 'estudantes', 'step_3_data_processed')
nome_arquivo = "estudantes.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Código do projeto / Projeto Espelho",
    "Unidade EMBRAPII",
    "CPF",
    "Nome",
    "Titulação",
    "Formação Acadêmica",
    "Nível de formação (Em andamento)",
    "Atividade / Função",
    "Disponibilidade (horas/mês)",
    "Data de início das atividades no projeto",
    "Data de término das atividades no projeto",
    "Possui Bolsa",
    "Observações ou comentários",
]

novos_nomes_e_ordem = {
    "Código do projeto / Projeto Espelho": "codigo_projeto",
    "Unidade EMBRAPII": "unidade_embrapii",
    "CPF": "cpf",
    "Nome": "nome",
    "Titulação": "titulacao",
    "Formação Acadêmica": "formacao",
    "Nível de formação (Em andamento)": "nivel_formacao_cursando",
    "Atividade / Função": "atividade",
    "Disponibilidade (horas/mês)": "disponibilidade",
    "Data de início das atividades no projeto": "data_inicio_atividades",
    "Data de término das atividades no projeto": "data_termino_atividades",
    "Possui Bolsa": "bolsista",
    "Observações ou comentários": "observacoes",
}

# Campos de data e valor
campos_data = ['data_inicio_atividades', 'data_termino_atividades']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data)



#Executar função
if __name__ == "__main__":
    main_estudantes()