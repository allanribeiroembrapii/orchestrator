import os
import inspect

def apagar_arquivos_pasta(caminho_pasta):
    """
    Função para apagar todos os arquivos de uma pasta.
        caminho_pasta: str - Caminho da pasta a ser apagada.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        try:
            # Verifica se o caminho é válido
            if not os.path.isdir(caminho_pasta):
                print(f"O caminho {caminho_pasta} não é uma pasta válida.")
                return
            
            # Lista todos os arquivos na pasta
            arquivos = os.listdir(caminho_pasta)
            
            # Apaga cada arquivo na pasta
            for arquivo in arquivos:
                caminho_arquivo = os.path.join(caminho_pasta, arquivo)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)
        except Exception as e:
            print(f"Ocorreu um erro ao apagar os arquivos: {e}")
            
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")
