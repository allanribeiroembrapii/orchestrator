import os
import shutil
from glob import glob
import inspect

def mover_arquivos_excel(numero_arquivos, pasta_atual, novo_caminho):
    """
    Função para mover arquivos de uma pasta para outra.
        numero_arquivos: int - número de arquivos a serem movidos
        pasta_atual: str - caminho da pasta atual
        novo_caminho: str - caminho da pasta de destino
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        #Lista todos os arquivos Excel na pasta atual
        files = glob(os.path.join(pasta_atual, '*.xlsx'))
        
        #Seleciona os n arquivos mais recentes
        files_to_move = files[:numero_arquivos]
        
        # Move os arquivos selecionados
        for i, file in enumerate(files_to_move, start=1):
            try:
                shutil.move(file, novo_caminho)
            except Exception as e:
                print(f'Erro ao mover {file} para {novo_caminho}. Razão: {e}')

        print("🟢 " + inspect.currentframe().f_code.co_name)

    except Exception as e:
        print(f"🔴 Erro: {e}")


def mover_arquivo_especifico(nome_arquivo, pasta_atual, novo_caminho):
    """
    Função para mover um arquivo específico de uma pasta para outra.
        nome_arquivo: str - nome do arquivo (com extensão)
        pasta_atual: str - caminho da pasta onde o arquivo está
        novo_caminho: str - caminho da pasta de destino
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        caminho_origem = os.path.join(pasta_atual, nome_arquivo)
        caminho_destino = os.path.join(novo_caminho, nome_arquivo)

        if os.path.exists(caminho_origem):
            shutil.move(caminho_origem, caminho_destino)
            print(f"✅ Arquivo '{nome_arquivo}' movido com sucesso para '{novo_caminho}'")
        else:
            print(f"❌ Arquivo '{nome_arquivo}' não encontrado em '{pasta_atual}'")

        print("🟢 " + inspect.currentframe().f_code.co_name)

    except Exception as e:
        print(f"🔴 Erro ao mover arquivo: {e}")