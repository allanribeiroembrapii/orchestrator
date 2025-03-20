import os
from dotenv import load_dotenv
from core.scripts_public.baixar_dados_srinfo import baixar_dados_srinfo
from core.scripts_public.mover_arquivos import mover_arquivos_excel
from core.scripts_public.append_arquivos import append_excel_files

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


def baixar_e_juntar_arquivos(
    driver, link, diretorio, nome_arquivo, num_pages=None, option1000=None, sebrae=False
):

    pasta_download = os.getenv("PASTA_DOWNLOAD")

    numero_arquivos = baixar_dados_srinfo(driver, link, num_pages, option1000, sebrae)
    mover_arquivos_excel(numero_arquivos, pasta_download, diretorio, nome_arquivo)
    append_excel_files(diretorio, nome_arquivo)


def criar_estrutura_diretorios():
    """
    Cria a estrutura básica de diretórios para o projeto.
    """
    ROOT = os.getenv("ROOT")

    # Diretórios principais
    diretorios_principais = [
        os.path.join(ROOT, "core", "empresa"),
        os.path.join(ROOT, "core", "analises_relatorios"),
        os.path.join(ROOT, "core", "unidade_embrapii"),
        os.path.join(ROOT, "core", "projeto"),
        os.path.join(ROOT, "core", "prospeccao"),
        os.path.join(ROOT, "core", "negociacoes"),
        os.path.join(ROOT, "core", "cg_classificacao_projetos"),
        os.path.join(ROOT, "core", "atualizar_google_sheets"),
        os.path.join(ROOT, "core", "qim_ues"),
        os.path.join(ROOT, "core", "DWPII_backup"),
        os.path.join(ROOT, "core", "DWPII_copy"),
        os.path.join(ROOT, "core", "DWPII_up"),
        os.path.join(ROOT, "core", "logs"),
        os.path.join(ROOT, "core", "lookup_tables"),
    ]

    # Criar diretórios principais
    for diretorio in diretorios_principais:
        os.makedirs(diretorio, exist_ok=True)
        print(f"Diretório verificado/criado: {diretorio}")

    return True
