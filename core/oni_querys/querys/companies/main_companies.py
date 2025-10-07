import os
import pandas as pd
import numpy as np
from datetime import datetime
import inspect
from dotenv import load_dotenv
from connection.query_clickhouse import query_clickhouse_com_retorno
from connection.connect_databricks import connect_databricks
from connection.connect_vpn import connect_vpn, disconnect_vpn
import clickhouse_connect

# Obter o diretório atual e o diretório raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente do .env
load_dotenv()
ROOT = os.getenv("ROOT")
if not ROOT:
    ROOT = parent_dir
STEP3 = os.getenv("STEP_3_DATA_PROCESSED")
#ACESSO CLICKHOUSE
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')


# Funções auxiliares para manipulação de IDs e tipos
def obter_proximo_id():
    """Obter o maior ID da tabela ClickHouse para gerar novos IDs sequenciais."""
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        # Conectar ao ClickHouse
        client = clickhouse_connect.get_client(host=HOST, port=PORT, user=USER, password=PASSWORD)
        
        # Buscar o maior ID atual
        result = client.query("SELECT MAX(id) as max_id FROM data_pii.tb_oni_companies")
        
        if result.result_rows and result.result_rows[0][0] is not None:
            max_id = result.result_rows[0][0]
            print(f"📊 Maior ID encontrado: {max_id}")
        else:
            max_id = 0
            print("📊 Tabela vazia, iniciando com ID 0")
        
        print("🟢 " + inspect.currentframe().f_code.co_name)
        return max_id + 1  # Próximo ID disponível
        
    except Exception as e:
        print(f"🔴 Erro ao obter próximo ID: {e}")
        return 1  # Fallback para ID 1

def adicionar_ids_sequenciais(df, id_inicial):
    """Adiciona IDs sequenciais ao DataFrame."""
    print("🟡 Adicionando IDs sequenciais...")
    
    df = df.copy()
    df['id'] = range(id_inicial, id_inicial + len(df))
    
    # Reordenar colunas para colocar 'id' no início
    colunas = ['id'] + [col for col in df.columns if col != 'id']
    df = df[colunas]
    
    print(f"📊 IDs adicionados: {id_inicial} a {id_inicial + len(df) - 1}")
    return df

def forcar_int_ou_none(valor, obrigatorio=False):
    """Força conversão para int ou None - ULTRA AGRESSIVA"""
    
    if valor is None:
        return 0 if obrigatorio else None
    
    if isinstance(valor, (np.float64, np.float32, float)):
        if np.isnan(valor):
            return 0 if obrigatorio else None
        else:
            return int(valor)
    
    if pd.isna(valor):
        return 0 if obrigatorio else None
    
    try:
        if isinstance(valor, str):
            if valor.strip() == '' or valor.lower() in ['nan', 'none', 'null']:
                return 0 if obrigatorio else None
        
        num = float(valor)
        if np.isnan(num) or np.isinf(num):
            return 0 if obrigatorio else None
        
        return int(num)
    except:
        return 0 if obrigatorio else None

def forcar_string_ou_none(valor, obrigatorio=False):
    """Força conversão para string ou None"""
    
    if valor is None:
        return "" if obrigatorio else None
    
    if isinstance(valor, (np.float64, np.float32, float)) and np.isnan(valor):
        return "" if obrigatorio else None
    
    if pd.isna(valor):
        return "" if obrigatorio else None
    
    try:
        if isinstance(valor, (int, np.int64, np.int32)):
            return str(valor)
        
        if isinstance(valor, (float, np.float64, np.float32)):
            if np.isnan(valor):
                return "" if obrigatorio else None
            if valor == int(valor):
                return str(int(valor))
            return str(valor)
        
        str_valor = str(valor).strip()
        
        if str_valor == '' or str_valor.lower() in ['nan', 'none', 'null', 'na']:
            return "" if obrigatorio else None
        
        return str_valor
    except:
        return "" if obrigatorio else None

def forcar_data_ou_none(valor, obrigatorio=False):
    """Força conversão para data ou None"""
    
    if valor is None:
        return pd.Timestamp.now().date() if obrigatorio else None
    
    if isinstance(valor, (np.float64, np.float32, float)) and np.isnan(valor):
        return pd.Timestamp.now().date() if obrigatorio else None
    
    if pd.isna(valor):
        return pd.Timestamp.now().date() if obrigatorio else None
    
    try:
        if isinstance(valor, pd.Timestamp):
            return valor.date()
        
        dt = pd.to_datetime(valor, errors='coerce')
        if pd.isna(dt):
            return pd.Timestamp.now().date() if obrigatorio else None
        
        return dt.date()
    except:
        return pd.Timestamp.now().date() if obrigatorio else None

