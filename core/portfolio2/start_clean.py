import os
import shutil
import inspect

def start_clean():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Corrigindo o caminho base para ser absoluto e garantindo que funciona em qualquer sistema operacional
    base_path = os.path.abspath('./core/portfolio2/data')

    # Verifica se a pasta data existe e apaga se existir
    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    # Cria a pasta data e as subpastas necessárias
    os.makedirs(base_path)

    folders_to_create = ['step_1_data_raw', 'step_2_stage_area', 'step_3_data_processed']
    for folder in folders_to_create:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path)

    print("🟢 " + inspect.currentframe().f_code.co_name)
