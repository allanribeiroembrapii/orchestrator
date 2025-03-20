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

#Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(CURRENT_DIR)

#Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
from scripts_public.processar_excel import processar_excel

#Definição da função
def main_sebrae(driver):
    # Criar diretórios necessários
    for pasta in ['step_1_data_raw', 'step_2_stage_area', 'step_3_data_processed']:
        caminho = os.path.join(CURRENT_DIR, pasta)
        os.makedirs(caminho, exist_ok=True)
        print(f"Verificado/criado diretório: {caminho}")
    
    link = 'https://srinfo.embrapii.org.br/partnerships/sebrae_4_contrato/list'
    nome_arquivo = 'sebrae_srinfo'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo, num_pages=1, sebrae = True)
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