def converter_dataframe_para_clickhouse(df):
    """
    Conversão ultra agressiva - força todos os valores para tipos Python nativos
    com correção para campos nullable/não-nullable
    """
    df = df.copy()
    
    # Colunas que DEVEM ser inteiros ou None
    colunas_numericas = ['id', 'cd_cnpj_ordem', 'cd_cnpj_dv', 'cd_mun', 
                        'cd_sit_cadastral', 'cd_motivo_sit_cadastral', 'cd_pais']
    
    # Colunas que DEVEM ser strings ou None  
    colunas_string = ['cnpj', 'ds_matriz_filial', 'razao_social', 'nome_fantasia', 
                     'porte', 'ds_sit_cadastral', 'nm_cidade_exterior', 
                     'cd_cnae20sub_secundaria', 'nm_tipo_logradouro', 'nm_logradouro',
                     'nm_numero_estbl', 'nm_complemento', 'nm_bairro', 'cd_cep', 
                     'sg_uf', 'nm_ddd_1', 'nm_telefone_1', 'nm_ddd_2', 'nm_telefone_2',
                     'nm_ddd_fax', 'nm_fax', 'nm_email', 'cd_cnae20sub_principal']
    
    # Colunas de data
    colunas_data = ['dt_sit_cadastral', 'dt_inicio_ativ', 'dt_carga']
    
    # Apenas 3 campos obrigatórios
    campos_obrigatorios = ['id', 'cnpj', 'dt_carga']
    
    # Processar colunas numéricas
    for col in colunas_numericas:
        if col in df.columns:
            nova_coluna = []
            for valor in df[col]:
                novo_valor = forcar_int_ou_none(valor, obrigatorio=(col in campos_obrigatorios))
                nova_coluna.append(novo_valor)
            df[col] = pd.Series(nova_coluna, dtype=object)
    
    # Processar colunas string
    for col in colunas_string:
        if col in df.columns:
            nova_coluna = []
            for valor in df[col]:
                novo_valor = forcar_string_ou_none(valor, obrigatorio=(col in campos_obrigatorios))
                nova_coluna.append(novo_valor)
            df[col] = nova_coluna
    
    # Processar colunas de data
    for col in colunas_data:
        if col in df.columns:
            nova_coluna = []
            for valor in df[col]:
                novo_valor = forcar_data_ou_none(valor, obrigatorio=(col in campos_obrigatorios))
                nova_coluna.append(novo_valor)
            df[col] = nova_coluna
    
    return df



# Funções principais para processamento de empresas
def obter_cnpj_para_consulta():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        # Buscar CNPJs do ClickHouse
        empresas = query_clickhouse_com_retorno(
            HOST,
            PORT,
            USER,
            PASSWORD,
            "SELECT DISTINCT cnpj FROM db_bronze_srinfo.company_company WHERE cnpj IS NOT NULL"
        )
        df = pd.DataFrame(empresas, columns=['cnpj'])

        # Limpar e formatar os CNPJs
        df['cnpj2'] = df['cnpj'].str.replace('/', '', regex=True)
        df['cnpj2'] = df['cnpj2'].str.replace('-', '', regex=True)
        df['cnpj2'] = df['cnpj2'].str.replace('.', '', regex=False)
        df['cnpj_8digitos'] = df['cnpj2'].str.extract(r'(\d{8})')
        df = df[['cnpj', 'cnpj2', 'cnpj_8digitos']]

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")
    return df

def dtbricks_consulta_porte(empresas):
    """Busca no Databricks os cnpjs de 8 digitos informados."""
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        cnpj_8digitos = empresas['cnpj_8digitos'].tolist()
        query = f"""
        SELECT CD_CNPJ_BASICO, NM_RAZAO_SOCIAL, DS_PORTE_EMPRESA
        FROM datalake__trs.oni.rfb_cnpj__cadastro_empresa_f
        WHERE CD_CNPJ_BASICO IN ({','.join([f"'{cnpj}'" for cnpj in cnpj_8digitos])})
        """
        with connect_databricks() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                print("🟢 " + inspect.currentframe().f_code.co_name)
                return results
    except Exception as e:
        print(f"🔴 Erro: {e}")
        
