import os
import sys
from dotenv import load_dotenv

# carregar .env
load_dotenv()
# Carrega o .env da raiz do projeto para obter ROOT_PIPELINE
load_dotenv(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"
    )
)
ROOT = os.getenv("ROOT_PIPELINE")

# Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, "scripts_public"))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, "unidade_embrapii", "info_unidades"))
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "scripts"))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, "step_3_data_processed"))

# Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)
sys.path.append(SCRIPTS_PUBLIC_PATH)
sys.path.append(SCRIPTS_PATH)

# Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import (
    copiar_arquivos_finalizados_para_dwpii,
)
from scripts_public.processar_excel import processar_excel

# from tratamento_dados import processar_dados
from .scripts.criar_tabela_ue_linhas_atuacao import criar_tabela_ue_linhas_atuacao
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta

STEP_1_DATA_RAW = os.path.abspath(os.path.join(CURRENT_DIR, "step_1_data_raw"))
STEP_2_STAGE_AREA = os.path.abspath(os.path.join(CURRENT_DIR, "step_2_stage_area"))
STEP_3_DATA_PROCESSED = os.path.abspath(os.path.join(CURRENT_DIR, "step_3_data_processed"))


def main_info_unidades(driver):
    apagar_arquivos_pasta(STEP_1_DATA_RAW)
    apagar_arquivos_pasta(STEP_2_STAGE_AREA)
    apagar_arquivos_pasta(STEP_3_DATA_PROCESSED)
    link = "https://srinfo.embrapii.org.br/units/list/"
    nome_arquivo = "info_unidades_embrapii"
    baixar_e_juntar_arquivos(driver, link, CURRENT_DIR, nome_arquivo)
    processar_dados()
    criar_tabela_ue_linhas_atuacao()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


# Definições dos caminhos e nomes de arquivos
origem = os.path.join(ROOT, "unidade_embrapii", "info_unidades", "step_2_stage_area")
destino = os.path.join(ROOT, "unidade_embrapii", "info_unidades", "step_3_data_processed")
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
    "Unidade EMBRAPII": "unidade_embrapii",
    "Tipo de Instituição": "tipo_instituicao",
    "Chamada de Credenciamento": "chamada_credenciamento",
    "Cidade": "municipio",
    "Estado": "uf",
    "Competências Técnicas": "competencias_tecnicas",
    "Status de Credenciamento": "status_credenciamento",
    "Coordenador": "coordenador",
    "Email do coordenador": "coordenador_email",
    "Telefone do coordenador": "coordenador_telefone",
    "Celular do coordenador": "coordenador_celular",
    "Responsável EMBRAPII": "embrapii_responsavel",
    "Responsável institucional": "ue_responsavel_institucional",
    "Telefone do responsável institucional": "ue_responsavel_institucional_telefone",
    "Celular do responsável institucional": "ue_responsavel_institucional_celular",
    "Responsável comercial": "ue_responsavel_comercial",
    "Telefone do responsável comercial": "ue_responsavel_comercial_telefone",
    "Celular do responsável comercial": "ue_responsavel_comercial_celular",
    "Assinatura do plano de ação": "assinatura_plano_acao",
}


def processar_dados():
    processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)


if __name__ == "__main__":
    main_info_unidades()
