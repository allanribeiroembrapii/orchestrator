import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Importar configurações centralizadas
from config.module_configs import get_config

# Carregar .env
load_dotenv()
ROOT = os.getenv("ROOT")

# Adicionar caminhos ao sys.path
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "scripts_public"))

# Importar módulos necessários
from scripts_public.scripts_public import baixar_e_juntar_arquivos
from scripts_public.processar_excel import processar_excel
from scripts_public.apagar_arquivos_pasta import apagar_arquivos_pasta
from scripts_public.copiar_arquivos_finalizados_para_dwpii import (
    copiar_arquivos_finalizados_para_dwpii,
)


def baixar_info_empresas(driver, config=None):
    """
    Baixa e processa informações de empresas do SRInfo.

    Args:
        driver: Instância do WebDriver
        config: Configurações do módulo
    """
    if config is None:
        config = get_config("info_empresas")

    # Extrair valores das configurações
    caminhos = config["caminhos"]
    link = config["link"]
    nome_arquivo = config["nome_arquivo"]

    # Garantir que as pastas existam
    for caminho in caminhos.values():
        os.makedirs(caminho, exist_ok=True)

    # Limpar as pastas
    print("Limpando pastas de dados...")
    apagar_arquivos_pasta(caminhos["step_1_data_raw"])
    apagar_arquivos_pasta(caminhos["step_2_stage_area"])
    apagar_arquivos_pasta(caminhos["step_3_data_processed"])

    # Baixar dados
    print(f"Baixando informações de empresas de {link}...")
    baixar_e_juntar_arquivos(driver, link, caminhos["current_dir"], nome_arquivo)

    # Processar dados
    print("Processando dados de empresas...")
    processar_dados_empresas(config)


def processar_info_empresas(config=None):
    """
    Processa as informações de empresas já baixadas.

    Args:
        config: Configurações do módulo
    """
    if config is None:
        config = get_config("info_empresas")

    agregar_dados_porte_empresa(config)
    copiar_arquivos_finalizados_para_dwpii(config["caminhos"]["step_3_data_processed"])


def main(driver=None, apenas_baixar=False, apenas_processar=False, config_override=None):
    """
    Função principal para baixar e processar informações de empresas.
    Busca automaticamente suas configurações.

    Args:
        driver: Instância do WebDriver, necessário para baixar dados
        apenas_baixar: Se True, apenas baixa os dados sem processar
        apenas_processar: Se True, apenas processa os dados já baixados
        config_override: Configurações para sobrescrever as padrões

    Returns:
        bool: True se a operação foi concluída com sucesso
    """
    # Obter configurações
    config = get_config("info_empresas")
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

    if not apenas_processar and driver is None:
        print("ERRO: Driver é necessário para baixar dados.")
        return False

    try:
        if apenas_processar:
            print("Apenas processando dados já baixados...")
            processar_info_empresas(config)
        elif apenas_baixar:
            print("Apenas baixando dados...")
            baixar_info_empresas(driver, config)
        else:
            print("Baixando e processando dados...")
            baixar_info_empresas(driver, config)
            processar_info_empresas(config)

        return True
    except Exception as e:
        print(f"ERRO durante a execução: {e}")
        return False


# Manter as funções antigas para compatibilidade
def main_info_empresas_baixar(driver):
    return baixar_info_empresas(driver)


def main_info_empresas_processar():
    return processar_info_empresas()


def agregar_dados_porte_empresa(config=None):
    """
    Agrega dados de porte das empresas ao arquivo de informações de empresas.

    Args:
        config: Configurações do módulo
    """
    if config is None:
        config = get_config("info_empresas")

    print("Agregando dados de porte das empresas...")

    path_empresas = os.path.join(config["caminhos"]["step_3_data_processed"], "info_empresas.xlsx")
    path_porte = os.path.join(
        ROOT,
        "core",
        "projeto",
        "projetos_empresas",
        "step_3_data_processed",
        "informacoes_empresas.xlsx",
    )

    # Verificar se os arquivos existem
    if not os.path.exists(path_empresas):
        print(f"ERRO: Arquivo de empresas não encontrado: {path_empresas}")
        return

    try:
        # Carregar dados de empresas
        print(f"Carregando dados de empresas de: {path_empresas}")
        df_empresas = pd.read_excel(path_empresas)

        # Verificar se o arquivo de porte existe
        if os.path.exists(path_porte):
            print(f"Carregando dados de porte de: {path_porte}")
            df_porte = pd.read_excel(path_porte)

            # Código comentado para futura implementação
            # colunas_remover = [
            #     'Código',
            #     'CNAE',
            #     'Empresas',
            #     'CNAE_parte',
            #     'cnae_divisao',
            # ]
            # df_porte = df_porte.drop(columns=colunas_remover)
            #
            # df_empresas = df_empresas.merge(df_porte, left_on='cnpj', right_on='CNPJ', how='left')
            # colunas_remover = [
            #     'CNPJ',
            # ]
            # df_empresas = df_empresas.drop(columns=colunas_remover)
            #
            # novos_nomes = {
            #     'Faixa de faturamento declarada':'faixa_faturamento',
            #     'Faixa de empregados declarada':'faixa_empregados',
            # }
            # df_empresas = df_empresas.rename(columns=novos_nomes)
        else:
            print(f"AVISO: Arquivo de porte não encontrado: {path_porte}")
            print("Continuando apenas com os dados de empresas...")

        # Remover duplicatas
        print("Removendo duplicatas baseadas no CNPJ...")
        df_empresas = df_empresas.drop_duplicates(subset="cnpj")
        print(f"Total de {len(df_empresas)} empresas únicas")

        # Salvar arquivo processado
        print(f"Salvando arquivo processado em: {path_empresas}")

        # Garantir que o diretório de destino existe
        os.makedirs(os.path.dirname(path_empresas), exist_ok=True)

        df_empresas.to_excel(path_empresas, index=False)
        print("Arquivo salvo com sucesso")

    except Exception as e:
        print(f"ERRO durante o processamento dos dados de empresas: {e}")


def processar_dados_empresas(config=None):
    """
    Processa os dados brutos de empresas, selecionando campos de interesse e renomeando colunas.

    Args:
        config: Configurações do módulo
    """
    if config is None:
        config = get_config("info_empresas")

    print("Processando dados brutos de empresas...")

    # Definir caminhos com base na configuração
    caminhos = config["caminhos"]
    nome_arquivo = config["nome_arquivo"] + ".xlsx"
    arquivo_origem = os.path.join(caminhos["step_2_stage_area"], nome_arquivo)
    arquivo_destino = os.path.join(caminhos["step_3_data_processed"], nome_arquivo)

    # Obter campos de interesse e novos nomes
    campos_interesse = config["campos_interesse"]
    novos_nomes_e_ordem = config["novos_nomes_e_ordem"]

    # Verificar se o arquivo de origem existe
    if not os.path.exists(arquivo_origem):
        print(f"ERRO: Arquivo de origem não encontrado: {arquivo_origem}")
        print("Verifique se o download e a junção dos arquivos foram realizados corretamente.")
        return

    try:
        # Garantir que o diretório de destino existe
        os.makedirs(os.path.dirname(arquivo_destino), exist_ok=True)

        # Processar o arquivo
        print(f"Processando arquivo: {arquivo_origem}")
        processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)
        print(f"Arquivo processado e salvo em: {arquivo_destino}")

    except Exception as e:
        print(f"ERRO durante o processamento do arquivo: {e}")
