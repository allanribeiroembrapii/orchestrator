import os
from dotenv import load_dotenv
import pandas as pd
from scripts.processar_excel import processar_excel

load_dotenv()
ROOT = os.getenv('ROOT_BFA')
STEP1 = os.path.abspath(os.path.join(ROOT, 'data', 'step_1_data_raw'))
STEP2 = os.path.abspath(os.path.join(ROOT, 'data', 'step_2_stage_area'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'data', 'step_3_data_processed'))

def gerar_planilhas():
    # lendo as planilhas
    proj = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Informações Tecnicas Projeto')
    proj_emp = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Empresas')
    proj_ue = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Unidades')
    execucao = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Execução')
    recurso = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Recurso')
    status_me = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Status Macroentregas')
    comentarios = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Comentários')
    stage_gates = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Stage Gate')
    stage_gates_rep = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'BFA - Base de Dados para BI.xlsx')),
                         sheet_name='Representantes Stage Gates')
    
    # juntando projetos com recurso
    proj = proj.merge(recurso, on='Codigo do Projeto', how='left')
    # juntando nome dos representantes
    proj = proj.merge(stage_gates_rep[['Codigo do Projeto', 'Representante GERIN']], on='Codigo do Projeto', how='left')
    # alterando recurso
    proj['Recurso'] = proj['Recurso'].str.replace(
        'CG\n(antes ROTA 2030)',
        'CG; ROTA 2030'
    )
    # tirando "meses" de tempo execução
    proj['Tempo de execução do projeto'] = proj['Tempo de execução do projeto'].str.replace(
        ' meses',
        ''
    )
    # alterando titulo do projeto
    proj['Título'] = proj['Título'].str.replace(
        '\n',
        ' '
    )
    # inserindo coluna com a data de hoje
    proj['data_extracao'] = pd.to_datetime('today').normalize()

    # pegando o código do projeto para incluir nos comentários
    comentarios = comentarios.merge(proj[['Codigo do Projeto', 'Nome Projeto']], on='Nome Projeto', how='left')

    # salvando as planilhas no step1
    proj.to_excel(os.path.join(STEP2, 'bfa_projetos.xlsx'), index=False)
    proj_emp.to_excel(os.path.join(STEP2, 'bfa_projetos_empresas.xlsx'), index=False)
    proj_ue.to_excel(os.path.join(STEP2, 'bfa_projetos_unidades.xlsx'), index=False)
    execucao.to_excel(os.path.join(STEP2, 'bfa_execucao.xlsx'), index=False)
    status_me.to_excel(os.path.join(STEP2, 'bfa_status_macroentregas.xlsx'), index=False)
    comentarios.to_excel(os.path.join(STEP2, 'bfa_comentarios.xlsx'), index=False)
    stage_gates.to_excel(os.path.join(STEP2, 'bfa_stage_gates.xlsx'), index=False)

