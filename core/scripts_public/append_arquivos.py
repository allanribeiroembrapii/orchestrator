import os
import sys
import pandas as pd
from datetime import datetime
import win32com.client as win32
import pythoncom
import shutil
import stat

def remove_protection(file_path, temp_folder):
    """
    Remove a proteção de um arquivo Excel e salva uma cópia sem proteção.
    
    Args:
        file_path: Caminho do arquivo Excel protegido
        temp_folder: Pasta temporária para salvar o arquivo sem proteção
        
    Returns:
        str: Caminho do arquivo sem proteção
    """
    try:
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        
        excel = win32.DispatchEx('Excel.Application')
        workbook = excel.Workbooks.Open(file_path)
        base_name = os.path.basename(file_path)
        new_file_path = os.path.join(temp_folder, base_name)
        workbook.SaveAs(new_file_path, FileFormat=51)  # FileFormat=51 is for .xlsx files
        workbook.Close(False)
        excel.Application.Quit()
        
        # Uninitialize COM when done
        pythoncom.CoUninitialize()
        
        return new_file_path
    except Exception as e:
        print(f"ERRO ao remover proteção do arquivo {file_path}: {e}")
        raise

def append_excel_files(diretorio, nome_arquivo):
    """
    Concatena múltiplos arquivos Excel em um único arquivo.
    
    Args:
        diretorio: Diretório base do projeto
        nome_arquivo: Nome base para o arquivo final
    """
    print(f"Processando arquivos Excel para {nome_arquivo}...")
    
    # Obtém a data atual no formato aaaa.mm.dd
    data_atual = datetime.now().strftime('%Y.%m.%d')
    novo_nome = f"{nome_arquivo}.xlsx"

    input_folder = os.path.join(diretorio, 'step_1_data_raw')
    output_folder = os.path.join(diretorio, 'step_2_stage_area')
    
    # Verificar se as pastas existem
    if not os.path.isdir(input_folder):
        print(f"ERRO: A pasta de entrada '{input_folder}' não existe")
        print("Criando a pasta...")
        os.makedirs(input_folder, exist_ok=True)
    
    if not os.path.isdir(output_folder):
        print(f"ERRO: A pasta de saída '{output_folder}' não existe")
        print("Criando a pasta...")
        os.makedirs(output_folder, exist_ok=True)
    
    # Apagar os arquivos da output_folder
    if os.path.exists(output_folder) and os.path.isdir(output_folder):
        for file in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'AVISO: Falha ao deletar {file_path}. Razão: {e}')
    

    # Criar pasta temporária para arquivos sem proteção
    data_temp_folder = os.path.join(input_folder, 'data_temp')
    if not os.path.exists(data_temp_folder):
        os.makedirs(data_temp_folder)

    # Listar todos os arquivos Excel na pasta de entrada
    all_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
                if f.endswith('.xlsx') and not os.path.isdir(os.path.join(input_folder, f))]
    
    if not all_files:
        print(f"AVISO: Nenhum arquivo Excel encontrado na pasta '{input_folder}'")
        # Limpar pasta temporária
        if os.path.exists(data_temp_folder):
            shutil.rmtree(data_temp_folder)
        return
    
    try:
        if len(all_files) == 1:
            # Caso tenha apenas um arquivo, copie, renomeie e mova para a pasta de destino
            file = all_files[0]
            print(f"Processando arquivo único: {os.path.basename(file)}")
            unprotected_file = remove_protection(file, data_temp_folder)
            novo_caminho = os.path.join(output_folder, novo_nome)
            shutil.copy2(unprotected_file, novo_caminho)  # Faz a cópia e renomeia o arquivo
            print(f"Arquivo processado e salvo como: {novo_nome}")
        else:
            # Caso tenha mais de um arquivo, concatene-os
            print(f"Concatenando {len(all_files)} arquivos Excel...")
            data_frames = []

            for file in all_files:
                print(f"Processando: {os.path.basename(file)}")
                unprotected_file = remove_protection(file, data_temp_folder)
                df = pd.read_excel(unprotected_file)
                df.insert(0, 'ID', range(1, 1 + len(df)))
                df.insert(1, 'data_dados', datetime.now().strftime('%Y-%m-%d'))
                data_frames.append(df)

            final_df = pd.concat(data_frames, ignore_index=True)
            print(f"Total de {len(final_df)} linhas após concatenação")

            output_file = os.path.join(output_folder, novo_nome)
            final_df.to_excel(output_file, index=False)
            print(f"Arquivo concatenado salvo como: {novo_nome}")
    
    except Exception as e:
        print(f"ERRO durante o processamento dos arquivos Excel: {e}")
        raise
    
    finally:
        # Apaga a pasta data_temp e todo o seu conteúdo
        if os.path.exists(data_temp_folder):
            try:
                shutil.rmtree(data_temp_folder)
                print("Pasta temporária removida com sucesso")
            except Exception as e:
                print(f"AVISO: Não foi possível remover a pasta temporária: {e}")
