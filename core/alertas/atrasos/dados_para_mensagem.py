import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import date
import inspect

# Carregar as variáveis de ambiente
load_dotenv()
ROOT = os.getenv('ROOT')
PLANILHAS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'planilhas'))
ANTERIOR = os.path.abspath(os.path.join(ROOT, 'atrasos', 'anterior'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def verificar_status(df, atual=True):
    """
    Função para verificar os status dos projetos, com base no prazo para atrasados.
        df: data frame - portfolio de projetos.
        atual: bool - se é a planilha atual ou anterior.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        hoje = datetime.now().date()
        semana_passada = hoje - pd.DateOffset(weeks=1)
        semana_passada = semana_passada.date()

        # Converte cada data_termino para apenas a data
        df['data_termino_data'] = df['data_termino'].apply(lambda x: x.date())
        
        if atual:
            # Calcula o prazo em dias
            df['prazo'] = df['data_termino_data'].apply(lambda x: (x - hoje).days)
            
            # Define o novo status
            df['status2'] = df.apply(
                lambda row: 'Atrasado' if row['status'] == 'Em andamento' and row['prazo'] < 0 else row['status'],
                axis=1
            )
        
        else:
            # Calcula o prazo em dias
            df['prazo'] = df['data_termino_data'].apply(lambda x: (x - semana_passada).days)
            
            # Define o novo status
            df['status2'] = df.apply(
                lambda row: 'Atrasado' if row['status'] == 'Em andamento' and row['prazo'] < 0 else row['status'],
                axis=1
            )  

        print("🟢 " + inspect.currentframe().f_code.co_name)
        
        return df
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def comparar_status(df_hoje, df_anterior, nome_status, status_desejado, colunas_interesse, coluna_arrange=None, macro=False):
    """
    Função para comparar status dos projetos e macroentregas entre duas planilhas.
        df_hoje: data frame - planilha atual.
        df_anterior: data frame - planilha anterior.
        nome_status: string - nome da coluna com o status.
        status_desejado: list - status desejado para filtrar.
        colunas_interesse: list - colunas de interesse.
        coluna_arrange: string - coluna para ordenar (se houver).
        macro: bool - se é macroentrega.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        # Filtra os projetos com o status desejado
        df_hoje_filtrado = df_hoje[df_hoje[nome_status].isin(status_desejado)]
        df_anterior_filtrado = df_anterior[df_anterior[nome_status].isin(status_desejado)]

        if macro:
            df_hoje_filtrado['codigo_me'] = df_hoje_filtrado['codigo_projeto'] + df_hoje_filtrado['num_macroentrega'].astype(str)
            df_anterior_filtrado['codigo_me'] = df_anterior_filtrado['codigo_projeto'] + df_anterior_filtrado['num_macroentrega'].astype(str)

            hoje_set = set(df_hoje_filtrado['codigo_me'])
            anterior_set = set(df_anterior_filtrado['codigo_me'])

            # Filtra as linhas com base no conjunto de projetos de hoje que não estavam no anterior
            df_hoje_unicos = df_hoje_filtrado[df_hoje_filtrado['codigo_me'].isin(hoje_set - anterior_set)]

        else:
            # Cria conjuntos com base no 'codigo_projeto'
            hoje_set = set(df_hoje_filtrado['codigo_projeto'])
            anterior_set = set(df_anterior_filtrado['codigo_projeto'])

            # Filtra as linhas com base no conjunto de projetos de hoje que não estavam no anterior
            df_hoje_unicos = df_hoje_filtrado[df_hoje_filtrado['codigo_projeto'].isin(hoje_set - anterior_set)]


        # Seleciona apenas as colunas de interesse
        df_hoje_unicos_interesse = df_hoje_unicos[colunas_interesse]

        # Ordena as colunas de interesse
        if coluna_arrange:
            df_hoje_unicos_interesse = df_hoje_unicos_interesse.sort_values(by=coluna_arrange, ascending=True)

        print("🟢 " + inspect.currentframe().f_code.co_name)

        return df_hoje_unicos_interesse, len(hoje_set), len(hoje_set - anterior_set)
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def nova_data_macroentrega(df_macro, data_termino, data_aceitacao):
    """
    Função para verificar a data de término real ou aceitação da macroentrega.
        df_macro: data frame - macroentregas.
        data_termino: string - nome da coluna com a data de término.
        data_aceitacao: string - nome da coluna com a data de aceitação.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        # Obtendo a data de hoje
        today = pd.Timestamp.today()

        df_macro['_data_termino_real_ou_aceitacao'] = np.where(
            df_macro[data_termino].isna(),
            np.where(
                (df_macro[data_aceitacao] <= today),
                df_macro[data_aceitacao],
                pd.NaT
            ),
            np.where(
                (df_macro[data_termino] <= today),
                df_macro[data_termino],
                pd.NaT
            )
        )
        print("🟢 " + inspect.currentframe().f_code.co_name)
        return df_macro
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def verificar_status_macroentrega(df_macro, df_portfolio, atual=True):
    """
    Função para verificar os status das macroentregas, levando em conta o status dos projetos.
        df_macro: data frame - macroentregas.
        df_portfolio: data frame - portfolio de projetos.
        atual: bool - se é a planilha atual ou anterior.

    retorna o dataframe com o status das macroentregas.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        today = datetime.now().date()
        last_week = today - pd.DateOffset(weeks=1)
        last_week = last_week.date()

        df_macro = df_macro.merge(df_portfolio, on='codigo_projeto', how='left')

        # Converte 'data_termino_planejado' para formato de data (caso tenha horas)
        df_macro['data_termino_planejado'] = pd.to_datetime(df_macro['data_termino_planejado']).dt.date

        if atual:
            # Definição das condições
            conditions = [
                df_macro['_data_termino_real_ou_aceitacao'].isna() & df_macro['data_termino_planejado'].isna(),
                df_macro['_data_termino_real_ou_aceitacao'].isna() & (df_macro['data_termino_planejado'] >= today),
                df_macro['_data_termino_real_ou_aceitacao'].isna() & (df_macro['data_termino_planejado'] < today) &
                df_macro['status2'].isin(['Em andamento', 'Atrasado']) & (df_macro['termo_aceite'] == 'Download'),
                df_macro['_data_termino_real_ou_aceitacao'].isna() & (df_macro['data_termino_planejado'] < today) &
                df_macro['status2'].isin(['Em andamento', 'Atrasado']) & (df_macro['termo_aceite'] == 'Nenhum anexo'),
                df_macro['_data_termino_real_ou_aceitacao'].notna() & (df_macro['termo_aceite'] == 'Nenhum anexo'),
                df_macro['_data_termino_real_ou_aceitacao'].notna(),
                df_macro['status2'].isin(['Cancelado', 'Suspenso']),
                df_macro['termo_aceite'] == 'Nenhum anexo'
            ]

        else:
            # Definição das condições
            conditions = [
                df_macro['_data_termino_real_ou_aceitacao'].isna() & df_macro['data_termino_planejado'].isna(),
                df_macro['_data_termino_real_ou_aceitacao'].isna() & (df_macro['data_termino_planejado'] >= last_week),
                df_macro['_data_termino_real_ou_aceitacao'].isna() & (df_macro['data_termino_planejado'] < last_week) &
                df_macro['status2'].isin(['Em andamento', 'Atrasado']) & (df_macro['termo_aceite'] == 'Download'),
                df_macro['_data_termino_real_ou_aceitacao'].isna() & (df_macro['data_termino_planejado'] < last_week) &
                df_macro['status2'].isin(['Em andamento', 'Atrasado']) & (df_macro['termo_aceite'] == 'Nenhum anexo'),
                df_macro['_data_termino_real_ou_aceitacao'].notna() & (df_macro['termo_aceite'] == 'Nenhum anexo'),
                df_macro['_data_termino_real_ou_aceitacao'].notna(),
                df_macro['status2'].isin(['Cancelado', 'Suspenso']),
                df_macro['termo_aceite'] == 'Nenhum anexo'
            ]

        # Definição dos valores correspondentes
        values = [
            "Não entregue - Sem data planejada",
            "Não entregue - Dentro do prazo",
            "Termo de aceite entregue - sem data de término/aceite da ME",
            "Não entregue - Em atraso",
            "Entregue - Sem termo de aceite",
            "Entregue",
            "Projeto " + df_macro['status2'],
            "Projeto " + df_macro['status2'] + ", ME sem termo e sem data de término/aceite"
        ]
        
        # Aplicando a lógica
        df_macro['status_macroentrega'] = np.select(conditions,
                                                    values,
                                                    default="Projeto " + df_macro['status2'] + ", sem data de término/aceite da ME")

        print("🟢 " + inspect.currentframe().f_code.co_name)
        return df_macro
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def definir_modalidade(modalidade_financiamento):
    """
    Função para padronizar as categorias de modalidade de financiamento.
        modalidade_financiamento: string - coluna onde está a modalidade de financiamento no dataframe.

    retorna a modalidade de financiamento padronizada.
    """
    try:
        modalidade_financiamento = modalidade_financiamento.upper()

        if "SEBRAE" in modalidade_financiamento:
            if "BNDES" in modalidade_financiamento:
                resultado = "BNDES/Sebrae"
            elif "ROTA" in modalidade_financiamento:
                resultado = "MOVER/Sebrae"
            else:
                resultado = "CG/Sebrae"

        elif "BNDES" in modalidade_financiamento:
            resultado = "BNDES"

        elif "ROTA" in modalidade_financiamento:
            resultado = "MOVER"

        else:
            resultado = "CG"

        return resultado

    except Exception as e:
        print(f"🔴 Erro: {e}")
        

def dados_projetos():
    """
    Função para obter os dados necessários dos projetos para o envio da mensagem ao Teams.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        # Carregar as planilhas
        projetos_atual = pd.read_excel(os.path.join(PLANILHAS, "portfolio.xlsx"))  # Planilha de projetos (atual)
        projetos_anterior = pd.read_excel(os.path.join(ANTERIOR, "portfolio.xlsx"))  # Planilha de projetos (anterior)

        # Novo status projetos
        projetos_atual['modalidade'] = projetos_atual['modalidade_financiamento'].apply(definir_modalidade)
        projetos_atual = verificar_status(projetos_atual)
        projetos_anterior = verificar_status(projetos_anterior, atual=False)

        # Comparar status dos projetos
        novos, proj_concluidos, novos_concluidos = comparar_status(projetos_atual, projetos_anterior,
                                                                'status2', ['Concluído', 'Encerrado'],
                                                                ['unidade_embrapii', 'codigo_projeto', 'modalidade', 'data_inicio', 'data_termino'],
                                                                coluna_arrange='unidade_embrapii')
        novos2, proj_atrasados, novos_atrasados = comparar_status(projetos_atual, projetos_anterior,
                                                                'status2', ['Atrasado'],
                                                                ['unidade_embrapii', 'codigo_projeto', 'data_termino', 'prazo'],
                                                                coluna_arrange='unidade_embrapii')
        
        novos["data_inicio"] = pd.to_datetime(novos["data_inicio"])
        novos["data_termino"] = pd.to_datetime(novos["data_termino"])

        novos["duracao_dias"] = (novos["data_termino"] - novos["data_inicio"]).dt.days

        
        #### TOTAIS ####
        total_projetos = len(projetos_atual['codigo_projeto'])
        total_projetos_anterior = len(projetos_anterior['codigo_projeto'])
        novos_projetos = total_projetos - total_projetos_anterior

        print("🟢 " + inspect.currentframe().f_code.co_name)
        return novos, proj_concluidos, novos_concluidos, novos2, proj_atrasados, novos_atrasados, total_projetos, total_projetos_anterior, novos_projetos
    
    except Exception as e:
        print(f"🔴 Erro: {e}")


def dados_macroentregas():
    """
    Função para obter os dados necessários das macroentregas para o envio da mensagem ao Teams.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:

        # Carregar as planilhas
        projetos_atual = pd.read_excel(os.path.join(PLANILHAS, "portfolio.xlsx"))  # Planilha de projetos (atual)
        projetos_anterior = pd.read_excel(os.path.join(ANTERIOR, "portfolio.xlsx"))  # Planilha de projetos (anterior)
        macroentregas_atual = pd.read_excel(os.path.join(PLANILHAS, "macroentregas.xlsx"))  # Planilha de macroentregas (atual)
        macroentregas_anterior = pd.read_excel(os.path.join(ANTERIOR, "macroentregas.xlsx"))  # Planilha de macroentregas (anterior)

        # Totais
        total_macroentregas = len(macroentregas_atual['codigo_projeto'])
        total_macroentregas_anterior = len(macroentregas_anterior['codigo_projeto'])
        novas_macroentregas = total_macroentregas - total_macroentregas_anterior

        # Novo status projetos
        projetos_atual['modalidade'] = projetos_atual['modalidade_financiamento'].apply(definir_modalidade)
        projetos_atual = verificar_status(projetos_atual)
        projetos_anterior = verificar_status(projetos_anterior, atual=False)
        
        # data termino real ou aceite da macroentrega
        # Convertendo colunas para datetime
        macroentregas_anterior['data_termino_real'] = pd.to_datetime(macroentregas_anterior['data_termino_real'])
        macroentregas_atual['data_termino_real'] = pd.to_datetime(macroentregas_atual['data_termino_real'])
        macroentregas_anterior['data_aceitacao'] = pd.to_datetime(macroentregas_anterior['data_aceitacao'])
        macroentregas_atual['data_aceitacao'] = pd.to_datetime(macroentregas_atual['data_aceitacao'])

        # Aplicando a lógica
        macroentregas_anterior = nova_data_macroentrega(macroentregas_anterior, 'data_termino_real', 'data_aceitacao')
        macroentregas_atual = nova_data_macroentrega(macroentregas_atual, 'data_termino_real', 'data_aceitacao')

        # status da macroentrega
        macroentregas_anterior = verificar_status_macroentrega(macroentregas_anterior, projetos_atual, atual=False)
        macroentregas_atual = verificar_status_macroentrega(macroentregas_atual, projetos_atual)

        # prazo da macroentrega
        # Converter para datetime se necessário
        macroentregas_anterior['data_termino_planejado'] = pd.to_datetime(macroentregas_anterior['data_termino_planejado'], errors='coerce')

        # Calcular diferença de dias corretamente
        macroentregas_anterior['prazo'] = np.where(
            ~macroentregas_anterior['status_macroentrega'].isin(['Entregue', 'Projeto Cancelado']),
            (macroentregas_anterior['data_termino_planejado'] - pd.Timestamp(date.today())).dt.days,
            0
        )

        # Converter para datetime se necessário
        macroentregas_atual['data_termino_planejado'] = pd.to_datetime(macroentregas_atual['data_termino_planejado'], errors='coerce')

        macroentregas_atual['prazo'] = np.where(
            ~macroentregas_atual['status_macroentrega'].isin(['Entregue', 'Projeto Cancelado']),
            (macroentregas_atual['data_termino_planejado'] - pd.Timestamp.today()).dt.days,
            0
        )

        ### Comparar macroentregas ###
        novas_macro, macro_atrasadas, novas_macro_atrasadas = comparar_status(macroentregas_atual, macroentregas_anterior,
                                                                'status_macroentrega', ['Não entregue - Em atraso'],
                                                                ['unidade_embrapii', 'codigo_projeto', 'num_macroentrega', 'data_termino_planejado', 'prazo'],
                                                                coluna_arrange='unidade_embrapii', macro=True)
        macro_sem_termo_60 = macroentregas_atual[(macroentregas_atual['status_macroentrega'] == 'Entregue - Sem termo de aceite') & (macroentregas_atual['prazo'] <= -60)][['unidade_embrapii', 'codigo_projeto', 'num_macroentrega', 'prazo']]
        macro_sem_termo_60 = macro_sem_termo_60.sort_values(by='unidade_embrapii', ascending=True)

        macro_sem_termo_60_novas = macroentregas_atual[(macroentregas_atual['status_macroentrega'] == 'Entregue - Sem termo de aceite') & (macroentregas_atual['prazo'] <= -60) & (macroentregas_atual['prazo'] > -68)][['unidade_embrapii', 'codigo_projeto', 'num_macroentrega', 'prazo']]

        print("🟢 " + inspect.currentframe().f_code.co_name)

        return novas_macro, macro_atrasadas, novas_macro_atrasadas, macro_sem_termo_60, macro_sem_termo_60_novas, total_macroentregas, total_macroentregas_anterior, novas_macroentregas
    
    except Exception as e:
        print(f"🔴 Erro: {e}")