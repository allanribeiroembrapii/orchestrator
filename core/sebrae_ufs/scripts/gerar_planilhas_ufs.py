import os
import pandas as pd
from dotenv import load_dotenv
from office365_api.upload_files_sebrae import upload_files
from scripts.gerar_planilha_geral import copiar_planilha_formatada
from shutil import copyfile
from openpyxl import load_workbook

#carregar .env
load_dotenv()
ROOT = os.getenv('ROOT_SEBRAE_UFS')

STEP1 = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw'))
STEP2 = os.path.abspath(os.path.join(ROOT, 'step_2_stage_area'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))

def gerar_planilhas_uf(planilha_geral, combinado, municipios, port_ue, proj_emp, port_emp, port_me, gerar_novo = False, enviar_pasta_sebrae = False):
    # juntando combinado com planilha_geral
    planilha_geral_uf = pd.merge(planilha_geral, combinado, on = 'codigo_projeto', how = 'left')

    # obtendo codigo_projeto por uf
    codigos_uf = []
    for uf in municipios['sg_uf'].unique():
        if uf == 'EX':
            continue

        # filtrando os projetos por uf
        projetos_uf = planilha_geral_uf[planilha_geral_uf['uf'] == uf]

        # obtendo os codigos dos projetos
        for codigo in projetos_uf['codigo_projeto'].unique():
            codigos_uf.append({'uf': uf, 'codigo_projeto': codigo})
    
    codigos_uf = pd.DataFrame(codigos_uf)

    # obtendo planilhas por uf
    # Iterar por cada UF única no DataFrame codigos_uf
    for uf in codigos_uf['uf'].unique():
        uf_lower = str(uf).lower()
        # Obter os códigos de projeto associados à UF
        codigos = codigos_uf[codigos_uf['uf'] == uf]['codigo_projeto'].unique()

        if gerar_novo == False:
            # lendo as planilhas anteriores
            anterior_port = pd.read_excel(os.path.abspath(os.path.join(STEP1, f'sebrae_{uf}.xlsx')), sheet_name = f'BD_portfolio_{uf}')
            anterior_ue = pd.read_excel(os.path.abspath(os.path.join(STEP1, f'sebrae_{uf}.xlsx')), sheet_name = f'BD_UEs_{uf}')
            anterior_proj_emp = pd.read_excel(os.path.abspath(os.path.join(STEP1, f'sebrae_{uf}.xlsx')), sheet_name = f'BD_projetos_empresas_{uf}')
            anterior_emp = pd.read_excel(os.path.abspath(os.path.join(STEP1, f'sebrae_{uf}.xlsx')), sheet_name = f'BD_empresas_{uf}')
            anterior_me = pd.read_excel(os.path.abspath(os.path.join(STEP1, f'sebrae_{uf}.xlsx')), sheet_name = f'BD_macroentregas_{uf}')

            # mudando as planilhas anteriores para dado_atual = 0
            anterior_port['dado_atual'] = 0
            anterior_ue['dado_atual'] = 0
            anterior_proj_emp['dado_atual'] = 0
            anterior_emp['dado_atual'] = 0
            anterior_me['dado_atual'] = 0

        ####### PLANILHA GERAL #######

        # Filtrar a planilha_geral pelos códigos da UF
        df_filtrado = planilha_geral[planilha_geral['codigo_projeto'].isin(codigos)]

        # escolhendo as coluna, renomeando e reordenando
        novos_nomes_e_ordem = {
            'n': 'n',
            'dado_atual': 'dado_atual',
            'data_extracao': 'data_extracao',
            'codigo_projeto': 'codigo_projeto',
            'codigo_negociacao': 'codigo_negociacao',
            'unidade_embrapii': 'unidade_embrapii',
            'data_contrato': 'data_contrato',
            'data_termino': 'data_termino',
            'valor_total': 'valor_total',
            'titulo_publico': 'titulo_publico',
            'descricao_publica': 'descricao_publica',
            'tipo_projeto': 'tipo_projeto',
            'tecnologia_habilitadora': 'tecnologia_habilitadora',
            'macroentregas': 'num_macroentregas',
            'status': 'status',
            'pct_aceites': 'percentual_projeto',
            'trl_inicial': 'trl_inicial',
            'trl_final': 'trl_final',
            'valor_unidade_embrapii': 'valor_unidade_embrapii',
            'valor_empresas_apoiadas': 'valor_empresas_apoiadas',
            'valor_outras_empresas': 'valor_outras_empresas',
            'valor_sebrae': 'valor_sebrae',
            'valor_embrapii': 'valor_embrapii',
            'modalidade_financiamento': 'modalidade_financiamento',
            'empresas_menor_porte': 'empresas_menor_porte',
            'empresas_maior_porte': 'empresas_maior_porte',
            'pedidos_pi': 'pedidos_pi',
        }

        planilha_geral_final = df_filtrado[novos_nomes_e_ordem.keys()]
        planilha_geral_final = planilha_geral_final.rename(columns=novos_nomes_e_ordem)

        if gerar_novo == False:
            planilha_geral_final['n'] = range(max(anterior_port['n']) + 1, max(anterior_port['n']) + len(planilha_geral_final) + 1)
        else:
            planilha_geral_final['n'] = range(1, len(planilha_geral_final) + 1)

        # ajustando coluna de data
        planilha_geral_final['data_contrato'] = pd.to_datetime(planilha_geral_final['data_contrato'], format='%d/%m/%Y', errors='coerce').dt.date
        planilha_geral_final['data_termino'] = pd.to_datetime(planilha_geral_final['data_termino'], format='%d/%m/%Y', errors='coerce').dt.date

        # ajustando coluna de percentual
        planilha_geral_final['percentual_projeto'] = planilha_geral_final['percentual_projeto'] * 100

        # ajustando coluna de modalidade
        planilha_geral_final['modalidade_financiamento'] = planilha_geral_final['modalidade_financiamento'].apply(
            lambda x: 'DT' if '(DT)' in x else ('ET' if '(ET)' in x else 'AT')
        )

        # juntando a planilha anterior com a nova
        if gerar_novo == False:
            planilha_geral_final = pd.concat([anterior_port, planilha_geral_final], ignore_index=True)



        ####### PLANILHA AUXILIAR DE UEs #######
        port_ue_filtrado = port_ue[port_ue['codigo_projeto'].isin(codigos)]

        # Selecionar as colunas desejadas
        colunas_desejadas_ues = [
            'unidade_embrapii',
            'ue_responsavel_institucional',
            'tipo_instituicao',
            'zip_code',
            'address',
            'municipio',
            'uf',
            'competencias_tecnicas',
            'cnpj'
            ]   

        # agrupando por unidade e selecionando as colunas necessárias
        port_ue_filtrado = port_ue_filtrado[colunas_desejadas_ues].groupby(['unidade_embrapii'], as_index=False).first()

        if gerar_novo == False:
            port_ue_filtrado['n'] = range(max(anterior_ue['n']) + 1, max(anterior_ue['n']) + len(port_ue_filtrado) + 1)
        else:
            port_ue_filtrado['n'] = range(1, len(port_ue_filtrado) + 1)

        port_ue_filtrado['dado_atual'] = 1
        port_ue_filtrado['data_extracao'] = pd.to_datetime('today').date()
        colunas_desejadas_ues = [
            'n',
            'dado_atual',
            'data_extracao',
            'unidade_embrapii',
            'ue_responsavel_institucional',
            'tipo_instituicao',
            'zip_code',
            'address',
            'municipio',
            'uf',
            'competencias_tecnicas',
            'cnpj'
        ]

        # renomeando as colunas
        port_ue_filtrado = port_ue_filtrado[colunas_desejadas_ues].rename(columns={
            'unidade_embrapii': 'unidade_embrapii',
            'ue_responsavel_institucional': 'responsavel_institucional',
            'tipo_instituicao': 'tipo_instituicao',
            'zip_code': 'cep',
            'address': 'endereco',
            'municipio': 'municipio',
            'uf': 'uf',
            'competencias_tecnicas': 'competencias_tecnicas',
            'cnpj': 'cnpj_representante_financeiro'
        })

        # juntando a planilha anterior com a nova
        if gerar_novo == False:
            port_ue_filtrado = pd.concat([anterior_ue, port_ue_filtrado], ignore_index=True)



        ####### PLANILHA AUXILIAR PROJETOS EMPRESAS #######
        projetos_empresas = proj_emp[proj_emp['codigo_projeto'].isin(codigos)]

        if gerar_novo == False:
            projetos_empresas['n'] = range(max(anterior_proj_emp['n']) + 1, max(anterior_proj_emp['n']) + len(projetos_empresas) + 1)
        else:
            projetos_empresas['n'] = range(1, len(projetos_empresas) + 1)

        projetos_empresas['dado_atual'] = 1
        projetos_empresas['data_extracao'] = pd.to_datetime('today').date()
        colunas_desejadas_proj_emp = [
            'n',
            'dado_atual',
            'data_extracao',
            'codigo_projeto',
            'cnpj'
        ]
        projetos_empresas = projetos_empresas[colunas_desejadas_proj_emp]

        # juntando a planilha anterior com a nova
        if gerar_novo == False:
            projetos_empresas = pd.concat([anterior_proj_emp, projetos_empresas], ignore_index=True)



        ####### PLANILHA AUXILIAR DE EMPRESAS #######
        # pegando informações mais recentes de oni_companies
        port_emp_filtrado = port_emp[port_emp['codigo_projeto'].isin(codigos)]

        # Selecionar as colunas desejadas
        colunas_desejadas_emp = [
                'cnpj',
                'empresa_x',
                'contatos',
                'emails_contatos',
                'telefones_contatos',
                'zip_code',
                'neighborhood',
                'municipio',
                'uf',
                'porte',
                'faixa_faturamento_x'
                ]      

        # agrupando por empresa e selecionando as colunas desejadas
        port_emp_filtrado = port_emp_filtrado[colunas_desejadas_emp].groupby(['cnpj'], as_index=False).first()
        
        if gerar_novo == False:
            port_emp_filtrado['n'] = range(max(anterior_emp['n']) + 1, max(anterior_emp['n']) + len(port_emp_filtrado) + 1)
        else:
            port_emp_filtrado['n'] = range(1, len(port_emp_filtrado) + 1)

        port_emp_filtrado['dado_atual'] = 1
        port_emp_filtrado['data_extracao'] = pd.to_datetime('today').date()
        colunas_desejadas_emp = [
            'n',
            'dado_atual',
            'data_extracao',
            'cnpj',
            'empresa_x',
            'contatos',
            'emails_contatos',
            'telefones_contatos',
            'zip_code',
            'neighborhood',
            'municipio',
            'uf',
            'porte',
            'faixa_faturamento_x'
        ]

        # renomeando as colunas
        port_emp_filtrado = port_emp_filtrado[colunas_desejadas_emp].rename(columns={
            'cnpj': 'cnpj',
            'empresa_x': 'razao_social',
            'contatos': 'contato_declarado',
            'emails_contatos': 'e-mail_de_contato',
            'telefones_contatos': 'telefone',
            'zip_code': 'cep',
            'neighborhood': 'bairro',
            'municipio': 'municipio',
            'uf': 'uf',
            'porte': 'porte',
            'faixa_faturamento_x': 'faixa_faturamento'
            })
        
        # juntando a planilha anterior com a nova
        if gerar_novo == False:
            port_emp_filtrado = pd.concat([anterior_emp, port_emp_filtrado], ignore_index=True)
        


        ####### PLANILHA AUXILIAR DE MACROENTREGAS #######
        # juntando as planilhas
        port_me_filtrado = port_me[port_me['codigo_projeto'].isin(codigos)]

        # Selecionar as colunas desejadas
        colunas_desejadas_me = [
            'codigo_projeto',
            'num_macroentrega',
            'titulo',
            'descricao_macroentrega',
            'valor_embrapii_me',
            'valor_empresa_me',
            'valor_unidade_embrapii_me',
            'data_inicio_planejado',
            'data_termino_planejado',
            'data_inicio_real',
            'data_termino_real',
            'percentual_executado',
            'data_aceitacao'
            ]   

        # agrupando por projeto e macroentrega e selecionando as colunas desejadas
        port_me_filtrado = port_me_filtrado[colunas_desejadas_me].groupby(['codigo_projeto', 'num_macroentrega'], as_index=False).first()

        # calculando o valor total
        port_me_filtrado['valor_total'] = port_me_filtrado['valor_embrapii_me'] + port_me_filtrado['valor_empresa_me'] + port_me_filtrado['valor_unidade_embrapii_me']

        if gerar_novo == False:
            port_me_filtrado['n'] = range(max(anterior_me['n']) + 1, max(anterior_me['n']) + len(port_me_filtrado) + 1)
        else:
            port_me_filtrado['n'] = range(1, len(port_me_filtrado) + 1)

        port_me_filtrado['dado_atual'] = 1
        port_me_filtrado['data_extracao'] = pd.to_datetime('today').date()

        # Selecionar as colunas desejadas
        colunas_desejadas_me2 = [
            'n',
            'dado_atual',
            'data_extracao',
            'codigo_projeto',
            'num_macroentrega',
            'titulo',
            'descricao_macroentrega',
            'valor_total',
            'data_inicio_planejado',
            'data_termino_planejado',
            'data_inicio_real',
            'data_termino_real',
            'percentual_executado',
            'data_aceitacao'
            ]  
        
        # selecionando somente as desejadas
        port_me_filtrado = port_me_filtrado[colunas_desejadas_me2]

        # ajustando colunas de data
        campos_data = ['data_extracao', 'data_inicio_planejado', 'data_termino_planejado', 'data_inicio_real', 'data_termino_real', 'data_aceitacao']
        for campo in campos_data:
            if campo in port_me_filtrado.columns:
                port_me_filtrado[campo] = pd.to_datetime(port_me_filtrado[campo], format='%d/%m/%Y', errors='coerce').dt.date

        # juntando a planilha anterior com a nova
        if gerar_novo == False:
            port_me_filtrado = pd.concat([anterior_me, port_me_filtrado], ignore_index=True)


        ####### SALVANDO AS INFORMAÇÕES #######

        caminho_arquivo = os.path.abspath(os.path.join(STEP3, f'sebrae_{uf}.xlsx'))

        if not gerar_novo:
            # Copia o arquivo base
            origem = os.path.abspath(os.path.join(STEP1, f'sebrae_{uf}.xlsx'))
            copyfile(origem, caminho_arquivo)

            # Copia a aba Dicionário preservando a formatação
            copiar_planilha_formatada(origem, caminho_arquivo, 'Dicionário')

        # Escrevendo cada DataFrame em uma aba diferente
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:          
            planilha_geral_final.to_excel(writer, sheet_name= f'BD_portfolio_{uf}', index=False)
            port_ue_filtrado.to_excel(writer, sheet_name= f'BD_UEs_{uf}', index=False)
            projetos_empresas.to_excel(writer, sheet_name= f'BD_projetos_empresas_{uf}', index=False)
            port_emp_filtrado.to_excel(writer, sheet_name= f'BD_empresas_{uf}', index=False)
            port_me_filtrado.to_excel(writer, sheet_name= f'BD_macroentregas_{uf}', index=False)

         # Garante que ao menos uma aba está visível
        wb = load_workbook(caminho_arquivo)
        abas_visiveis = [sheet for sheet in wb.worksheets if sheet.sheet_state == 'visible']
        if not abas_visiveis:
            wb.worksheets[0].sheet_state = 'visible'
        wb.save(caminho_arquivo)
        wb.close()

        if enviar_pasta_sebrae == True:
            upload_files(
                pasta_arquivos = STEP3,
                destino = f'Acompanhamento Descentralizado//SEBRAE_{uf}//base_de_dados_sebrae_{uf_lower}',
                arquivo_especifico = os.path.abspath(os.path.join(STEP3, f'sebrae_{uf}.xlsx'))
            )