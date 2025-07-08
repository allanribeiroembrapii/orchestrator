import os
import inspect
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from glob import glob
from core.classifier_gepes.start_clean import start_clean
from core.classifier_gepes.connection.sharepoint import sharepoint_post

load_dotenv()
ROOT = os.getenv("ROOT_CLASSIFIER_GEPES")
STEP_1_DATA_RAW = os.getenv("STEP_1_DATA_RAW")
STEP_2_STAGE_AREA = os.getenv("STEP_2_STAGE_AREA")
STEP_3_DATA_PROCESSED = os.getenv("STEP_3_DATA_PROCESSED")

PROJETOS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'projetos.xlsx'))
AI_SUGGESTIONS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'ai_suggestions.xlsx'))
AI_RATINGS = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'ai_ratings.xlsx'))
TEC_VERDE = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'tecnologias_verdes.xlsx'))
TEC_HABILITADORA = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'techabilitadora_manual.xlsx'))
PUBLICO_ALVO = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'publico_alvo.xlsx'))
TIPO_ENTREGAVEL = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, 'tipo_entregavel.xlsx'))

AIA_STAGE_AREA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'starea_aia.xlsx'))
TECVERDE_STAGE_AREA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'starea_tecver.xlsx'))
TECHABILITADORA_STAGE_AREA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'starea_techabilitadora.xlsx'))
PUBALVO_STAGE_AREA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'starea_pubalvo.xlsx'))
ENTREGAVEL_STAGE_AREA = os.path.abspath(os.path.join(ROOT, STEP_2_STAGE_AREA, 'starea_entregavel.xlsx'))
CLASSIFICACAO_PROJETOS = os.path.abspath(os.path.join(ROOT, STEP_3_DATA_PROCESSED, 'classificacao_projetos_app_classifier.xlsx'))

# Credenciais do banco Heroku
DB_HOST = 'cbhk6rs82poqi7.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com'
DB_NAME = 'dfotgpmc8offkr'
DB_USER = 'ufko09qfvgbn4g'
DB_PASS = 'p895a87e702cb837c9a1a83505f0c5eab91d65f4a870fcf303120f278a7dc4fe1'
DB_PORT = '5432'
SCHEMA = 'gepes'


