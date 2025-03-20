import os
from core.atualizar_google_sheets.puxar_planilhas_sharepoint import puxar_planilhas
from core.atualizar_google_sheets.atualizacao_gsheet import atualizar_gsheet
from config.module_configs import get_config


def main(config_override=None):
    """
    Função principal para atualizar o Google Sheets com dados do SharePoint.
    Busca automaticamente as configurações do módulo.

    Args:
        config_override (dict, optional): Configurações para sobrescrever as padrões.
            Pode conter 'url' e/ou 'caminhos_arquivos'.

    Returns:
        bool: True se a operação foi concluída com sucesso.
    """
    # Obter configurações
    config = get_config("google_sheets")
    if config_override:
        # Atualizar configurações com as fornecidas
        if isinstance(config_override, dict):
            for key, value in config_override.items():
                if key in config:
                    if isinstance(value, dict) and isinstance(config[key], dict):
                        # Para dicionários aninhados, atualizar em vez de substituir
                        config[key].update(value)
                    else:
                        config[key] = value

    # Extrair valores das configurações
    url = config["url"]
    caminhos_arquivos = config["caminhos_arquivos"]

    try:
        # Puxar planilhas do SharePoint
        print("Buscando planilhas do SharePoint...")
        puxar_planilhas()

        # Atualizar cada aba
        print(f"Atualizando Google Sheets: {url}")
        for aba, caminho_arquivo in caminhos_arquivos.items():
            print(f"Processando aba: {aba}")
            atualizar_gsheet(url, aba, caminho_arquivo)

        print("Atualização do Google Sheets concluída com sucesso.")
        return True
    except Exception as e:
        print(f"Erro durante a atualização do Google Sheets: {e}")
        return False


if __name__ == "__main__":
    main()
