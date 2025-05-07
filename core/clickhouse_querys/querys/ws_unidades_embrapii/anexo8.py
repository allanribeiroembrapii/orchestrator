from dotenv import load_dotenv
import os
import sys
from connection.query_clickhouse import query_clickhouse
from datetime import datetime
import pandas as pd

load_dotenv()

ROOT = os.getenv('ROOT')
sys.path.append(ROOT)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
STEP_1_DATA_RAW = os.getenv('STEP_1_DATA_RAW')
STEP_2_STAGE_AREA = os.getenv('STEP_2_STAGE_AREA')
STEP_3_DATA_PROCESSED = os.getenv('STEP_3_DATA_PROCESSED')


def anexo8(por_unidade, por_projeto, por_mes, mes_especifico, ano_especifico, tirar_desqualificados):
    query = """
    SELECT  U.name
            ,P.code
            ,P.status
            ,CASE   WHEN    YEAR(cast(PFR.period_start as datetime)) = YEAR(cast(PFR.period_end as datetime))
                    THEN     (CASE  WHEN cast(MONTH(cast(PFR.period_start as datetime)) as Int8) = 1 AND cast(MONTH(cast(PFR.period_end as datetime)) as Int8) = 6
                                    THEN concat('1/',   cast(YEAR(cast(PFR.period_start as datetime)) as String))
                                    WHEN cast(MONTH(cast(PFR.period_start as datetime)) as Int8) = 7 AND cast(MONTH(cast(PFR.period_end as datetime)) as Int8) = 12
                                    THEN concat('2/',   cast(YEAR(cast(PFR.period_start as datetime)) as String))
                                    WHEN cast(MONTH(cast(PFR.period_start as datetime)) as Int8) = 1 AND cast(MONTH(cast(PFR.period_end as datetime)) as Int8) = 12
                                    THEN cast(YEAR(cast(PFR.period_start as datetime)) as String)
                                    ELSE concat(arrayElement(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], MONTH(cast(PFR.period_start as datetime))),'/', cast(YEAR(cast(PFR.period_start as datetime)) as String),' - ', arrayElement(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], MONTH(cast(PFR.period_end as datetime))),'/', cast(YEAR(cast(PFR.period_end as datetime)) as String))
                                    END
                            )
                    WHEN    YEAR(cast(PFR.period_end as datetime)) > YEAR(cast(PFR.period_start as datetime))
                    THEN    concat((CASE    WHEN cast(MONTH(cast(PFR.period_start as datetime)) as Int8) = 1
                                            THEN '1/'
                                            WHEN cast(MONTH(cast(PFR.period_start as datetime)) as Int8) = 7
                                            THEN '2/'
                                            ELSE ''
                                            END
                                    )
                                    ,cast(YEAR(cast(PFR.period_start as datetime)) as String)
                                    ,' - '
                                    ,(CASE  WHEN cast(MONTH(cast(PFR.period_end as datetime)) as Int8) = 6
                                            THEN '1/'
                                            WHEN cast(MONTH(cast(PFR.period_end as datetime)) as Int8) = 12
                                            THEN '2/'
                                            ELSE ''
                                            END
                                    )
                                    ,cast(YEAR(cast(PFR.period_end as datetime)) as String)
                                    )
                    ELSE 'Erro'
            END                                                 Periodo
            ,CASE WHEN RE.status = '1' THEN 'Aberto' WHEN RE.status = '2' THEN 'Em Análise' WHEN RE.status = '3' THEN 'Fechado' END SitParecer
            ,TM.month_year
            ,TM.total_hours
            ,TM.value
            ,R.availability
            ,R.start_date
            ,R.end_date
            ,PE.cpf
            ,PE.name
    FROM    db_bronze_srinfo.ue_unit                     U
    JOIN    db_bronze_srinfo.project_project_ue                PU ON U.id          = PU.unit_id
    JOIN    db_bronze_srinfo.project_project               P  ON P.id          = PU.project_id
    JOIN    db_bronze_srinfo.projectfinance_financialreport       PFR    ON P.id          = PFR.project_related_id
    JOIN    db_bronze_srinfo.projectfinance_report              RE  ON  PFR.report_id   = RE.id
    JOIN    db_bronze_srinfo.projectfinance_timesheet        TM  ON  PFR.id          = TM.financial_report_id
    JOIN    db_bronze_srinfo.projectfinance_memberallocation   M  ON M.id          = TM.memberallocation_related_id
    JOIN    db_bronze_srinfo.people_role                  R  ON M.role_id      = R.id
    JOIN    db_bronze_srinfo.people_person                PE ON R.person_id        = PE.id
    WHERE   U.data_inativacao IS NULL
    AND     PU.data_inativacao IS NULL
    AND     P.data_inativacao IS NULL
    AND     PFR.data_inativacao IS NULL
    AND     RE.data_inativacao IS NULL
    AND     TM.data_inativacao IS NULL
    AND     M.data_inativacao IS NULL
    AND     R.data_inativacao IS NULL
    AND     PE.data_inativacao IS NULL
    """
    nome_arquivo = "anexo8"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)
    gerar_planilhas_equipes(por_unidade, por_projeto, por_mes, mes_especifico, ano_especifico, tirar_desqualificados)



