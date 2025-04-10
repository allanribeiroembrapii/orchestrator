import os
import pandas as pd
import win32com.client as win32

# Caminho da pasta com os arquivos
PASTA_FILES_RAW = r'unidade_embrapii/plano_metas/files_raw_metas'

def salvar_como_xlsx(caminho_arquivo):
    # Verifica se o arquivo existe antes de abrir
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False  # Deixa o Excel oculto
    excel.DisplayAlerts = False  # Desativa os alertas para evitar confirmações
    wb = excel.Workbooks.Open(os.path.abspath(caminho_arquivo))

    # Salva o arquivo como .xlsx no mesmo lugar
    novo_caminho = caminho_arquivo if caminho_arquivo.endswith('.xlsx') else caminho_arquivo.replace('.xls', '.xlsx')
    wb.SaveAs(os.path.abspath(novo_caminho), FileFormat=51)  # 51 é o código para XLSX
    wb.Close(False)
    excel.Application.Quit()

    return novo_caminho

def join_metas():
    # Lista para armazenar os dataframes
    lista_dfs = []

    # Percorre cada arquivo na pasta
    for arquivo in os.listdir(PASTA_FILES_RAW):
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join(PASTA_FILES_RAW, arquivo)

        # Verifica se é um arquivo Excel
        if caminho_arquivo.endswith('.xlsx') or caminho_arquivo.endswith('.xls'):
            try:
                # Salva como .xlsx se necessário
                caminho_arquivo = salvar_como_xlsx(caminho_arquivo)
            except FileNotFoundError as e:
                print(e)
                continue
            
            # Extrai o ID a partir do nome do arquivo (ex.: 'id_1.xlsx' -> 1)
            partes = os.path.splitext(arquivo)[0].split('_')
            if len(partes) == 2 and partes[0] == 'id' and partes[1].isdigit():
                id_num = int(partes[1])
            else:
                print(f"Formato inesperado para o nome do arquivo: '{arquivo}'")
                continue
            
            # Carrega o workbook como .xlsx
            xls = pd.ExcelFile(caminho_arquivo, engine='openpyxl')
            
            for nome_planilha in xls.sheet_names:
                try:
                    df = pd.read_excel(xls, sheet_name=nome_planilha)
                    
                    # Adiciona a coluna 'id' com o número do arquivo
                    df['id'] = id_num

                    # Ajusta o DataFrame para o formato desejado
                    # Assume que a primeira coluna é o título da meta e as outras colunas são anos
                    df_melt = pd.melt(df, id_vars=['id', df.columns[0]], var_name='ano', value_name='valor')
                    df_melt.rename(columns={df.columns[0]: 'Título da meta'}, inplace=True)
                    
                    # Adiciona o dataframe transformado na lista
                    lista_dfs.append(df_melt)

                except Exception as e:
                    print(f"Erro ao processar a planilha '{nome_planilha}' no arquivo '{arquivo}': {e}")
                    continue

    # Concatena todos os dataframes da lista, se houver dataframes para concatenar
    if lista_dfs:
        df_final = pd.concat(lista_dfs, ignore_index=True)
        # Exporta o dataframe final para um arquivo Excel
        caminho_saida = r'unidade_embrapii/plano_metas/metas_consolidadas/metas_consolidadas.xlsx'
        df_final.to_excel(caminho_saida, index=False)
    else:
        print("Nenhuma planilha válida foi processada.")

