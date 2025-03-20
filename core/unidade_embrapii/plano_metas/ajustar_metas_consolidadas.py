import pandas as pd

ARQUIVO = r'unidade_embrapii/plano_metas/metas_consolidadas/metas_consolidadas.xlsx'
PLANO_METAS = r'unidade_embrapii/plano_metas/step_3_data_processed/plano_metas.xlsx'

def ajustar_metas_consolidadas():
    # Carrega o arquivo Excel
    df = pd.read_excel(ARQUIVO)
    
    # Função para formatar os valores na coluna 'valor'
    def formatar_valor(valor):
        if isinstance(valor, str):
            # Verifica se o valor é um percentual e converte para decimal
            if '%' in valor:
                return float(valor.replace('%', '').replace(',', '.')) / 100
            # Verifica se o valor é monetário e converte para float
            elif 'R$' in valor:
                return float(valor.replace('R$', '').replace('.', '').replace(',', '.'))
        return valor

    # Aplica a função de formatação na coluna 'valor'
    df['valor'] = df['valor'].apply(formatar_valor)
    
    # Salva o DataFrame ajustado de volta para o mesmo arquivo Excel
    df.to_excel(ARQUIVO, index=False)

    inserir_status()
    formatar_nome_metas()
    criar_coluna_considerar()


def inserir_status():
    # Carrega os arquivos Excel
    metas_consolidadas = pd.read_excel(ARQUIVO)
    plano_metas = pd.read_excel(PLANO_METAS)
    
    # Renomeia as colunas para o padrão desejado em 'metas_consolidadas'
    metas_consolidadas.rename(columns={'Título da meta': 'titulo_meta', 'id': 'id_plano_meta'}, inplace=True)

    # Faz o merge (junção) com base nos campos de chave
    metas_consolidadas = metas_consolidadas.merge(
        plano_metas[['id_plano_meta', 'status', 'unidade_embrapii', 'termo_cooperacao']],
        how='left',
        left_on='id_plano_meta',
        right_on='id_plano_meta'
    )

    # Reorganiza as colunas na ordem especificada
    colunas_ordenadas = ['id_plano_meta', 'unidade_embrapii', 'termo_cooperacao', 'status', 'titulo_meta', 'ano', 'valor']
    metas_consolidadas = metas_consolidadas[colunas_ordenadas]

    # Salva o DataFrame ajustado de volta para o mesmo arquivo Excel
    metas_consolidadas.to_excel(ARQUIVO, index=False)


def formatar_nome_metas():
    # Carrega o arquivo Excel
    metas_consolidadas = pd.read_excel(ARQUIVO)
    
    # Dicionário de substituição para os títulos das metas
    substituicoes = {
        'Contratação de empresas': 'Nº de empresas que contrataram',
        'Contratação de projetos': 'Nº de projetos contratados',
        'Empresas contratantes': 'Nº de empresas que contrataram',
        'Empresas prospectadas': 'Nº de empresas prospectadas',
        'Eventos com empresas': 'Nº de eventos com empresas',
        'Inserção de recursos humanos em projetos de PD&I': 'Inserção de recursos humanos em projetos de PD&I',
        'Número de propostas técnicas': 'Nº de propostas técnicas',
        'Participação de alunos em projetos de PD&I': 'Nº de alunos em projetos de PD&I',
        'Participação de alunos(as) em projetos de PD&I': 'Nº de alunos em projetos de PD&I',
        'Participação de empresas em eventos': 'Participação de empresas em eventos',
        'Participação financeira das empresas no portfólio': 'Percentual de participação financeira das empresas nos projetos contratados',
        'Participação financeira das empresas nos projetos contratados': 'Percentual de participação financeira das empresas nos projetos contratados',
        'Pedidos de propriedade intelectual': 'Nº de pedidos de PI',
        'Pedidos de Propriedade intelectual: (PI)': 'Nº de pedidos de PI',
        'Pedidos de propriedade intelectual¹': 'Nº de pedidos de PI',
        'Projetos contratados': 'Nº de projetos contratados',
        'Propostas técnicas': 'Nº de propostas técnicas',
        'Prospecção de empresas': 'Nº de empresas prospectadas',
        'Recursos aportados pela EMBRAPII': 'Valor R$ aportado pela Embrapii',
        'Recursos aportados pela Unidade EMBRAPII': 'Valor R$ aportado pela Unidade Embrapii',
        'Recursos aportados por empresas': 'Valor R$ aportado pelas empresas',
        'Satisfação das Empresas': 'Nota de satisfação das empresas',
        'Startups, micro e pequenas empresas contratantes': 'Nº de empresas startups, micro e pequenas contratantes',
        'Taxa de sucesso de projeto': 'Percentual de sucesso de projeto',
        'Taxa de sucesso de propostas técnicas': 'Percentual de sucesso de propostas técnicas',
        'Totais R$ por exercicio': 'Valor total R$ por exercício'
    }

    # Cria a coluna 'titulo_meta_ajustada' com os valores ajustados
    metas_consolidadas['titulo_meta_ajustada'] = metas_consolidadas['titulo_meta'].map(substituicoes).fillna(metas_consolidadas['titulo_meta'])
    
    # Reorganiza as colunas na ordem especificada
    colunas_ordenadas = ['id_plano_meta', 'unidade_embrapii', 'termo_cooperacao', 'status', 'titulo_meta', 'titulo_meta_ajustada', 'ano', 'valor']
    metas_consolidadas = metas_consolidadas[colunas_ordenadas]

    # Salva o DataFrame ajustado de volta para o mesmo arquivo Excel
    metas_consolidadas.to_excel(ARQUIVO, index=False)

def criar_coluna_considerar():
    # Carrega o arquivo Excel
    metas_consolidadas = pd.read_excel(ARQUIVO)
    
    # Função que simula a fórmula do Excel simplificada
    def considerar_computo(row):
        # Se a coluna D ('status') for 'Expirado'
        if row['status'] == 'Expirado':
            # Filtra as linhas com mesma unidade_embrapii e ano e com status 'Vigente'
            filtro = (
                (metas_consolidadas['unidade_embrapii'] == row['unidade_embrapii']) &
                (metas_consolidadas['ano'] == row['ano']) &
                (metas_consolidadas['status'] == 'Vigente')
            )
            
            # Verifica se há pelo menos uma linha que atende ao filtro
            if metas_consolidadas[filtro].shape[0] > 0:
                return 'Não'
            else:
                return 'Sim'
        else:
            return 'Sim'

    # Aplica a função para criar a nova coluna
    metas_consolidadas['considerar_computo_geral'] = metas_consolidadas.apply(considerar_computo, axis=1)
    
    # Salva o DataFrame ajustado de volta para o mesmo arquivo Excel
    metas_consolidadas.to_excel(ARQUIVO, index=False)