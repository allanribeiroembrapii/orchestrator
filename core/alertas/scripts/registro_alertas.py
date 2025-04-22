import pandas as pd
from datetime import datetime
import os

def registrar_envio(caminho, id_alerta, conteudo):
    data_envio = datetime.now().strftime('%Y-%m-%d %H:%M')
    novo_envio = {
        'id': gerar_id_envio(caminho),
        'id_alerta': id_alerta,
        'data': data_envio,
        'conteudo': conteudo
    }
    
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df = df._append(novo_envio, ignore_index=True)
    else:
        df = pd.DataFrame([novo_envio])
    
    df.to_excel(caminho, index=False)

def gerar_id_envio(caminho):
    if not os.path.exists(caminho):
        return 1
    df = pd.read_excel(caminho)
    return int(df['id'].max()) + 1