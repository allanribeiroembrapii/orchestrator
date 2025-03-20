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
origem = os.path.join(ROOT, 'projeto', 'macroentregas', 'step_2_stage_area')
destino = os.path.join(ROOT, 'projeto', 'macroentregas', 'step_3_data_processed')
nome_arquivo = "macroentregas.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Código EMBRAPII",
    "ME",
    "Projeto",
    "Descrição dos entregáveis desta macroentrega",
    "Valor aportado EMBRAPII",
    "Valor aportado Empresa",
    "Valor aportado pela Unidade",
    "Início planejado",
    "Término planejado",
    "Início real",
    "Término real",
    "Versão do replanejmanto",
    "Percentual executado",
    "Em atraso?",
    "Data de aceitação",
    "Observações ou comentários",
]

novos_nomes_e_ordem = {
    "Código EMBRAPII": "codigo_embrapii",
    "ME": "num_macroentrega",
    "Projeto": "titulo",
    "Descrição dos entregáveis desta macroentrega": "descricao_macroentrega",
    "Valor aportado EMBRAPII": "valor_embrapii_me",
    "Valor aportado Empresa": "valor_empresa_me",
    "Valor aportado pela Unidade": "valor_unidade_embrapii_me",
    "Início planejado": "data_inicio_planejado",
    "Término planejado": "data_termino_planejado",
    "Início real": "data_inicio_real",
    "Término real": "data_termino_real",
    "Versão do replanejmanto": "versao",
    "Percentual executado": "percentual_executado",
    "Em atraso?": "me_atrasada",
    "Data de aceitação": "data_aceitacao",
    "Observações ou comentários": "observacoes", 
}

# Campos de data e valor
campos_data = ['data_inicio_planejado', 'data_termino_planejado', 'data_inicio_real', 'data_termino_real', 'data_aceitacao']
campos_valor = ['valor_embrapii_me', 'valor_empresa_me', 'valor_unidade_embrapii_me']

def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)

if __name__ == "__main__":
    processar_dados()