def dtbricks_consulta_info_gerais(empresas):
    """Busca no Databricks os cnpjs completos informados."""
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        cnpj2 = empresas['cnpj2'].tolist()
        query = f"""
        SELECT CD_CNPJ, CD_CNPJ_BASICO, CD_CNPJ_ORDEM, CD_CNPJ_DV, DS_MATRIZ_FILIAL, NM_FANTASIA, CD_SIT_CADASTRAL, DS_SIT_CADASTRAL, DT_SIT_CADASTRAL, CD_MOTIVO_SIT_CADASTRAL, NM_CIDADE_EXTERIOR, CD_PAIS, DT_INICIO_ATIV, CD_CNAE20_SUBCLASSE_PRINCIPAL, CD_CNAE20_SUBCLASSE_SECUNDARIA, NM_TIPO_LOGRADOURO, NM_LOGRADOURO, NM_NUMERO_ESTBL, NM_COMPLEMENTO, NM_BAIRRO, CD_CEP, SG_UF, CD_MUN, NM_DDD_1, NM_TELEFONE_1, NM_DDD_2, NM_TELEFONE_2, NM_DDD_FAX, NM_FAX, NM_EMAIL
        FROM datalake__trs.oni.rfb_cnpj__cadastro_estbl_f
        WHERE CD_CNPJ IN ({','.join([f"'{cnpj}'" for cnpj in cnpj2])})
        """
        with connect_databricks() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results2 = cursor.fetchall()
                print("🟢 " + inspect.currentframe().f_code.co_name)

                return results2
    except Exception as e:
        print(f"🔴 Erro: {e}")

def juntar_e_processar_resultados(empresas, resultados, resultados2):
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        today = datetime.now()

        """Salva os resultados em um DataFrame."""
        df_resultados = pd.DataFrame(resultados, columns=["cnpj_8digitos", "razao_social", "porte"])
        df_resultados = df_resultados.merge(empresas, on='cnpj_8digitos', how='right')
        df_resultados['razao_social'] = df_resultados['razao_social'].str.replace(' EM RECUPERACAO JUDICIAL', '', regex=False)

        df_resultados2 = pd.DataFrame(resultados2, columns=["cnpj2", "cnpj_8digitos", "cd_cnpj_ordem", "cd_cnpj_dv", "ds_matriz_filial",
                                                            "nome_fantasia", "cd_sit_cadastral", "ds_sit_cadastral", "dt_sit_cadastral",
                                                            "cd_motivo_sit_cadastral", "nm_cidade_exterior", "cd_pais", "dt_inicio_ativ",
                                                            "cd_cnae20sub_principal", "cd_cnae20sub_secundaria", "nm_tipo_logradouro",
                                                            "nm_logradouro", "nm_numero_estbl", "nm_complemento", "nm_bairro",
                                                            "cd_cep", "sg_uf", "cd_mun", "nm_ddd_1", "nm_telefone_1", "nm_ddd_2",
                                                            "nm_telefone_2", "nm_ddd_fax", "nm_fax", "nm_email"])
        df_resultados2 = df_resultados2.merge(empresas, on='cnpj2', how='right')
        df_resultados_final = df_resultados2.merge(df_resultados, on='cnpj2', how='left')

        df_resultados_final['dt_carga'] = today

        # Campos de interesse e novos nomes das colunas
        campos_interesse = [
            'cd_cnpj_ordem',
            'cd_cnpj_dv',
            'ds_matriz_filial',
            'nome_fantasia',
            "cd_sit_cadastral",
            "ds_sit_cadastral",
            "dt_sit_cadastral",
            "cd_motivo_sit_cadastral",
            'nm_cidade_exterior',
            'cd_pais',
            'dt_inicio_ativ',
            'cd_cnae20sub_principal',
            'cd_cnae20sub_secundaria',
            'nm_tipo_logradouro',
            'nm_logradouro',
            'nm_numero_estbl',
            'nm_complemento',
            'nm_bairro',
            'cd_cep',
            'sg_uf',
            'cd_mun',
            'nm_ddd_1',
            'nm_telefone_1',
            'nm_ddd_2',
            'nm_telefone_2',
            'nm_ddd_fax',
            'nm_fax',
            'nm_email',
            'cnpj_x',
            'razao_social',
            'porte',
            'dt_carga'
        ]

        novos_nomes_e_ordem = {
            'cnpj_x': 'cnpj',
            'cd_cnpj_ordem': 'cd_cnpj_ordem',
            'cd_cnpj_dv': 'cd_cnpj_dv',
            'ds_matriz_filial': 'ds_matriz_filial',
            'razao_social': 'razao_social',
            'nome_fantasia': 'nome_fantasia',
            'porte': 'porte',
            "cd_sit_cadastral": 'cd_sit_cadastral',
            "ds_sit_cadastral": 'ds_sit_cadastral',
            "dt_sit_cadastral": 'dt_sit_cadastral',
            "cd_motivo_sit_cadastral": 'cd_motivo_sit_cadastral',
            'nm_cidade_exterior': 'nm_cidade_exterior',
            'cd_pais': 'cd_pais',
            'dt_inicio_ativ': 'dt_inicio_ativ',
            'cd_cnae20sub_principal': 'cd_cnae20sub_principal',
            'cd_cnae20sub_secundaria': 'cd_cnae20sub_secundaria',
            'nm_tipo_logradouro': 'nm_tipo_logradouro',
            'nm_logradouro': 'nm_logradouro',
            'nm_numero_estbl': 'nm_numero_estbl',
            'nm_complemento': 'nm_complemento',
            'nm_bairro': 'nm_bairro',
            'cd_cep': 'cd_cep',
            'sg_uf': 'sg_uf',
            'cd_mun': 'cd_mun',
            'nm_ddd_1': 'nm_ddd_1',
            'nm_telefone_1': 'nm_telefone_1',
            'nm_ddd_2': 'nm_ddd_2',
            'nm_telefone_2': 'nm_telefone_2',
            'nm_ddd_fax': 'nm_ddd_fax',
            'nm_fax': 'nm_fax',
            'nm_email': 'nm_email',
            'dt_carga': 'dt_carga',
        }

        df_resultados_final = df_resultados_final[campos_interesse]
        df_resultados_final = df_resultados_final.rename(columns=novos_nomes_e_ordem)
        df_resultados_final = df_resultados_final[novos_nomes_e_ordem.values()]
        
        print("🟢 " + inspect.currentframe().f_code.co_name)

        return df_resultados_final
    
    except Exception as e:
        print(f"🔴 Erro: {e}")
        return None

