import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'projeto', 'sebrae'))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'scripts'))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, 'step_3_data_processed'))
pasta_download = os.getenv('PASTA_DOWNLOAD')

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

#Importar módulos necessários
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.processar_excel import processar_excel
from scripts_public.baixar_dados_srinfo import baixar_dados_srinfo
from scripts_public.mover_arquivos import mover_arquivos_excel
from scripts_public.append_arquivos import append_excel_files

#Definição da função
def main_sebrae(driver):
    link1 = 'https://srinfo.embrapii.org.br/partnerships/sebrae_4_contrato/list'
    link2 = 'https://srinfo.embrapii.org.br/partnerships/sebrae_ciclo_integrado/list'
    link3 = 'https://srinfo.embrapii.org.br/partnerships/sebrae_ciclo_2/list'
    baixar_dados_srinfo(driver, link1, 1, sebrae = True)
    baixar_dados_srinfo(driver, link2, 1, sebrae = True)
    baixar_dados_srinfo(driver, link3, 1, sebrae = True)
    mover_arquivos_excel(3, pasta_download, CURRENT_DIR, 'sebrae_srinfo1')
    append_excel_files(CURRENT_DIR, 'sebrae_srinfo')
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'projeto', 'sebrae', 'step_2_stage_area')
destino = os.path.join(ROOT, 'projeto', 'sebrae', 'step_3_data_processed')
nome_arquivo = "sebrae_srinfo.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Código da Negociação",
    "Unidade EMBRAPII",
    "Modalidade de Financiamento",
    "Status da solicitação de reserva",
    "Data de solicitação",
    "Data de reserva",
    "Expiração da reserva",
    "Data de repasse realizado",
    "Status da negociação",
    "Recursos EMBRAPII",
    "Recursos SEBRAE",
    "Valor aportado Empresa*",
    "Valor aportado pela Unidade",
]

novos_nomes_e_ordem = {
    "Código da Negociação": 'codigo_negociacao',
    "Unidade EMBRAPII": 'unidade_embrapii',
    "Modalidade de Financiamento": 'modalidade_financiamento',
    "Status da solicitação de reserva": 'status_solicitacao_reserva',
    "Data de solicitação": 'data_solicitacao',
    "Data de reserva": 'data_reserva',
    "Expiração da reserva": 'data_expiracao_reserva',
    "Data de repasse realizado": 'data_repasse_realizado',
    "Status da negociação": 'status_negociacao',
    "Recursos EMBRAPII": 'valor_embrapii',
    "Recursos SEBRAE": 'valor_sebrae',
    "Valor aportado Empresa*": 'valor_empresa',
    "Valor aportado pela Unidade": 'valor_unidade_embrapii',
}

# Campos de data e valor
campos_data = ['data_solicitacao', 'data_reserva', 'data_expiracao_reserva', 'data_repasse_realizado']
campos_valor = ['valor_embrapii', 'valor_sebrae', 'valor_empresa', 'valor_unidade_embrapii']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)

#Executar função
if __name__ == "__main__":
    main_sebrae()
