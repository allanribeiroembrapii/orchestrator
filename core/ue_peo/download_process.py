import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
from office365_api.office365_api import SharePoint  # Ajuste o import conforme sua estrutura

def process_data(file_content):
    # Envolve o objeto bytes em um BytesIO para compatibilidade futura
    df = pd.read_excel(BytesIO(file_content))
    return pd.DataFrame({
        'id': range(1, len(df)+1),
        'unidade_embrapii': df['Unidade EMBRAPII'],
        'peo_classificacao': df['Classificação Unidade'],
        'peo_aderiu': df['Aderiu?'].map({True: 'Sim', False: 'Não'}),
        'data_extracao': datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')
    })

def main():
    sharepoint = SharePoint()
    
    # Parâmetros específicos do seu arquivo
    folder_name = "General/Lucas Pinheiro/classificacao_unidade"  # Caminho completo
    file_name = "classificacao_unidade.xlsx"
    
    try:
        # Baixar arquivo
        file_content = sharepoint.download_file(folder_name, file_name)
        print(type(file_content))
        
        # Processar e salvar
        df_final = process_data(file_content)
        output_path = "ue_peo/output/step_1_data_raw/dados_consolidados.xlsx"
        df_final.to_excel(output_path, index=False)
        print(f"Arquivo salvo em: {output_path}")
        
    except Exception as e:
        print(f"Erro fatal: {str(e)}")

if __name__ == "__main__":
    main()