def gerar_planilhas_equipes(por_unidade = False, por_projeto = False, por_mes = False, mes_especifico = None,
                            ano_especifico = None, tirar_desqualificados = False):
        
        today = datetime.now()
        nome_arquivo = "anexo8"
        pasta = 'data/step_1_data_raw'

        # Carregar o CSV
        destino = os.path.join(ROOT, 'data/step_3_data_processed')

        arquivo_origem = os.path.join(ROOT, pasta, f"{nome_arquivo}.csv")   

        df = pd.read_csv(arquivo_origem, delimiter=',')

        # Converter a coluna de data para datetime
        df["month_year"] = pd.to_datetime(df["month_year"])

        # Criar uma coluna de ano/mês (formato AAAA-MM)
        df["mes_ano"] = df["month_year"].dt.to_period("M")

        # Criar colunas mês e ano
        df["ano"] = df["mes_ano"].dt.year
        df["mes"] = df["mes_ano"].dt.month

        if ano_especifico is not None and mes_especifico is not None:
                if tirar_desqualificados:
                        df2 = df[(df["mes"].isin(mes_especifico)) & (df["ano"].isin(ano_especifico)) & (df["P.status"] != "Desqualificado")]
                else:
                        df2 = df[(df["mes"].isin(mes_especifico)) & (df["ano"].isin(ano_especifico))]
        elif mes_especifico is not None:
                df2 = df[df["mes"].isin(mes_especifico)]
        elif ano_especifico is not None:
                df2 = df[df["ano"].isin(ano_especifico)]
        else:
                df2 = df


        # Contar CPFs distintos por unidade e mês
        if por_unidade:
                unidade_mes = df2.groupby(["U.name", "mes", "ano", "mes_ano"]).agg(
                        cpf = ("cpf", "count"),
                        cpf_distintos = ("cpf", "nunique"),
                        valor_total = ("value", "sum"),
                        horas_totais = ("total_hours", "sum")
                ).reset_index()

                unidade_mes["valor_por_pessoa"] = unidade_mes["valor_total"] / unidade_mes["cpf_distintos"]
                unidade_mes["horas_por_pessoa"] = unidade_mes["horas_totais"] / unidade_mes["cpf_distintos"]
                unidade_mes["data_extracao"] = today

                # Renomear as colunas
                unidade_mes.rename(
                columns={
                        "U.name": "unidade_embrapii"
                },
                
                inplace=True)

                # Salvar em excel
                os.makedirs(destino, exist_ok=True)
                unidade_mes.to_excel(os.path.join(destino, 'anexo8_cpfs_unidade_mes.xlsx'), index = False)    


        # Contar CPFs distintos por projeto e mês
        if por_projeto == True:
                projeto_mes = df2.groupby(["code", "mes", "ano", "mes_ano"]).agg(
                        cpf = ("cpf", "count"),
                        cpf_distintos = ("cpf", "nunique"),
                        valor_total = ("value", "sum"),
                        horas_totais = ("total_hours", "sum")
                ).reset_index()

                projeto_mes["valor_por_pessoa"] = projeto_mes["valor_total"] / projeto_mes["cpf_distintos"]
                projeto_mes["horas_por_pessoa"] = projeto_mes["horas_totais"] / projeto_mes["cpf_distintos"]
                projeto_mes["data_extracao"] = today

                # Renomear as colunas
                projeto_mes.rename(
                columns={
                        "code": "codigo_projeto"
                },
                
                inplace=True)

                # Salvar em Excel
                os.makedirs(destino, exist_ok=True)
                projeto_mes.to_excel(os.path.join(destino, 'anexo8_cpfs_projeto_mes.xlsx'), index = False)


        # Contar CPFs distintos por mes
        if por_mes == True:
                mes = df2.groupby(["mes", "ano", "mes_ano"]).agg(
                        cpf = ("cpf", "count"),
                        cpf_distintos = ("cpf", "nunique"),
                        valor_total = ("value", "sum"),
                        horas_totais = ("total_hours", "sum")
                ).reset_index()

                mes["valor_por_pessoa"] = mes["valor_total"] / mes["cpf_distintos"]
                mes["horas_por_pessoa"] = mes["horas_totais"] / mes["cpf_distintos"]
                mes["data_extracao"] = today

                # Salvar em Excel
                os.makedirs(destino, exist_ok=True)
                mes.to_excel(os.path.join(destino, 'anexo8_cpfs_mes.xlsx'), index = False)

        df3 = df2.rename(columns={"U.name": "unidade_embrapii",
                                  "code" : "codigo_projeto",
                                  "P.status" : "status_projeto",
                                  "Periodo" : "periodo",
                                  "SitParecer" : "situacao_parecer",
                                  "total_hours" : "horas_trabalho",
                                  "value" : "valor",
                                  "availability" : "disponibilidade",
                                  "start_date" : "data_inicio",
                                  "end_date" : "data_termino"})
        
        df3 = df3[['cpf', 'unidade_embrapii', 'codigo_projeto', 'mes_ano', 'mes', 'ano', 'status_projeto',
                   'periodo', 'situacao_parecer', 'horas_trabalho', 'valor', 'disponibilidade', 'data_inicio',
                   'data_termino']]
        
        # Salvar em csv
        os.makedirs(destino, exist_ok=True)
        df3.to_csv(os.path.join(destino, 'anexo8_completo.csv'), index = False)