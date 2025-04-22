import os
import pandas as pd
import re
import pyshorteners
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def encurtar_url(url, max_length=2000):
    """
    Encurta URLs que excedem o comprimento máximo especificado.
    
    Args:
        url: A URL a ser verificada e possivelmente encurtada
        max_length: O comprimento máximo permitido antes de encurtar
        
    Returns:
        URL encurtada se exceder o comprimento máximo, caso contrário a URL original
    """
    # Verificar se o valor é uma string
    if not isinstance(url, str):
        return url
    
    # Verificar se parece ser uma URL (começa com http:// ou https://)
    if not re.match(r'^https?://', url):
        return url
    
    # Se a URL for menor que o comprimento máximo, retornar como está
    if len(url) <= max_length:
        return url
    
    try:
        # Tentar encurtar a URL
        s = pyshorteners.Shortener()
        return s.tinyurl.short(url)
    except Exception as e:
        print(f"Erro ao encurtar URL: {e}")
        # Em caso de erro, truncar a URL para evitar exceder o limite do Excel
        return url[:max_length]

def processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino, campos_data=None, campos_valor=None, campos_url=None):
    # Ler o arquivo Excel
    df = pd.read_excel(arquivo_origem)

    # Selecionar apenas as colunas de interesse
    df_selecionado = df[campos_interesse]

    # Renomear as colunas e definir a nova ordem
    df_renomeado = df_selecionado.rename(columns=novos_nomes_e_ordem)
    
    # Identificar automaticamente campos que podem conter URLs se campos_url não for fornecido
    if campos_url is None:
        campos_url = []
        for coluna in df_renomeado.columns:
            # Verificar nomes de coluna que provavelmente contêm URLs
            if any(termo in coluna.lower() for termo in ['link', 'url', 'site', 'web', 'http']):
                campos_url.append(coluna)
    
    # Encurtar URLs em campos identificados
    for campo in campos_url:
        if campo in df_renomeado.columns:
            df_renomeado[campo] = df_renomeado[campo].apply(lambda x: encurtar_url(x) if pd.notna(x) else x)

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
    
    # Verificar se há URLs longas em qualquer coluna (como medida de segurança adicional)
    for coluna in df_final.columns:
        if df_final[coluna].dtype == 'object':  # Apenas colunas de texto
            # Verificar se algum valor parece ser uma URL longa
            mask = df_final[coluna].astype(str).str.len() > 2000
            if mask.any():
                # Se encontrar URLs longas, aplicar o encurtador
                df_final.loc[mask, coluna] = df_final.loc[mask, coluna].apply(
                    lambda x: encurtar_url(x) if isinstance(x, str) else x
                )

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
