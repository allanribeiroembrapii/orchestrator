import os
import shutil

def copiar_e_renomear_arquivos(origens, destino, renomeios):
    
    for chave, caminho_origem in origens.items():
        # Verifica se o arquivo de origem existe
        if not os.path.isfile(caminho_origem):
            print(f"Atenção: O arquivo {caminho_origem} não foi encontrado.")
            continue
        
        arquivo_destino = os.path.join(destino, renomeios[chave])
        
        # Copia e renomeia o arquivo
        shutil.copy2(caminho_origem, arquivo_destino)