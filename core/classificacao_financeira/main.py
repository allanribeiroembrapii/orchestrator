from start_clean import start_clean
from core.classificacao_financeira.connection.sharepoint import get_files_from_sharepoint, sharepoint_post
from core.classificacao_financeira.classificar_projetos import classificar_projetos

def main_classificacao_financeira():
    start_clean()
    get_files_from_sharepoint()
    classificar_projetos()
    sharepoint_post()


if __name__ == "__main__":
    main_classificacao_financeira()