def buscar_dados():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Conectar ao banco de dados
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        sslmode='require'
    )

    # Criar cursor para listar as tabelas
    cur = conn.cursor()

    # Buscar todas as tabelas do schema
    cur.execute(f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_type = 'BASE TABLE';
    """, (SCHEMA,))

    # Extrair os nomes das tabelas
    tables = [row[0] for row in cur.fetchall()]

    # Baixar os dados de cada tabela e salvar como Excel
    for table in tables:
        try:
            query = f'SELECT * FROM {SCHEMA}.{table};'
            df = pd.read_sql_query(query, conn)
            arquivo = f'{table}.xlsx'
            caminho = os.path.abspath(os.path.join(ROOT, STEP_1_DATA_RAW, arquivo))
            df.to_excel(caminho, index=False)
        except Exception as e:
            print(f'❌ Erro ao processar tabela {table}: {e}')

    # Encerrar conexão
    cur.close()
    conn.close()
    print("🟢 " + inspect.currentframe().f_code.co_name)

def tratar_aia():
    # Carrega os dataframes
    df_projeto = pd.read_excel(PROJETOS)
    df_classificacao = pd.read_excel(AI_SUGGESTIONS)
    df_rating = pd.read_excel(AI_RATINGS)

    # Renomeia 'id' para 'id_projeto' para permitir merge
    df_projeto = df_projeto.rename(columns={'id': 'id_projeto'})
    df_projeto = df_projeto[['id_projeto', 'codigo_projeto']]

    # Mantém apenas as colunas desejadas em df_classificacao
    df_classificacao = df_classificacao[[
        'id_projeto', '_aia_n1_macroarea', '_aia_n2_segmento',
        '_aia_n3_dominio_afeito', '_aia_n3_dominio_outro', 'justificativa'
    ]]

    # Junta os domínios com "; ", tratando valores nulos
    df_classificacao['_aia_n3_dominio'] = (
        df_classificacao['_aia_n3_dominio_afeito'].fillna('') +
        '; ' +
        df_classificacao['_aia_n3_dominio_outro'].fillna('')
    ).str.strip('; ').replace('', pd.NA)

    # Remove colunas antigas
    df_classificacao = df_classificacao[[
        'id_projeto', '_aia_n1_macroarea', '_aia_n2_segmento', '_aia_n3_dominio', 'justificativa'
    ]]

    # Faz o merge com os códigos dos projetos
    df_final = df_classificacao.merge(df_projeto, on='id_projeto', how='left')

    # Reorganiza as colunas
    df_final = df_final[[
        'id_projeto', 'codigo_projeto', '_aia_n1_macroarea',
        '_aia_n2_segmento', '_aia_n3_dominio', 'justificativa'
    ]]

    # Transforma a coluna de domínios em lista, separando por ";"
    df_final['_aia_n3_dominio'] = df_final['_aia_n3_dominio'].fillna('')
    df_final['_aia_n3_dominio'] = df_final['_aia_n3_dominio'].apply(
        lambda x: [d.strip() for d in x.split(';') if d.strip()]
    )

    # Explode os domínios em múltiplas linhas
    df_explodido = df_final.explode('_aia_n3_dominio').reset_index(drop=True)

    # Rating
    df_rating = df_rating[df_rating['tipo'] == 'aia']
    df_rating['timestamp'] = pd.to_datetime(df_rating['timestamp'])
    df_rating = df_rating.sort_values(['id_projeto', 'timestamp'], ascending=[True, False])
    df_rating = df_rating.drop_duplicates(subset='id_projeto', keep='first')
    df_rating = df_rating[['id_projeto', 'rating', 'observacoes', 'nome_usuario', 'timestamp']]

    # Merge com os domínios explodidos
    df_explodido = df_explodido.merge(df_rating, on='id_projeto', how='left')


    # Criar coluna "status"
    df_explodido['status'] = df_explodido['rating'].apply(
        lambda x: 'Validado por Humano' if pd.notna(x) else 'Classificado por IA'
    )

    # Criar coluna "tipo_classificacao"
    df_explodido['tipo_classificacao'] = 'Área de Interesse de Aplicação'


    colunas = {
        'id_projeto': 'id_projeto',
        'codigo_projeto': 'codigo_projeto',
        'status': 'status',
        'tipo_classificacao': 'tipo_classificacao',
        '_aia_n1_macroarea': 'nivel_1',
        '_aia_n2_segmento': 'nivel_2',
        '_aia_n3_dominio': 'nivel_3',
        'justificativa': 'observacoes',
        'rating': 'rating',
        'nome_usuario': 'rating_usuario',
        'timestamp': 'rating_timestamp',
        'observacoes': 'rating_observacoes',
    }

    # Aplicar renomeação
    df_explodido = df_explodido.rename(columns=colunas)
    df_explodido = df_explodido[list(colunas.values())]

    # Salva o resultado final
    df_explodido.to_excel(AIA_STAGE_AREA, index=False)

def tratar_tec_habilitadora():
    # Carrega os dataframes
    df_projeto = pd.read_excel(PROJETOS)
    df_ai = pd.read_excel(AI_SUGGESTIONS)
    df_tec_habilitadora = pd.read_excel(TEC_HABILITADORA)
    df_rating = pd.read_excel(AI_RATINGS)

    # Renomeia 'id' para 'id_projeto' para permitir merge
    df_projeto = df_projeto.rename(columns={'id': 'id_projeto'})
    df_projeto = df_projeto[['id_projeto', 'codigo_projeto']]

    # Mantém apenas as colunas desejadas em df_classificacao
    df_ai = df_ai[[
        'id_projeto', 'techabilitadora_categoria', 'techabilitadora_subcategoria',
        'techabilitadora_justificativa',
    ]]

    df_ai = df_ai.rename(columns={'techabilitadora_categoria': 'categoria'})
    df_ai = df_ai.rename(columns={'techabilitadora_subcategoria': 'subcategoria'})
    df_ai = df_ai.rename(columns={'techabilitadora_justificativa': 'observacoes'})

    # Adiciona ao df_tec_habilitadora todos os registros novos de df_ai
    ids_existentes = df_tec_habilitadora['id_projeto'].unique()
    df_novos = df_ai[~df_ai['id_projeto'].isin(ids_existentes)]
    df_tec_habilitadora = pd.concat([df_tec_habilitadora, df_novos], ignore_index=True)


    # Faz o merge com os códigos dos projetos
    df_final = df_tec_habilitadora.merge(df_projeto, on='id_projeto', how='left')

    # Reorganiza as colunas
    df_final = df_final[[
        'id_projeto', 'codigo_projeto', 'categoria',
        'subcategoria', 'observacoes',
    ]]

    # Rating
    df_rating = df_rating[df_rating['tipo'] == 'techabilitadora']
    df_rating['timestamp'] = pd.to_datetime(df_rating['timestamp'])
    df_rating = df_rating.sort_values(['id_projeto', 'timestamp'], ascending=[True, False])
    df_rating = df_rating.drop_duplicates(subset='id_projeto', keep='first')
    df_rating = df_rating[['id_projeto', 'rating', 'observacoes', 'nome_usuario', 'timestamp']]
    df_rating = df_rating.rename(columns={'observacoes': 'rating_observacoes'})

    # Merge com os domínios explodidos
    df_final = df_final.merge(df_rating, on='id_projeto', how='left')

    # Criar coluna "status"
    df_final['status'] = df_final['rating'].apply(
        lambda x: 'Validado por Humano' if pd.notna(x) else 'Classificado por IA'
    )

    # Criar coluna "tipo_classificacao"
    df_final['tipo_classificacao'] = 'Tecnologia Habilitadora'
    df_final['nivel_3'] = 'Não se aplica'

    colunas = {
        'id_projeto': 'id_projeto',
        'codigo_projeto': 'codigo_projeto',
        'status': 'status',
        'tipo_classificacao': 'tipo_classificacao',
        'categoria': 'nivel_1',
        'subcategoria': 'nivel_2',
        'nivel_3': 'nivel_3',
        'observacoes': 'observacoes',
        'rating': 'rating',
        'nome_usuario': 'rating_usuario',
        'timestamp': 'rating_timestamp',
        'rating_observacoes': 'rating_observacoes',
    }

    # Aplicar renomeação
    df_final = df_final.rename(columns=colunas)
    df_final = df_final[list(colunas.values())]

    # Substituir FALSO e VERDADEIRO por Não e Sim na coluna nivel_1
    df_final['nivel_1'] = df_final['nivel_1'].replace({
        'VERDADEIRO': 'Sim',
        'FALSO': 'Não',
        True: 'Sim',
        False: 'Não'
    })

    # Salva o resultado final
    df_final.to_excel(TECHABILITADORA_STAGE_AREA, index=False)

def tratar_tec_verde():
    # Carrega os dataframes
    df_projeto = pd.read_excel(PROJETOS)
    df_classificacao = pd.read_excel(AI_SUGGESTIONS)
    df_tec_verde = pd.read_excel(TEC_VERDE)
    df_rating = pd.read_excel(AI_RATINGS)

    # Renomeia 'id' para 'id_projeto' para permitir merge
    df_projeto = df_projeto.rename(columns={'id': 'id_projeto'})
    df_projeto = df_projeto[['id_projeto', 'codigo_projeto']]

    # Mantém apenas as colunas desejadas em df_classificacao
    df_classificacao = df_classificacao[[
        'id_projeto', 'tecverde_se_aplica', 'tecverde_classe',
        'tecverde_subclasse', 'tecverde_justificativa'
    ]]

    df_classificacao = df_classificacao.rename(columns={'tecverde_se_aplica': 'se_aplica'})
    df_classificacao = df_classificacao.rename(columns={'tecverde_classe': 'classe'})
    df_classificacao = df_classificacao.rename(columns={'tecverde_subclasse': 'subclasse'})
    df_classificacao = df_classificacao.rename(columns={'tecverde_justificativa': 'observacoes'})

    # Adiciona ao df_tec_verde todos os registros novos de df_classificacao
    ids_existentes = df_tec_verde['id_projeto'].unique()
    df_novos = df_classificacao[~df_classificacao['id_projeto'].isin(ids_existentes)]
    df_tec_verde = pd.concat([df_tec_verde, df_novos], ignore_index=True)


    # Faz o merge com os códigos dos projetos
    df_final = df_tec_verde.merge(df_projeto, on='id_projeto', how='left')

    # Reorganiza as colunas
    df_final = df_final[[
        'id_projeto', 'codigo_projeto', 'se_aplica',
        'classe', 'subclasse', 'observacoes',
    ]]

    # Rating
    df_rating = df_rating[df_rating['tipo'] == 'tecverde']
    df_rating['timestamp'] = pd.to_datetime(df_rating['timestamp'])
    df_rating = df_rating.sort_values(['id_projeto', 'timestamp'], ascending=[True, False])
    df_rating = df_rating.drop_duplicates(subset='id_projeto', keep='first')
    df_rating = df_rating[['id_projeto', 'rating', 'observacoes', 'nome_usuario', 'timestamp']]
    df_rating = df_rating.rename(columns={'observacoes': 'rating_observacoes'})

    # Merge com os domínios explodidos
    df_final = df_final.merge(df_rating, on='id_projeto', how='left')

    # Criar coluna "status"
    df_final['status'] = df_final['rating'].apply(
        lambda x: 'Validado por Humano' if pd.notna(x) else 'Classificado por IA'
    )

    # Criar coluna "tipo_classificacao"
    df_final['tipo_classificacao'] = 'Tecnologia Verde'

    colunas = {
        'id_projeto': 'id_projeto',
        'codigo_projeto': 'codigo_projeto',
        'status': 'status',
        'tipo_classificacao': 'tipo_classificacao',
        'se_aplica': 'nivel_1',
        'classe': 'nivel_2',
        'subclasse': 'nivel_3',
        'observacoes': 'observacoes',
        'rating': 'rating',
        'nome_usuario': 'rating_usuario',
        'timestamp': 'rating_timestamp',
        'rating_observacoes': 'rating_observacoes',
    }

    # Aplicar renomeação
    df_final = df_final.rename(columns=colunas)
    df_final = df_final[list(colunas.values())]

    # Substituir FALSO e VERDADEIRO por Não e Sim na coluna nivel_1
    df_final['nivel_1'] = df_final['nivel_1'].replace({
        'VERDADEIRO': 'Sim',
        'FALSO': 'Não',
        True: 'Sim',
        False: 'Não'
    })

    # Salva o resultado final
    df_final.to_excel(TECVERDE_STAGE_AREA, index=False)

def tratar_publico_alvo():
    # Carrega os dataframes
    df_projeto = pd.read_excel(PROJETOS)
    df_ai = pd.read_excel(AI_SUGGESTIONS)
    df_pub_alvo = pd.read_excel(PUBLICO_ALVO)
    df_rating = pd.read_excel(AI_RATINGS)

    # Renomeia 'id' para 'id_projeto' para permitir merge
    df_projeto = df_projeto.rename(columns={'id': 'id_projeto'})
    df_projeto = df_projeto[['id_projeto', 'codigo_projeto']]

    # Mantém apenas as colunas desejadas em df_classificacao
    df_ai = df_ai[[
        'id_projeto', 'publico_alvo_categoria', 'publico_alvo_justificativa',
    ]]

    df_ai = df_ai.rename(columns={'publico_alvo_categoria': 'categoria'})
    df_ai = df_ai.rename(columns={'publico_alvo_justificativa': 'observacoes'})

    # Adiciona ao df_tec_habilitadora todos os registros novos de df_ai
    ids_existentes = df_pub_alvo['id_projeto'].unique()
    df_novos = df_ai[~df_ai['id_projeto'].isin(ids_existentes)]
    df_pub_alvo = pd.concat([df_pub_alvo, df_novos], ignore_index=True)


    # Faz o merge com os códigos dos projetos
    df_final = df_pub_alvo.merge(df_projeto, on='id_projeto', how='left')

    # Reorganiza as colunas
    df_final = df_final[[
        'id_projeto', 'codigo_projeto', 'categoria', 'observacoes',
    ]]

    # Rating
    df_rating = df_rating[df_rating['tipo'] == 'publico_alvo']
    df_rating['timestamp'] = pd.to_datetime(df_rating['timestamp'])
    df_rating = df_rating.sort_values(['id_projeto', 'timestamp'], ascending=[True, False])
    df_rating = df_rating.drop_duplicates(subset='id_projeto', keep='first')
    df_rating = df_rating[['id_projeto', 'rating', 'observacoes', 'nome_usuario', 'timestamp']]
    df_rating = df_rating.rename(columns={'observacoes': 'rating_observacoes'})

    # Merge com os domínios explodidos
    df_final = df_final.merge(df_rating, on='id_projeto', how='left')

    # Criar coluna "status"
    df_final['status'] = df_final['rating'].apply(
        lambda x: 'Validado por Humano' if pd.notna(x) else 'Classificado por IA'
    )

    # Criar coluna "tipo_classificacao"
    df_final['tipo_classificacao'] = 'Público Alvo'
    df_final['nivel_2'] = 'Não se aplica'
    df_final['nivel_3'] = 'Não se aplica'

    colunas = {
        'id_projeto': 'id_projeto',
        'codigo_projeto': 'codigo_projeto',
        'status': 'status',
        'tipo_classificacao': 'tipo_classificacao',
        'categoria': 'nivel_1',
        'nivel_2': 'nivel_2',
        'nivel_3': 'nivel_3',
        'observacoes': 'observacoes',
        'rating': 'rating',
        'nome_usuario': 'rating_usuario',
        'timestamp': 'rating_timestamp',
        'rating_observacoes': 'rating_observacoes',
    }

    # Aplicar renomeação
    df_final = df_final.rename(columns=colunas)
    df_final = df_final[list(colunas.values())]

    # Substituir FALSO e VERDADEIRO por Não e Sim na coluna nivel_1
    df_final['nivel_1'] = df_final['nivel_1'].replace({
        'VERDADEIRO': 'Sim',
        'FALSO': 'Não',
        True: 'Sim',
        False: 'Não'
    })

    # Salva o resultado final
    df_final.to_excel(PUBALVO_STAGE_AREA, index=False)

def tratar_tipo_entregavel():
    # Carrega os dataframes
    df_projeto = pd.read_excel(PROJETOS)
    df_ai = pd.read_excel(AI_SUGGESTIONS)
    df_entregavel = pd.read_excel(TIPO_ENTREGAVEL)
    df_rating = pd.read_excel(AI_RATINGS)

    # Renomeia 'id' para 'id_projeto' para permitir merge
    df_projeto = df_projeto.rename(columns={'id': 'id_projeto'})
    df_projeto = df_projeto[['id_projeto', 'codigo_projeto']]

    # Mantém apenas as colunas desejadas em df_classificacao
    df_ai = df_ai[[
        'id_projeto', 'tipo_entregavel_categoria', 'tipo_entregavel_justificativa',
    ]]

    df_ai = df_ai.rename(columns={'tipo_entregavel_categoria': 'categoria'})
    df_ai = df_ai.rename(columns={'tipo_entregavel_justificativa': 'observacoes'})

    # Adiciona ao df_tec_habilitadora todos os registros novos de df_ai
    ids_existentes = df_entregavel['id_projeto'].unique()
    df_novos = df_ai[~df_ai['id_projeto'].isin(ids_existentes)]
    df_entregavel = pd.concat([df_entregavel, df_novos], ignore_index=True)

    # Faz o merge com os códigos dos projetos
    df_final = df_entregavel.merge(df_projeto, on='id_projeto', how='left')

    # Reorganiza as colunas
    df_final = df_final[[
        'id_projeto', 'codigo_projeto', 'categoria', 'observacoes',
    ]]

    # Rating
    df_rating = df_rating[df_rating['tipo'] == 'publico_alvo']
    df_rating['timestamp'] = pd.to_datetime(df_rating['timestamp'])
    df_rating = df_rating.sort_values(['id_projeto', 'timestamp'], ascending=[True, False])
    df_rating = df_rating.drop_duplicates(subset='id_projeto', keep='first')
    df_rating = df_rating[['id_projeto', 'rating', 'observacoes', 'nome_usuario', 'timestamp']]
    df_rating = df_rating.rename(columns={'observacoes': 'rating_observacoes'})

    # Merge com os domínios explodidos
    df_final = df_final.merge(df_rating, on='id_projeto', how='left')

    # Criar coluna "status"
    df_final['status'] = df_final['rating'].apply(
        lambda x: 'Validado por Humano' if pd.notna(x) else 'Classificado por IA'
    )

    # Criar coluna "tipo_classificacao"
    df_final['tipo_classificacao'] = 'Tipo de Entregável'
    df_final['nivel_2'] = 'Não se aplica'
    df_final['nivel_3'] = 'Não se aplica'

    colunas = {
        'id_projeto': 'id_projeto',
        'codigo_projeto': 'codigo_projeto',
        'status': 'status',
        'tipo_classificacao': 'tipo_classificacao',
        'categoria': 'nivel_1',
        'nivel_2': 'nivel_2',
        'nivel_3': 'nivel_3',
        'observacoes': 'observacoes',
        'rating': 'rating',
        'nome_usuario': 'rating_usuario',
        'timestamp': 'rating_timestamp',
        'rating_observacoes': 'rating_observacoes',
    }

    # Aplicar renomeação
    df_final = df_final.rename(columns=colunas)
    df_final = df_final[list(colunas.values())]

    # Substituir FALSO e VERDADEIRO por Não e Sim na coluna nivel_1
    df_final['nivel_1'] = df_final['nivel_1'].replace({
        'VERDADEIRO': 'Sim',
        'FALSO': 'Não',
        True: 'Sim',
        False: 'Não'
    })

    # Salva o resultado final
    df_final.to_excel(ENTREGAVEL_STAGE_AREA, index=False)

def agregar_tabelas():
    # Encontra todos os arquivos .xlsx na pasta
    arquivos = glob(os.path.join(ROOT, STEP_2_STAGE_AREA, "*.xlsx"))

    # Carrega e agrega todos os dataframes
    df_lista = [pd.read_excel(arquivo) for arquivo in arquivos]
    df_geral = pd.concat(df_lista, ignore_index=True)

    # Exporta resultado final
    df_geral.to_excel(CLASSIFICACAO_PROJETOS, index=False)

def tratar_dados():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    tratar_aia()
    tratar_tec_verde()
    tratar_tec_habilitadora()
    tratar_publico_alvo()
    tratar_tipo_entregavel()
    agregar_tabelas()

    print("🟢 " + inspect.currentframe().f_code.co_name)

def main_classifier_gepes():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    start_clean()
    buscar_dados()
    tratar_dados()
    sharepoint_post()

    print("🟢 " + inspect.currentframe().f_code.co_name)

if __name__ == "__main__":
    main_classifier_gepes()