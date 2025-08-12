from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
from office365_api.connect_databricks import connect_databricks
from processar_excel import processar_excel
import inspect

load_dotenv()

ROOT = os.getenv('ROOT_BFA')
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, 'scripts'))

STEP_1_DATA_RAW = os.path.abspath(os.path.join(ROOT, 'data', 'step_1_data_raw'))
STEP_2_STAGE_AREA = os.path.abspath(os.path.join(ROOT, 'data', 'step_2_stage_area'))
STEP_3_DATA_PROCESSED = os.path.abspath(os.path.join(ROOT, 'data', 'step_3_data_processed'))


def obter_cnpj_8digitos():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        empresas = pd.read_excel(os.path.abspath(os.path.join(STEP_3_DATA_PROCESSED, 'bfa_projetos_empresas.xlsx')))
        print(empresas.head())
        empresas = empresas[['cnpj']].drop_duplicates()
        empresas['cnpj2'] = empresas['cnpj'].str.replace('/', '', regex=True)
        empresas['cnpj2'] = empresas['cnpj2'].str.replace('-', '', regex=True)
        empresas['cnpj2'] = empresas['cnpj2'].str.replace('.', '', regex=False)
        empresas['cnpj_8digitos'] = empresas['cnpj2'].str.extract(r'(\d{8})')
        
        empresas = empresas[['cnpj', 'cnpj2', 'cnpj_8digitos']]
        print(f"Número de empresas a procurar: {len(empresas['cnpj'])}")
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")
    return empresas

def buscar_no_databricks(empresas):
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
        
def buscar_no_databricks2(empresas):
    """Busca no Databricks os cnpjs completos informados."""
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        cnpj2 = empresas['cnpj2'].tolist()
        query = f"""
        SELECT CD_CNPJ, CD_CNPJ_BASICO, CD_CNPJ_ORDEM, CD_CNPJ_DV, DS_MATRIZ_FILIAL, NM_FANTASIA, NM_CIDADE_EXTERIOR, CD_PAIS, DT_INICIO_ATIV, CD_CNAE20_SUBCLASSE_PRINCIPAL, CD_CNAE20_SUBCLASSE_SECUNDARIA, NM_TIPO_LOGRADOURO, NM_LOGRADOURO, NM_NUMERO_ESTBL, NM_COMPLEMENTO, NM_BAIRRO, CD_CEP, SG_UF, CD_MUN, NM_DDD_1, NM_TELEFONE_1, NM_DDD_2, NM_TELEFONE_2, NM_DDD_FAX, NM_FAX, NM_EMAIL
        FROM datalake__trs.oni.rfb_cnpj__cadastro_estbl_f
        WHERE CD_CNPJ IN ({','.join([f"'{cnpj}'" for cnpj in cnpj2])})
        """
        with connect_databricks() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results2 = cursor.fetchall()
                print(f"Número de empresas encontradas: {len(results2)}")
                print("🟢 " + inspect.currentframe().f_code.co_name)
                return results2
    except Exception as e:
        print(f"🔴 Erro: {e}")

def salvar_resultados(empresas, resultados, resultados2, caminho_saida):
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        today = datetime.now()

        """Salva os resultados em um arquivo Excel."""
        df_resultados = pd.DataFrame(resultados, columns=["cnpj_8digitos", "razao_social", "porte"])
        df_resultados = df_resultados.merge(empresas, on='cnpj_8digitos', how='right')
        df_resultados['razao_social'] = df_resultados['razao_social'].str.replace(' EM RECUPERACAO JUDICIAL', '', regex=False)

        df_resultados2 = pd.DataFrame(resultados2, columns=["cnpj2", "cnpj_8digitos", "cd_cnpj_ordem", "cd_cnpj_dv", "ds_matriz_filial", "nome_fantasia", "nm_cidade_exterior", "cd_pais", "dt_inicio_ativ", "cd_cnae20sub_principal", "cd_cnae20sub_secundaria", "nm_tipo_logradouro", "nm_logradouro", "nm_numero_estbl", "nm_complemento", "nm_bairro", "cd_cep", "sg_uf", "cd_mun", "nm_ddd_1", "nm_telefone_1", "nm_ddd_2", "nm_telefone_2", "nm_ddd_fax", "nm_fax", "nm_email"])
        df_resultados2 = df_resultados2.merge(empresas, on='cnpj2', how='right')
        df_resultados_final = df_resultados2.merge(df_resultados, on='cnpj2', how='left')

        df_resultados_final['data_extracao'] = today
        
        df_resultados_final.to_excel(caminho_saida, index=False)
        print(f"Número de empresas final: {len(df_resultados_final['cnpj2'])}")
        print(f"Resultados salvos em: {caminho_saida}")
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")

def processar_novo_resultado():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        # Definições dos caminhos e nomes de arquivos
        nome = "bfa_empresas_info.xlsx"
        arquivo_origem = os.path.join(STEP_2_STAGE_AREA, nome)
        arquivo_destino = os.path.join(STEP_3_DATA_PROCESSED, nome)

        # Campos de interesse e novos nomes das colunas
        campos_interesse = [
            'cd_cnpj_ordem',
            'cd_cnpj_dv',
            'ds_matriz_filial',
            'nome_fantasia',
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
            'data_extracao'
        ]

        novos_nomes_e_ordem = {
            'cnpj_x': 'cnpj',
            'cd_cnpj_ordem': 'cd_cnpj_ordem',
            'cd_cnpj_dv': 'cd_cnpj_dv',
            'ds_matriz_filial': 'ds_matriz_filial',
            'razao_social': 'razao_social',
            'nome_fantasia': 'nome_fantasia',
            'porte': 'porte',
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
            'data_extracao': 'data_extracao',
        }

        processar_excel(arquivo_origem, campos_interesse, novos_nomes_e_ordem, arquivo_destino)
        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")

def main_companies():
    empresas = obter_cnpj_8digitos()
    resultados = buscar_no_databricks(empresas)
    resultados2 = buscar_no_databricks2(empresas)
    caminho_saida = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'bfa_empresas_info.xlsx'))
    salvar_resultados(empresas, resultados, resultados2, caminho_saida)
    processar_novo_resultado()

if __name__ == "__main__":
    main_companies()