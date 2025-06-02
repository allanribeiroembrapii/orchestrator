import os

def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é uma pasta; se não for, cria
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            return

        # Lista todos os arquivos na pasta
        arquivos = os.listdir(caminho_pasta)
        
        # Apaga cada arquivo na pasta
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
            elif os.path.isdir(caminho_arquivo):
                # Se quiser apagar subpastas também, descomente a linha abaixo
                # shutil.rmtree(caminho_arquivo)
                pass
    except Exception as e:
        print(f"Ocorreu um erro ao apagar os arquivos: {e}")
