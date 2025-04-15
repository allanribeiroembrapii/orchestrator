import pandas as pd
from datetime import datetime
import os

CAMINHO_REGISTRO_ENVIO = 'copy_sharepoint_atual/registro_alertas.xlsx'

def registrar_envio(id_alerta, conteudo):
    data_envio = datetime.now().strftime('%Y-%m-%d %H:%M')
    novo_envio = {
        'id': gerar_id_envio(),
        'id_alerta': id_alerta,
        'data': data_envio,
        'conteudo': conteudo
    }
    
    if os.path.exists(CAMINHO_REGISTRO_ENVIO):
        df = pd.read_excel(CAMINHO_REGISTRO_ENVIO)
        df = df._append(novo_envio, ignore_index=True)
    else:
        df = pd.DataFrame([novo_envio])
    
    df.to_excel(CAMINHO_REGISTRO_ENVIO, index=False)

def gerar_id_envio():
    if not os.path.exists(CAMINHO_REGISTRO_ENVIO):
        return 1
    df = pd.read_excel(CAMINHO_REGISTRO_ENVIO)
    return int(df['id'].max()) + 1