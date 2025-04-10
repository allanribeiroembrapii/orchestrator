import os
import pandas as pd

def processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data=None, campos_valor=None):
    # Ler o arquivo Excel
    df = pd.read_excel(arquivo_origem)

    # Selecionar apenas as colunas de interesse
    df_selecionado = df[campos_interesse]

    # Renomear as colunas e definir a nova ordem
    df_renomeado = df_selecionado.rename(columns=novos_nomes_e_ordem)

    # Ajustar campos de data, se fornecidos
    if campos_data:
        for campo in campos_data:
            if campo in df_renomeado.columns:
                df_renomeado[campo] = pd.to_datetime(df_renomeado[campo], format='%d/%m/%Y', errors='coerce')

    # Ajustar campos de valor, se fornecidos
    if campos_valor:
        for campo in campos_valor:
            if campo in df_renomeado.columns:
                df_renomeado[campo] = df_renomeado[campo].str.replace('R$ ', '')
                df_renomeado[campo] = df_renomeado[campo].str.replace('.', '').str.replace(',', '.')
                df_renomeado[campo] = df_renomeado[campo].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Reordenar as colunas conforme especificado
    df_final = df_renomeado[list(novos_nomes_e_ordem.values())]

    # Garantir que o diretório de destino existe
    os.makedirs(os.path.dirname(arquivo_destino), exist_ok=True)

    # Verificar se o arquivo de destino está sendo usado e remover se necessário
    if os.path.exists(arquivo_destino):
        os.remove(arquivo_destino)

    # Salvar o arquivo resultante
    with pd.ExcelWriter(arquivo_destino, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Sheet1')

        # Acessar o workbook e worksheet
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Aplicar formatação numérica aos campos de valor
        if campos_valor:
            format_currency = workbook.add_format({'num_format': 'R$ #,##0.00'})
            for coluna in campos_valor:
                if coluna in df_final.columns:
                    col_idx = df_final.columns.get_loc(coluna)
                    worksheet.set_column(col_idx, col_idx, 20, format_currency)

        # Aplicar formatação de data aos campos de data
        if campos_data:
            format_date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            for coluna in campos_data:
                if coluna in df_final.columns:
                    col_idx = df_final.columns.get_loc(coluna)
                    worksheet.set_column(col_idx, col_idx, 20, format_date)

        # Definir a largura das colunas
        for i, coluna in enumerate(df_final.columns):
            col_idx = i
            worksheet.set_column(col_idx, col_idx, 20)

# Exemplo de chamada da função
# processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data, campos_valor)