def processar_planilhas():
    # Processando planilha de projetos
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_proj = "bfa_projetos.xlsx"
    arquivo_origem_proj = os.path.join(STEP2, nome_arquivo_proj)
    arquivo_destino_proj = os.path.join(STEP3, nome_arquivo_proj)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_proj = [
        "Codigo do Projeto",
        "Nome Projeto",
        "Pesquisadores",
        "Data do Repasse",
        "Data de Inicio Vigencia Contrato",
        "Data de Término Vigencia Contrato",
        "Tempo de execução do projeto",
        "Programa",
        "Chamada",
        "Recurso",
        "Título",
        "Status",
        "Objetivo",
        "Data de inicio do contrato",
        "Data de término do contrato",
        "Valor total",
        "Valor EMBRAPII",
        "Valor EMPRESAS",
        "Valor Unidades",
        "Valor EMBRAPII Repassado",
        "Representante GERIN",
        "data_extracao",
    ]

    novos_nomes_proj = {
        "Codigo do Projeto": "codigo_projeto",
        "Programa": "programa",
        "Chamada": "chamada",
        "Recurso": "recurso",
        "Data de Inicio Vigencia Contrato": 'data_inicio_vigencia_contrato',
        "Data de Término Vigencia Contrato": 'data_termino_vigencia_contrato',
        "Data de inicio do contrato": "data_inicio_contrato",
        "Data de término do contrato": "data_termino_contrato",
        "Tempo de execução do projeto": 'tempo_execucao_meses',
        "Status": "status_projeto",
        "Nome Projeto": "nome_projeto",
        "Título": "titulo_projeto",
        "Objetivo": "objetivo",
        "Valor total": 'valor_total',
        "Valor EMBRAPII": 'valor_embrapii',
        "Valor EMPRESAS": 'valor_empresas',
        "Valor Unidades": 'valor_unidades',
        "Valor EMBRAPII Repassado": 'valor_embrapii_repassado',
        "Data do Repasse": 'data_repasse',
        "Pesquisadores": 'pesquisadores',
        "Representante GERIN": 'representante_gerin',
        "data_extracao": 'data_extracao',
    }


    # Campos específicos
    campos_data_proj = ["data_inicio_vigencia_contrato", "data_termino_vigencia_contrato",
                   "data_inicio_contrato", "data_termino_contrato", "data_repasse", "data_extracao"]

    campos_string_proj = ["codigo_projeto", "programa", "chamada", "recurso", "status_projeto",
                          "nome_projeto", "titulo_projeto", "objetivo", "representante_gerin"]

    processar_excel(
        arquivo_origem_proj,
        campos_interesse_proj,
        novos_nomes_proj,
        arquivo_destino_proj,
        campos_data = campos_data_proj,
        campos_string = campos_string_proj
    )

    # Processando planilha de projetos empresas
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_proj_emp = "bfa_projetos_empresas.xlsx"
    arquivo_origem_proj_emp = os.path.join(STEP2, nome_arquivo_proj_emp)
    arquivo_destino_proj_emp = os.path.join(STEP3, nome_arquivo_proj_emp)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_proj_emp = [
        "Código",
        "CNPJ",
    ]

    novos_nomes_proj_emp = {
        "Código": "codigo_projeto",
        "CNPJ": "cnpj",
    }

    campos_string_proj_emp = ["codigo_projeto", "cnpj"]

    processar_excel(
        arquivo_origem_proj_emp,
        campos_interesse_proj_emp,
        novos_nomes_proj_emp,
        arquivo_destino_proj_emp,
        campos_string = campos_string_proj_emp
    )

    # Processando planilha de projetos unidades
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_proj_ue = "bfa_projetos_unidades.xlsx"
    arquivo_origem_proj_ue = os.path.join(STEP2, nome_arquivo_proj_ue)
    arquivo_destino_proj_ue = os.path.join(STEP3, nome_arquivo_proj_ue)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_proj_ue = [
        "Código",
        "Unidade",
        "Papel"
    ]

    novos_nomes_proj_ue = {
        "Código": "codigo_projeto",
        "Unidade": "unidade_embrapii",
        "Papel": "papel_unidade",
    }

    campos_string_proj_ue = ["codigo_projeto", "unidade_embrapii", "papel_unidade"]

    processar_excel(
        arquivo_origem_proj_ue,
        campos_interesse_proj_ue,
        novos_nomes_proj_ue,
        arquivo_destino_proj_ue,
        campos_string = campos_string_proj_ue
    )

    # Processando planilha de execução
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_exec = "bfa_execucao.xlsx"
    arquivo_origem_exec = os.path.join(STEP2, nome_arquivo_exec)
    arquivo_destino_exec = os.path.join(STEP3, nome_arquivo_exec)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_exec = [
        "Codigo do Projeto",
        "Período",
        "Tipo",
        "%",
    ]

    novos_nomes_exec = {
        "Codigo do Projeto": "codigo_projeto",
        "Período": 'periodo',
        "Tipo": 'tipo',
        "%": 'percentual',
    }

    campos_string_exec = ["codigo_projeto", "periodo", "tipo"]

    processar_excel(
        arquivo_origem_exec,
        campos_interesse_exec,
        novos_nomes_exec,
        arquivo_destino_exec,
        campos_string = campos_string_exec
    )

    # Processando planilha de status das macroentregas
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_me = "bfa_status_macroentregas.xlsx"
    arquivo_origem_me = os.path.join(STEP2, nome_arquivo_me)
    arquivo_destino_me = os.path.join(STEP3, nome_arquivo_me)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_me = [
        "Codigo do Projeto",
        "Numero de Macroentregas",
        "# Macroentrega",
        "Entregue?",
        "Data Prevista",
        "Data de Envio",
    ]

    novos_nomes_me = {
        "Codigo do Projeto": 'codigo_projeto',
        "Numero de Macroentregas": 'total_macroentregas',
        "# Macroentrega": 'numero_macroentrega',
        "Data Prevista": 'data_prevista',
        "Data de Envio": 'data_envio',
        "Entregue?": 'entregue',
    }

    campos_data_me = ["data_prevista", "data_envio"]

    campos_string_me = ["codigo_projeto", "entregue"]

    processar_excel(
        arquivo_origem_me,
        campos_interesse_me,
        novos_nomes_me,
        arquivo_destino_me,
        campos_data = campos_data_me,
        campos_string = campos_string_me
    )

    # Processando planilha de comentários
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_com = "bfa_comentarios.xlsx"
    arquivo_origem_com = os.path.join(STEP2, nome_arquivo_com)
    arquivo_destino_com = os.path.join(STEP3, nome_arquivo_com)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_com = [
        "Codigo do Projeto",
        "Comentários",
        "Data do comentário",
    ]

    novos_nomes_com = {
        "Codigo do Projeto": 'codigo_projeto',
        "Comentários": 'comentario',
        "Data do comentário": 'data_comentario',
    }

    campos_data_com = ["data_comentario"]

    campos_string_com = ["codigo_projeto", "comentario"]

    processar_excel(
        arquivo_origem_com,
        campos_interesse_com,
        novos_nomes_com,
        arquivo_destino_com,
        campos_data = campos_data_com,
        campos_string = campos_string_com
    )

# Processando planilha de stage gates
    # Definições dos caminhos e nomes de arquivos
    nome_arquivo_sg = "bfa_stage_gates.xlsx"
    arquivo_origem_sg = os.path.join(STEP2, nome_arquivo_sg)
    arquivo_destino_sg = os.path.join(STEP3, nome_arquivo_sg)

    # Campos de interesse e novos nomes das colunas
    campos_interesse_sg = [
        "Codigo do Projeto",
        "Tipo",
        "Data",
        "Status",
        "Local",
        "Representante DO",
        "Modalidade",
    ]

    novos_nomes_sg = {
        "Codigo do Projeto": 'codigo_projeto',
        "Tipo": 'tipo',
        "Data": 'data',
        "Status": 'status',
        "Local": 'local',
        "Representante DO": 'representante_do',
        "Modalidade": 'modalidade',
    }

    campos_data_sg = ["data"]

    campos_string_sg = ["codigo_projeto", "tipo", "status"]

    processar_excel(
        arquivo_origem_sg,
        campos_interesse_sg,
        novos_nomes_sg,
        arquivo_destino_sg,
        campos_data = campos_data_sg,
        campos_string = campos_string_sg
    )
