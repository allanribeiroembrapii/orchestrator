import os
import pandas as pd
import hashlib
import urllib.parse
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def hash_arquivo(caminho_arquivo):
    """Calcula o hash MD5 de um arquivo."""
    hash_md5 = hashlib.md5()
    with open(caminho_arquivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def consolidar_planilhas(pasta_downloads):
    arquivos = [f for f in os.listdir(pasta_downloads) if f.endswith(('.xls', '.xlsx', '.xlsm'))]

    # Excluindo arquivos em branco ou que não são formulário de informações complementares
    arquivo_excluir = ["srinfo_partnership_fundsapproval.xlsx", "info_complementares.xlsx", "info_gerais.xlsm"]
    arquivos = [f for f in arquivos if f not in arquivo_excluir]

    registros = []
    hashes_processados = set()

    arquivo_n = 0
    for arquivo in arquivos:
        arquivo_n += 1
        print(f"Arquivo {arquivo_n} de {len(arquivos)}")

        nome_legivel = urllib.parse.unquote(arquivo)
        caminho = os.path.join(pasta_downloads, nome_legivel)
        try:
            hash_atual = hash_arquivo(caminho)
            if hash_atual in hashes_processados:
                print(f"Aviso: {nome_legivel} é duplicado e será ignorado.")
                continue
            hashes_processados.add(hash_atual)

            # Lendo os arquivos
            df = pd.read_excel(caminho, header=None)

            # Eliminando linhas totalmente vazias
            df.dropna(how='all', inplace=True)

            # Verificando se há ao menos três colunas para permitir deslocamento
            if df.shape[1] >= 3:
                # Verificando se a primeira coluna (coluna 0) está vazia nas primeiras linhas
                primeiras_linhas = df.head(10)
                if primeiras_linhas.iloc[:, 0].isna().sum() >= 8:  # mais de 80% das 10 primeiras células vazias
                    # Assumindo que os dados estão deslocados para colunas 1 e 2 (B e C)
                    df_recorte = df.iloc[:, 1:3].copy()
                    df_recorte.columns = ['pergunta', 'resposta']
                    df_recorte['arquivo'] = nome_legivel
                    registros.append(df_recorte)
                else:
                    # Assumindo que os dados estão nas colunas padrão 0 e 1 (A e B)
                    df_recorte = df.iloc[:, :2].copy()
                    df_recorte.columns = ['pergunta', 'resposta']
                    df_recorte['arquivo'] = nome_legivel
                    registros.append(df_recorte)
            elif df.shape[1] >= 2:
                df_recorte = df.iloc[:, :2].copy()
                df_recorte.columns = ['pergunta', 'resposta']
                df_recorte['arquivo'] = nome_legivel
                registros.append(df_recorte)

            else:
                print(f"Aviso: {nome_legivel} tem menos de 2 colunas relevantes.")
        except Exception as e:
            print(f"Erro ao processar {nome_legivel}: {e}")

    # Transformando a lista de dicionários em DataFrame
    df_final = pd.concat(registros, ignore_index=True)

    return df_final

def ajustes(df, pasta_saida):
    df_final = df

    # Removendo linhas com valor em branco ou NaN
    df_final = df_final[df_final['resposta'].notna() & (df_final['resposta'].astype(str).str.strip() != '')]

    # Retirando quebra de linha do nome das chaves
    df_final['pergunta'] = df_final['pergunta'].astype(str).str.replace('\n', ' ').str.strip()

    # Dicionário com renomeações das chaves
    renomear_chaves = {
        '% VALOR APORTADO EMBRAPII/BNDES:': 'pct_aporte_embrapii_bndes',
        '% VALOR APORTADO EMBRAPII:': 'pct_aporte_embrapii',
        '% VALOR APORTADO PEL0 SEBRAE:': 'pct_aporte_sebrae',
        '% VALOR APORTADO PELA UNIDADE EMBRAPII:': 'pct_aporte_unidade',
        '% VALOR APORTADO PELA(S) EMPRESA(S):': 'pct_aporte_empresa',
        '% VALOR APORTADO PELA(S) EMPRESAS(S):': 'pct_aporte_empresa',
        '% VALOR APORTADO PELO SEBRAE:': 'pct_aporte_sebrae',
        '1ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I:': 'tecnologias_habilitadoras',
        '1ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&i:': 'tecnologias_habilitadoras',
        '1ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I:': 'areas_aplicacao',
        '2ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I:': 'tecnologias_habilitadoras',
        '2ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I:': 'areas_aplicacao',
        '3ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I:': 'tecnologias_habilitadoras',
        '3ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I:': 'areas_aplicacao',
        '4ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I:': 'tecnologias_habilitadoras',
        '4ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I:': 'areas_aplicacao',
        'AMPLIAR A GAMA DE BENS OU SERVIÇOS OFERTADOS:': 'Ampliar a gama de bens ou serviços ofertados',
        'AMPLIAR A PARTICIPAÇÃO DA EMPRESA NO MERCADO:': 'Ampliar a participação da empresa no mercado',
        'AUMENTAR A CAPACIDADE DE PRODUÇÃO OU DE PRESTAÇÃO DE SERVIÇOS:': 'Aumentar a capacidade de produção ou de prestação de serviços',
        'AUMENTAR A FLEXIBILIDADE DA PRODUÇÃO OU DA PRESTAÇÃO DE SERVIÇOS:': 'Aumentar a flexibilidade da produção ou da prestação de serviços',
        'CASO TENHA ESCOLHIDO ""OUTROS"", PREENCHA AO LADO': 'outros',
        'CASO TENHA ESCOLHIDO "OUTROS", PREENCHA AO LADO': 'outros',
        'CNAE (GRUPO 3 DÍGITOS) DA EMPRESA DA 1ª EMPRESA:': 'cnae',
        'CNAE (GRUPO 3 DÍGITOS) DA EMPRESA DA 2ª EMPRESA:': 'cnae',
        'CNAE (GRUPO 3 DÍGITOS) DA EMPRESA DA 3ª EMPRESA:': 'cnae',
        'CNAE (GRUPO 3 DÍGITOS) DA EMPRESA DA EMPRESA:': 'cnae',
        'CNAE (GRUPO 3 DÍGITOS) DA EMPRESA:': 'cnae',
        'CNAE de idustrialização (GRUPO 3 DÍGITOS) DA EMPRESA:': 'cnae',
        'CNPJ DA 1ª EMPRESA:': 'cnpj',
        'CNPJ DA 2ª EMPRESA:': 'cnpj',
        'CNPJ DA 3ª EMPRESA:': 'cnpj',
        'CNPJ DA EMPRESA:': 'cnpj',
        'CNPJ:': 'cnpj',
        'CÓDIGO DE NEGOCIAÇÃO:': 'codigo_negociacao',
        'ENQUADRAR EM REGULAÇÕES E NORMAS-PADRÃO RELATIVAS AO MERCADO INTERNO OU EXTERNO:': 'Enquadrar em regulações e normas-padrão relativas ao mercado interno ou externo',
        'ESCALA DA TRL NA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO DO PROJETO):': 'trl_final',
        'ESCALA TRL DA 1ª MACROENTREGA DO PROJETO (NO INÍCIO DA SUA EXECUÇÃO):': 'trl_inicial',
        'ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO DO PROJETO):': 'trl_final',
        'EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OUALTO/DISRUPTIVO:': 'impacto_tecnologia',
        'EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU ALTO/DISRUPTIVO:': 'impacto_tecnologia',
        'EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO,': 'impacto_tecnologia',
        'EXPECTATIVA DE TEMPO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÂO) DESENVOLVIDA(S) - BAIXO, MÉDIO OU ALTO/DISRUPTIVO:': 'tempo_tecnologia',
        'EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS ACONCLUSÃO DO PROJETO):': 'tempo_chegada_mercado',
        'EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃO DO PROJETO):': 'tempo_chegada_mercado',
        'EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM NÚMERO DE MESES APÓS A CONCLUSÃO DO PROJETO):': 'tempo_chegada_mercado',
        'FAIXA DE ROB NO ÚLTIMO ANO DA 1ª EMPRESA:': 'rob',
        'FAIXA DE ROB NO ÚLTIMO ANO DA 2ª EMPRESA:': 'rob',
        'FAIXA DE ROB NO ÚLTIMO ANO DA 3ª EMPRESA:': 'rob',
        'FAIXA DE ROB NO ÚLTIMO ANO DA EMPRESA:': 'rob',
        'FAIXA DE ROB NO ÚLTIMO ANO:': 'rob',
        'FOCO DO CONTRATO BNDES/EMBRAPII DA SOLICITAÇÃO DE RESERVA:': 'foco',
        'FONTE DE RECURSO SECUNDÁRIA:': 'fonte_secundaria',
        'MELHORAR A QUALIDADE DOS BENS OU SERIÇOS:': 'Melhorar a qualidade dos bens ou serviços',
        'MELHORAR A QUALIDADE DOS BENS OU SERVIÇOS:': 'Melhorar a qualidade dos bens ou serviços',
        'MODALIDADE DE APORTE DO PROJETO:': 'modalidade_aporte',
        'MODALIDADE DE FINANCIAMENTO DO PROJETO:': 'modalidade_financiamento',
        'MODALIDADE DE PROJETO:': 'modalidade_financiamento',
        'NOME DO PROJETO:': 'projeto',
        'NOME FANTASIA DA 1ª EMPRESA:': 'nome_fantasia',
        'NOME FANTASIA DA 2ª EMPRESA:': 'nome_fantasia',
        'NOME FANTASIA DA 3ª EMPRESA:': 'nome_fantasia',
        'NOME FANTASIA DA EMPRESA:': 'nome_fantasia',
        'NOME FANTASIA:': 'nome_fantasia',
        'Nº DE MACROENTREGAS PLANEJADAS:': 'num_macroentregas',
        'NÚMERO DE FUNCIONÁRIOS': 'num_funcionarios',
        'NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO DA 1ª EMPRESA:': 'num_funcionarios',
        'NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO DA 2ª EMPRESA:': 'num_funcionarios',
        'NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO DA 3ª EMPRESA:': 'num_funcionarios',
        'NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO DA EMPRESA:': 'num_funcionarios',
        'NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO:': 'num_funcionarios',
        'O PROJETO IRÁ USAR RECURSOS DOS CONTRATOS SEBRAE': 'recursos_sebrae',
        'OBJETIVO DO PROJETO:': 'objetivo',
        'PERMITIR ABERTURA DE NOVOS MERCADOS:': 'Permitir abertura de novos mercados',
        'PERMITIR ABRERTURA DE NOVOS MERCADOS:': 'Permitir abertura de novos mercados',
        'PERMITIR CONTROLAR ASPECTOS LIGADOS À SAÚDE E/OU À SEGURANÇA:': 'Permitir controlar aspectos ligados à saúde e/ou à segurança',
        'PERMITIR MANTER A PARTICIPAÇÃO DA EMPRESA NO MERCADO:': 'Permitir manter a participação da empresa no mercado',
        'PERMITIR REDUZIR O IMPACTO SOBRE O MEIO AMBIENTE:': 'Permitir reduzir o impacto sobre o meio ambiente',
        'PORTE EMPRESA POR NÚMERO DE FUNCIONÁRIOS:': 'porte_num_funcionarios',
        'QUAL É A EXPECTATIVA DE SIGNIFICÂNCIA DA(S) INOVAÇÃO(ÕES) QUE SERÁ(ÃO) GERADA(S) NO PROJETO?': 'significancia_inovacao',
        'QUAL É A EXPECTATIVA DE SIGNIFICÂNCIA DA(S) INOVAÇÃO(ÕES) QUE SERÁ(ÃO) GERADA(S) NO': 'significancia_inovacao',
        'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOSSEGUINTES PONTOS:': 'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS:',
        'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS': 'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS:',
        'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS:': 'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS:',
        'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS: ': 'QUAL É O GRAU DE IMPACTO ESPERADO DO PROJETO (NA EMPRESA E NO MERCADO), EM RELAÇÃO AOS SEGUINTES PONTOS:',
        'RAZÃO SOCIAL DA 10º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 11º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 12º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 13º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 14º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 15º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 1ª EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 1º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 2ª EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 2º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 3ª EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 3º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 4º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 5º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 6º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 7º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 8º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA 9º EMPRESA:': 'empresa',
        'RAZÃO SOCIAL DA EMPRESA:': 'empresa',
        'RECICLAGEM DE RESÍDUOS, ÁGUAS RESIDUAIS OU MATERIAIS PARA VENDA E/OU REUTILIZAÇÃO:': 'Reciclagem de resíduos, águas residuais ou materiais para venda e/ou reutilização',
        'REDUZIR O CONSUMO DE ENERGIA:': 'Reduzir o consumo de energia',
        'REDUZIR O CONSUMO DE MATÉRIAS-PRIMAS:': 'Reduzir o consumo de matérias-primas',
        'REDUZIR O CONSUMO DE ÁGUA:': 'Reduzir o consumo de água',
        'REDUZIR OS CUSTOS DE PRODUÇÃO OU DOS SERVIÇOS PRESTADOS': 'Reduzir os custos de produção ou dos serviços prestados',
        'REDUZIR OS CUSTOS DE PRODUÇÃO OU DOS SERVIÇOS PRESTADOS:': 'Reduzir os custos de produção ou dos serviços prestados',
        'REDUZIR OS CUSTOS DO TRABALHO:': 'Reduzir os custos do trabalho',
        'REDUZIR OS CUSTOS DO TRABALHO: ': 'Reduzir os custos do trabalho',
        'REDUZIR RUÍDOS OU A CONTAMINAÇÃO DO SOLO, DA ÁGUA OU DO AR:': 'Reduzir ruídos ou a contaminação do solo, da água ou do ar',
        'REDUÇÃO DA \'PEGADA\' DE CO (PRODUÇÃO TOTAL DE CO) DE SUA EMPRESA:': 'Redução da pegada de CO (produção total de CO) de sua empresa',
        'RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO (DESCRITIVO - MÁX DE 500 CARACTERES):': 'resultados_esperados',
        'RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO (DESCRITIVO - MÁXIMO DE 500 CARACTERES):': 'resultados_esperados',
        'SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIARENOVÁVEIS:': 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        'SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA RENOVÁVEIS:': 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        'SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE': 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        'SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU PERIGOSAS:': 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        'SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU': 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        'TIPO DE IMPACTO PRODUTIVO ESPERADO COM O PROJETO:': 'impacto_produtivo',
        'TÍTULO DO PROJETO:': 'projeto',
        'UF DO CNPJ DA 1ª EMPRESA:': 'uf',
        'UF DO CNPJ DA 2ª EMPRESA:': 'uf',
        'UF DO CNPJ DA 3ª EMPRESA:': 'uf',
        'UF DO CNPJ DA EMPRESA:': 'uf',
        'UF DO CNPJ:': 'uf',
        'UNIDADE EMBRAPII:': 'unidade_embrapii',
        'UNIDADE EMBRAPII: ': 'unidade_embrapii',
        'VALOR APORTADO PELA EMBRAPII/BNDES:': 'valor_embrapii_bndes',
        'VALOR APORTADO PELA EMBRAPII:': 'valor_embrapii',
        'VALOR APORTADO PELA UNIDADE EMBRAPII:': 'valor_unidade_embrapii',
        'VALOR APORTADO PELA(S) EMPRESA(S):': 'valor_empresa',
        'VALOR APORTADO PELA(S) EMPRESAS(S):': 'valor_empresa',
        'VALOR APORTADO PELO SEBRAE:': 'valor_sebrae',
        'VALOR TOTAL:': 'valor_total',
    }

    # Aplicando as renomeações nas chaves
    df_final['pergunta'] = df_final['pergunta'].replace(renomear_chaves)

    # Criando a coluna de tickets
    df_final['ticket'] = df_final['arquivo'].str.extract(r'_(\d+)\.')


    ## SALVANDO O ARQUIVO COM AS PERGUNTAS COMPLEMENTARES SOBRE O PROJETO
    # Escolhendo as chaves desejadas
    chaves_desejadas = [
        'Ampliar a gama de bens ou serviços ofertados',
        'Ampliar a participação da empresa no mercado',
        'Aumentar a capacidade de produção ou de prestação de serviços',
        'Aumentar a flexibilidade da produção ou da prestação de serviços',
        'Enquadrar em regulações e normas-padrão relativas ao mercado interno ou externo',
        'Melhorar a qualidade dos bens ou serviços',
        'Permitir abertura de novos mercados',
        'Permitir controlar aspectos ligados à saúde e/ou à segurança',
        'Permitir manter a participação da empresa no mercado',
        'Permitir reduzir o impacto sobre o meio ambiente',
        'Reduzir o consumo de água',
        'Reduzir o consumo de energia',
        'Reduzir o consumo de matérias-primas',
        'Reduzir os custos de produção ou dos serviços prestados',
        'Reduzir os custos do trabalho',
        'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        'Reduzir ruídos ou a contaminação do solo, da água ou do ar',
        'Reciclagem de resíduos, águas residuais ou materiais para venda e/ou reutilização',
        'Redução da pegada de CO (produção total de CO) de sua empresa'
    ]

    # Filtrar o DataFrame
    df_filtrado = df_final[df_final['pergunta'].isin(chaves_desejadas)]

    # Reordenando
    df_filtrado = df_filtrado[['arquivo', 'ticket', 'pergunta', 'resposta']]

    # Modificando palavras específicas
    palavras_alvo = {
        'Alto': 'Alta',
        'Além': 'Alta',
        'Sim': 'Alta',
        'SIM': 'Alta',
        'Significativo': 'Média',
        'Media': 'Média',
        'Medio': 'Média',
        'Apesar': 'Média',
        'Baixo': 'Baixa',
        'Pouco': 'Baixa',
        'Não': 'Não relevante',
        'não': 'Não relevante'
    }

    # Aplica substituições
    for palavra, novo_valor in palavras_alvo.items():
        mask = df_filtrado['resposta'].str.contains(palavra, na=False)
        df_filtrado.loc[mask, 'resposta'] = novo_valor

    df_filtrado = df_filtrado.drop_duplicates(subset=['ticket', 'pergunta', 'resposta'])


    # Salvando na pasta de saída
    df_filtrado.to_excel(os.path.join(pasta_saida, "info_complementares.xlsx"), index=False)


    ## SALVANDO O ARQUIVO COM INFORMAÇÕES GERAIS DO PROJETO, EMPRESAS ETC
    # Agrupando por Arquivo + Chave e juntando os valores com "; " se for o caso
    df_agrupado = df_final.groupby(['arquivo', 'ticket', 'pergunta'])['resposta'].apply(lambda x: '; '.join(x.astype(str))).reset_index()

    # Pivotando
    df_pivot = df_agrupado.pivot(index=['arquivo', 'ticket'], columns='pergunta', values='resposta').reset_index()

    # Modificando palavras específicas
    df_pivot.loc[df_pivot['areas_aplicacao'].astype(str).str.contains(r'[1-9]', na=False), 'areas_aplicacao'] = ''
    df_pivot.loc[df_pivot['outros'].astype(str).str.contains(r'[1-9]', na=False), 'outros'] = ''
    df_pivot['cnpj'] = df_pivot['cnpj'].astype(str).str.replace('cnpj ', '', case=False)
    df_pivot.loc[df_pivot['num_macroentregas'].astype(str).str.contains('duas', case=False, na=False), 'num_macroentregas'] = 2
    df_pivot.loc[df_pivot['num_macroentregas'].astype(str).str.contains('três', case=False, na=False), 'num_macroentregas'] = 3

    trl = [
        '3. Estabelecimento de função crítica de forma analítica, experimental e/ou prova de conceito',
        '4. Validação funcional dos componentes em ambiente de laboratório',
        '5. Validação das funções críticas dos componentes em ambiente relevante',
        '6. Demonstração de funções críticas do protótipo em ambiente relevante',
        '7. Demonstração de protótipo do sistema em ambiente operacional',
        '8. Sistema qualificado e finalizado',
        '9. Sistema operando e comprovado em todos os aspectos de sua missão operacional'
    ]
    for i in range(len(trl)):
        df_pivot.loc[df_pivot['trl_inicial'].astype(str).str.contains(str(i+3), na=False), 'trl_inicial'] = trl[i]
        df_pivot.loc[df_pivot['trl_final'].astype(str).str.contains(str(i+3), na=False), 'trl_final'] = trl[i]

    valores = [
        'pct_aporte_embrapii',
        'pct_aporte_embrapii_bndes',
        'pct_aporte_empresa',
        'pct_aporte_sebrae',
        'pct_aporte_unidade',
        'valor_embrapii',
        'valor_embrapii_bndes',
        'valor_empresa',
        'valor_sebrae',
        'valor_unidade_embrapii',
        'valor_total'
    ]

    for i in range(len(valores)):
        df_pivot[valores[i]] = df_pivot[valores[i]].astype(str).apply(lambda x: x.replace('.', '') if 'R$ ' in x else x)
        df_pivot[valores[i]] = df_pivot[valores[i]].str.replace('R$ ', '', case=False)
        df_pivot[valores[i]] = df_pivot[valores[i]].str.replace(',', '.', case=False)
        df_pivot[valores[i]] = df_pivot[valores[i]].apply(lambda x: x.split(';')[0].strip() if ';' in x else x)
        df_pivot[valores[i]] = df_pivot[valores[i]].astype(float)


    # Escolhendo as colunas
    colunas_informacoes = [
        'arquivo',
        'ticket',
        'codigo_negociacao',
        'unidade_embrapii',
        'modalidade_financiamento',
        'modalidade_aporte',
        'foco',
        'trl_inicial',
        'trl_final',
        'num_macroentregas',
        'projeto',
        'objetivo',
        'recursos_sebrae',
        'fonte_secundaria',
        'impacto_produtivo',
        'areas_aplicacao',
        'tecnologias_habilitadoras',
        'outros',
        'resultados_esperados',
        'tempo_chegada_mercado',
        'impacto_tecnologia',
        'significancia_inovacao',
        'cnpj',
        'empresa',
        'nome_fantasia',
        'uf',
        'cnae',
        'rob',
        'num_funcionarios',
        'pct_aporte_embrapii',
        'pct_aporte_embrapii_bndes',
        'pct_aporte_empresa',
        'pct_aporte_sebrae',
        'pct_aporte_unidade',
        'valor_embrapii',
        'valor_embrapii_bndes',
        'valor_empresa',
        'valor_sebrae',
        'valor_unidade_embrapii',
        'valor_total'
        ]

    df_pivot = df_pivot[colunas_informacoes]

    colunas_para_usar = df_pivot.columns.difference(['arquivo'])
    df_pivot = df_pivot.drop_duplicates(subset=colunas_para_usar)

    df_pivot.to_excel(os.path.join(pasta_saida, 'info_gerais.xlsx'), index=False)
    print(f'Arquivos salvos com sucesso na pasta {pasta_saida}')