def enviar_para_clickhouse(df):
    """Envia dados processados para ClickHouse."""
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        if df is None or len(df) == 0:
            print("⚠️ Nenhum dado para inserir")
            return
        
        # 1. Obter próximo ID e adicionar IDs sequenciais
        proximo_id = obter_proximo_id()
        df_com_id = adicionar_ids_sequenciais(df, proximo_id)
        
        # 2. Aplicar conversão de tipos
        df_processado = converter_dataframe_para_clickhouse(df_com_id)

        # 3. Salvar localmente para envio posterior ao Sharepoint
        caminho_arquivo = os.path.join(ROOT, STEP3, "oni_companies.xlsx")
        df_processado.to_excel(caminho_arquivo, index=False)
        
        # 4. Conectar ao ClickHouse e inserir
        client = clickhouse_connect.get_client(host=HOST, port=PORT, user=USER, password=PASSWORD)

        client.insert_df(
            table="data_pii.tb_oni_companies",
            df=df_processado
        )
        
        print(f"🟢 {inspect.currentframe().f_code.co_name} - {len(df_processado)} registros inseridos com sucesso!")
        
    except Exception as e:
        print(f"🔴 Erro em {inspect.currentframe().f_code.co_name}: {e}")



# Função principal para processar empresas
def main_companies():
    """Função principal para processar empresas."""   
    try:
        # 0. Conectar à VPN
        connect_vpn()

        # 1. Obter CNPJs do arquivo
        empresas = obter_cnpj_para_consulta()
        
        if empresas is None or len(empresas) == 0:
            print("❌ Nenhuma empresa encontrada no arquivo")
            return
        
        # 2. Buscar dados no Databricks
        resultados = dtbricks_consulta_porte(empresas)
        resultados2 = dtbricks_consulta_info_gerais(empresas)
        
        if not resultados and not resultados2:
            print("❌ Nenhum resultado encontrado no Databricks")
            return
        
        # 3. Processar e salvar resultados
        df = juntar_e_processar_resultados(empresas, resultados, resultados2)
        
        if df is None:
            print("❌ Erro ao processar resultados")
            return
        
        # 4. Enviar para ClickHouse (com todos os tratamentos)
        enviar_para_clickhouse(df)

        # 5. Desconectar da VPN
        disconnect_vpn()
        
    except Exception as e:
        print(f"🔴 Erro geral em main_companies: {e}")