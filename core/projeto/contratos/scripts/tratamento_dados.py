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
origem = os.path.join(ROOT, 'projeto', 'contratos', 'step_2_stage_area')
destino = os.path.join(ROOT, 'projeto', 'contratos', 'step_3_data_processed')
nome_arquivo = "contratos.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Código",
    "Unidade EMBRAPII",
    "Data do contrato",
    "Parceria / Programa",
    "Call",
    "Cooperação Internacional",
    "Modalidade de financiamento",
    "Projeto",
    "Data de início",
    "Data de término",
    "É usada obrigatoriedade?",
    "Nível de maturidade inicial",
    "Nível de maturidade final",
    "Valor aportado EMBRAPII",
    "Valor aportado Empresa",
    "Valor aportado pela Unidade",
]

novos_nomes_e_ordem = {
    'Código': 'codigo_projeto', 
    'Unidade EMBRAPII': 'unidade_embrapii', 
    'Data do contrato': 'data_contrato', 
    'Parceria / Programa': 'parceria_programa', 
    'Call': 'call', 
    'Cooperação Internacional': 'cooperacao_internacional', 
    'Modalidade de financiamento': 'modalidade_financiamento', 
    'Projeto': 'projeto', 
    'Data de início': 'data_inicio', 
    'Data de término': 'data_termino', 
    'É usada obrigatoriedade?': 'uso_recurso_obrigatorio', 
    'Nível de maturidade inicial': 'trl_inicial', 
    'Nível de maturidade final': 'trl_final', 
    'Valor aportado EMBRAPII': 'valor_embrapii', 
    'Valor aportado Empresa': 'valor_empresa', 
    'Valor aportado pela Unidade': 'valor_unidade_embrapii', 
}

# Campos de data e valor
campos_data = ['data_contrato', 'data_inicio', 'data_termino']
campos_valor = ['valor_embrapii', 'valor_empresa', 'valor_unidade_embrapii']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)

if __name__ == "__main__":
    processar_dados()
