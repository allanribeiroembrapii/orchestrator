import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'projeto', 'pedidos_pi'))
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
from scripts_public.filtrar_projetos import filtrar_projetos

#Definição da função
def main_pedidos_pi(driver):
    link = 'https://srinfo.embrapii.org.br/projectmonitoring/ip/'
    nome_arquivo = 'pedidos_pi'
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)



# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, 'projeto', 'pedidos_pi', 'step_2_stage_area')
destino = os.path.join(ROOT, 'projeto', 'pedidos_pi', 'step_3_data_processed')
nome_arquivo = "pedidos_pi.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Projeto",
    "Unidade EMBRAPII",
    "Título",
    "Tipo",
    "País Emissor",
    "Data do Pedido",
    "Número do Pedido",
    "Direitos da Unidade",
    "Link",
    "Observações ou comentários",
    "Moderação",
]

novos_nomes_e_ordem = {
    "Projeto": "codigo_projeto",
    "Unidade EMBRAPII": "unidade_embrapii",
    "Título": "titulo_pedido",
    "Tipo": "tipo_pedido",
    "País Emissor": "pais_emissor",
    "Data do Pedido": "data_pedido",
    "Número do Pedido": "numero_pedido",
    "Direitos da Unidade": "percentual_direito_ue",
    "Link": "link_pedido",
    "Observações ou comentários": "observacoes",
    "Moderação": "moderacao", 
}

# Campos de data e valor
campos_data = ['data_pedido']
campos_valor = []

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)
    filtrar_projetos(arquivo_destino)


if __name__ == "__main__":
    main_pedidos_pi()