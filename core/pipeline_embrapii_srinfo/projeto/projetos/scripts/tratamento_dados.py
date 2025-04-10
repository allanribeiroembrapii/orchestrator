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

if __name__ == "__main__":
    processar_dados()
