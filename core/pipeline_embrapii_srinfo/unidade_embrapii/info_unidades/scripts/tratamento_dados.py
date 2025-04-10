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
origem = os.path.join(ROOT, 'unidade_embrapii', 'info_unidades', 'step_2_stage_area')
destino = os.path.join(ROOT, 'unidade_embrapii', 'info_unidades', 'step_3_data_processed')
nome_arquivo = "info_unidades_embrapii.xlsx"
arquivo_origem = os.path.join(origem, nome_arquivo)
arquivo_destino = os.path.join(destino, nome_arquivo)

# Campos de interesse e novos nomes das colunas
campos_interesse = [
    "Unidade EMBRAPII",
    "Tipo de Instituição",
    "Chamada de Credenciamento",
    "Cidade",
    "Estado",
    "Coordenador",
    "Email do coordenador",
    "Telefone do coordenador",
    "Celular do coordenador",
    "Responsável EMBRAPII",
    "Responsável institucional",
    "Telefone do responsável institucional",
    "Celular do responsável institucional",
    "Responsável comercial",
    "Telefone do responsável comercial",
    "Celular do responsável comercial",
    "Assinatura do plano de ação",
    "Competências Técnicas",
    "Status de Credenciamento",
]

novos_nomes_e_ordem = {
    'Unidade EMBRAPII':'unidade_embrapii',
    'Tipo de Instituição':'tipo_instituicao',
    'Chamada de Credenciamento':'chamada_credenciamento',
    'Cidade':'municipio',
    'Estado':'uf',
    'Competências Técnicas':'competencias_tecnicas',
    'Status de Credenciamento':'status_credenciamento',
    'Coordenador':'coordenador',
    'Email do coordenador':'coordenador_email',
    'Telefone do coordenador':'coordenador_telefone',
    'Celular do coordenador':'coordenador_celular',
    'Responsável EMBRAPII':'embrapii_responsavel',
    'Responsável institucional':'ue_responsavel_institucional',
    'Telefone do responsável institucional':'ue_responsavel_institucional_telefone',
    'Celular do responsável institucional':'ue_responsavel_institucional_celular',
    'Responsável comercial':'ue_responsavel_comercial',
    'Telefone do responsável comercial':'ue_responsavel_comercial_telefone',
    'Celular do responsável comercial':'ue_responsavel_comercial_celular',
    'Assinatura do plano de ação':'assinatura_plano_acao',
}


def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)

if __name__ == "__main__":
    processar_dados()
