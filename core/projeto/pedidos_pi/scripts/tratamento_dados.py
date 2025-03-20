import os
import sys
from dotenv import load_dotenv

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

#sys.path
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, 'scripts_public'))
sys.path.append(SCRIPTS_PUBLIC_PATH)

from processar_excel import processar_excel

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

if __name__ == "__main__":
    processar_dados()
