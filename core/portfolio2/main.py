from core.portfolio2.start_clean import start_clean
from core.portfolio2.connection.sharepoint import get_files_from_sharepoint, sharepoint_post
from core.portfolio2.processar_portfolio2 import processar_portfolio2


def main_portfolio2():
    start_clean()
    get_files_from_sharepoint()
    processar_portfolio2()
    sharepoint_post()


if __name__ == "__main__":
    main_portfolio2()