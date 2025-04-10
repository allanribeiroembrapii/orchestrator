import os
import pandas as pd
from datetime import datetime
import win32com.client as win32
import shutil
import stat

def remove_protection(file_path, temp_folder):
    excel = win32.DispatchEx('Excel.Application')
    workbook = excel.Workbooks.Open(file_path)
    base_name = os.path.basename(file_path)
    new_file_path = os.path.join(temp_folder, base_name)
    workbook.SaveAs(new_file_path, FileFormat=51)  # FileFormat=51 is for .xlsx files
    workbook.Close(False)
    excel.Application.Quit()
    return new_file_path

def append_excel_files(diretorio, nome_arquivo):

    # Obtém a data atual no formato aaaa.mm.dd
    data_atual = datetime.now().strftime('%Y.%m.%d')
    novo_nome = f"{nome_arquivo}.xlsx"

    input_folder = os.path.join(diretorio, 'step_1_data_raw')
    output_folder = os.path.join(diretorio, 'step_2_stage_area')

    #apagar os arquivos da output_folder
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Falha ao deletar {file_path}. Razão: {e}')


    data_temp_folder = os.path.join(input_folder, 'data_temp')
    if not os.path.exists(data_temp_folder):
        os.makedirs(data_temp_folder)

    all_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.xlsx')]
    if len(all_files) == 1:
        # Caso tenha apenas um arquivo, copie, renomeie e mova para a pasta de destino
        file = all_files[0]
        unprotected_file = remove_protection(file, data_temp_folder)
        novo_caminho = os.path.join(output_folder, novo_nome)
        shutil.copy2(unprotected_file, novo_caminho)  # Faz a cópia e renomeia o arquivo
    else:
        # Caso tenha mais de um arquivo, concatene-os
        data_frames = []

        for file in all_files:
            unprotected_file = remove_protection(file, data_temp_folder)
            df = pd.read_excel(unprotected_file)
            df.insert(0, 'ID', range(1, 1 + len(df)))
            df.insert(1, 'data_dados', datetime.now().strftime('%Y-%m-%d'))
            data_frames.append(df)

        final_df = pd.concat(data_frames, ignore_index=True)

        output_file = os.path.join(output_folder, novo_nome)
        final_df.to_excel(output_file, index=False)

    # Apaga a pasta data_temp e todo o seu conteúdo
    shutil.rmtree(data_temp_folder)

