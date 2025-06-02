import os
import fitz
import pandas as pd
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import io

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
ROOT = os.getenv("ROOT")
STEP1 = os.path.abspath(os.path.join(ROOT, "step_1_data_raw"))
STEP2 = os.path.abspath(os.path.join(ROOT, "step_2_stage_area"))
STEP3 = os.path.abspath(os.path.join(ROOT, "step_3_data_processed"))

# Processa os PDFs
def ler_pdfs():
    # Lista de frases de interesse
    frases_interesse = [
        "UNIDADE EMBRAPII",
        "CÓDIGO DE NEGOCIAÇÃO",
        "MODALIDADE DE FINANCIAMENTO DO PROJETO",
        "FOCO DO CONTRATO BNDES/EMBRAPII DA SOLICITAÇÃO DE RESERVA",
        "FONTE DE RECURSO SECUNDÁRIA",
        "EMPRESA:",
        "RAZÃO SOCIAL DA 1ª EMPRESA",
        "RAZÃO SOCIAL DA 1º EMPRESA",
        "RAZÃO SOCIAL DA 2ª EMPRESA",
        "RAZÃO SOCIAL DA 3ª EMPRESA",
        "RAZÃO SOCIAL DA 4ª EMPRESA",
        "NOME FANTASIA",
        "CNPJ",
        "UF DO CNPJ",
        "NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO",
        "FAIXA DE ROB NO ÚLTIMO ANO",
        "CNAE (GRUPO 3 DÍGITOS) DA EMPRESA",
        "VALOR TOTAL",
        "VALOR APORTADO PELA EMBRAPII",
        "VALOR APORTADO PELA EMBRAPII/BNDES",
        "% VALOR APORTADO EMBRAPII",
        "% VALOR APORTADO EMBRAPII/BNDES",
        "VALOR APORTADO PELA(S) EMPRESA(S)",
        "% VALOR APORTADO PELA(S) EMPRESA(S)",
        "VALOR APORTADO PELO SEBRAE",
        "% VALOR APORTADO PEL0 SEBRAE",
        "% VALOR APORTADO PELO SEBRAE",
        "VALOR APORTADO PELA UNIDADE EMBRAPII",
        "% VALOR APORTADO PELA UNIDADE EMBRAPII",
        "NOME DO PROJETO",
        "OBJETIVO DO PROJETO",
        "TIPO DE IMPACTO PRODUTIVO ESPERADO COM O PROJETO",
        "1ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I",
        "2ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I",
        "3ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I",
        "1ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I",
        "2ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I",
        "3ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I",
        "CASO TENHA ESCOLHIDO \"OUTROS\", PREENCHA AO LADO",
        "Nº DE MACROENTREGAS PLANEJADAS",
        "ESCALA TRL DA 1ª MACROENTREGA DO PROJETO (NO INÍCIO DA SUA EXECUÇÃO)",
        "ESCALA TRL DA 1ª MACROENTREGA DO PROJETO (NO INÍCIO DA SUA",
        "EXECUÇÃO)",
        "ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO DO PROJETO)",
        "ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO DO",
        "ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO",
        "RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO (DESCRITIVO - MÁX DE 500 CARACTERES)",
        "RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO (DESCRITIVO -",
        "RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO",
        "(DESCRITIVO - MÁX DE 500 CARACTERES)",
        "MÁX DE 500 CARACTERES)",
        "A CONCLUSÃO DO PROJETO)",
        "CONCLUSÃO DO PROJETO)",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃ",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃO",
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃO DO PROJETO)",
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO,",
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO",
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU",
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU ALTO/DISRUPTIVO",
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE",
        "SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU ALTO/DISRUPTIVO",
        "MÉDIO OU ALTO/DISRUPTIVO"
        "OU ALTO/DISRUPTIVO",
        "ALTO/DISRUPTIVO:",
        "QUAL É A EXPECTATIVA DE SIGNIFICÂNCIA DA(S) INOVAÇÃO(ÕES) QUE",
        "QUAL É A EXPECTATIVA DE SIGNIFICÂNCIA DA(S) INOVAÇÃO(ÕES) QUE SERÁ(ÃO) GERADA(S) NO PROJETO?",
        "O PROJETO IRÁ USAR RECURSOS DOS CONTRATOS SEBRAE",
        "MODALIDADE DE APORTE DO PROJETO",
        "AMPLIAR A GAMA DE BENS OU SERVIÇOS OFERTADOS",
        "AMPLIAR A PARTICIPAÇÃO DA EMPRESA NO MERCADO",
        "AUMENTAR A CAPACIDADE DE PRODUÇÃO OU DE PRESTAÇÃO DE SERVIÇOS",
        "AUMENTAR A CAPACIDADE DE PRODUÇÃO OU DE PRESTAÇÃO DE",
        "AUMENTAR A FLEXIBILIDADE DA PRODUÇÃO OU DA PRESTAÇÃO DE SERVIÇOS",
        "ENQUADRAR EM REGULAÇÕES E NORMAS-PADRÃO RELATIVAS AO MERCADO INTERNO OU EXTERNO",
        "MERCADO INTERNO OU EXTERNO",
        "MELHORAR A QUALIDADE DOS BENS OU SERVIÇOS",
        "PERMITIR ABRERTURA DE NOVOS MERCADOS",
        "PERMITIR ABERTURA DE NOVOS MERCADOS",
        "PERMITIR CONTROLAR ASPECTOS LIGADOS À SAÚDE E/OU À SEGURANÇA",
        "SEGURANÇA",
        "PERMITIR MANTER A PARTICIPAÇÃO DA EMPRESA NO MERCADO",
        "PERMITIR REDUZIR O IMPACTO SOBRE O MEIO AMBIENTE",
        "REDUZIR O CONSUMO DE ÁGUA",
        "REDUZIR O CONSUMO DE ENERGIA",
        "REDUZIR O CONSUMO DE MATÉRIAS-PRIMAS",
        "REDUZIR OS CUSTOS DE PRODUÇÃO OU DOS SERVIÇOS PRESTADOS",
        "REDUZIR OS CUSTOS DO TRABALHO",
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU PERIGOSAS",
        "MENOS CONTAMINANTES OU PERIGOSAS",
        "CONTAMINANTES OU PERIGOSAS",
        "PERIGOSAS",
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU",
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU ",
        "SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA RENOVÁVEIS",
        "SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA",
        "SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE",
        "ENERGIA RENOVÁVEIS",
        "RENOVÁVEIS",
        "COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA RENOVÁVEIS",
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS",
        "REDUZIR RUÍDOS OU A CONTAMINAÇÃO DO SOLO, DA ÁGUA OU DO AR",
        "RECICLAGEM DE RESÍDUOS, ÁGUAS RESIDUAIS OU MATERIAIS PARA VENDA E/OU REUTILIZAÇÃO",
        "VENDA E/OU REUTILIZAÇÃO",
        "REDUÇÃO DA 'PEGADA' DE CO (PRODUÇÃO TOTAL DE CO) DE SUA EMPRESA"
    ]

    # Ordenar frases de interesse da maior para a menor para evitar sobreposição (ex: "UF DO CNPJ" antes de "CNPJ")
    frases_interesse = sorted(frases_interesse, key=lambda x: -len(x))


    # Frases que devem ser ignoradas
    frases_excluir = [
        "Assinatura do responsável pela Unidade EMBRAPII",
        "RESPOSTAS",
        "INFORMAÇÕES GERAIS",
        "FORMULÁRIO PARA SOLICITAÇÃO DE RESERVA RECURSOS", 
        "CONTRATO SEBRAE/EMBRAPII",
        "Página"
    ]

    # Lista para armazenar os dados
    coletado = []
    arquivo_n = 0

    for arquivo in os.listdir(STEP1):
        if arquivo.lower().endswith('.pdf'):
            arquivo_n += 1
            caminho_arquivo = os.path.join(STEP1, arquivo)
            nome_arquivo = arquivo
            doc = fitz.open(caminho_arquivo)

            for pagina_num in range(len(doc)):
                pagina = doc.load_page(pagina_num)

                # Tenta extrair texto diretamente
                texto = pagina.get_text()
                if texto is None or len(texto.strip()) < 800:
                    # Muito pouco texto: faz OCR
                    print(f"OCR necessário na página {pagina_num+1} do arquivo {nome_arquivo}")
                    pix = pagina.get_pixmap(dpi=300)
                    img = Image.open(io.BytesIO(pix.tobytes()))
                    texto = pytesseract.image_to_string(img, lang='por')

                else:
                    print(f"Texto extraído normalmente da página {pagina_num+1} do arquivo {nome_arquivo}")

                linhas = texto.split('\n')

                i = 0
                while i < len(linhas):
                    linha = linhas[i].strip()

                    if not linha or any(f.lower() in linha.lower() for f in frases_excluir):
                        i += 1
                        continue

                    for frase in frases_interesse:
                        if frase.lower() in linha.lower():
                            pergunta = frase
                            resto = linha.replace(frase, '').strip().lstrip(':').strip()

                            if not resto:
                                # Pega próxima linha
                                j = i + 1
                                while j < len(linhas):
                                    proxima = linhas[j].strip()
                                    if proxima:
                                        resto = proxima
                                        break
                                    j += 1
                                i = j - 1

                            coletado.append({
                                'arquivo': nome_arquivo,
                                'pagina': pagina_num + 1,
                                'pergunta': pergunta,
                                'resposta': resto
                            })
                            break
                    i += 1

    print(f"Arquivos lidos: {arquivo_n}")

    if coletado:
        df = pd.DataFrame(coletado)
        df['ticket'] = df['arquivo'].str.extract(r'_(\d+)\.')
        df.to_excel(os.path.join(STEP2, "dados_extraidos.xlsx"), index=False)
        print("Extração concluída. Dados salvos em 'dados_extraidos.xlsx'")
    else:
        print("Nenhum dado coletado.")

def juntando_planilhas_info():
    df = pd.read_excel(os.path.join(STEP2, 'dados_extraidos.xlsx'))
    info = pd.read_excel(os.path.join(STEP2, 'info_complementares.xlsx'))
    neg = pd.read_excel(os.path.join(STEP1, 'srinfo_partnership_fundsapproval.xlsx'))
    neg = neg[['fundsapp_ticket_monitoring', 'negotiation_code']]

    info2 = neg.merge(info, left_on='fundsapp_ticket_monitoring', right_on='ticket', how='right')

    renomear_chaves = {
        "AMPLIAR A GAMA DE BENS OU SERVIÇOS OFERTADOS": 'Ampliar a gama de bens ou serviços ofertados',
        "AMPLIAR A PARTICIPAÇÃO DA EMPRESA NO MERCADO": 'Ampliar a participação da empresa no mercado',
        "AUMENTAR A CAPACIDADE DE PRODUÇÃO OU DE PRESTAÇÃO DE SERVIÇOS": 'Aumentar a capacidade de produção ou de prestação de serviços',
        "AUMENTAR A CAPACIDADE DE PRODUÇÃO OU DE PRESTAÇÃO DE": 'Aumentar a capacidade de produção ou de prestação de serviços',
        "AUMENTAR A FLEXIBILIDADE DA PRODUÇÃO OU DA PRESTAÇÃO DE SERVIÇOS": 'Aumentar a flexibilidade da produção ou da prestação de serviços',
        "ENQUADRAR EM REGULAÇÕES E NORMAS-PADRÃO RELATIVAS AO MERCADO INTERNO OU EXTERNO": 'Enquadrar em regulações e normas-padrão relativas ao mercado interno ou externo',
        "MERCADO INTERNO OU EXTERNO": 'Enquadrar em regulações e normas-padrão relativas ao mercado interno ou externo',
        "MELHORAR A QUALIDADE DOS BENS OU SERVIÇOS": 'Melhorar a qualidade dos bens ou serviços',
        "PERMITIR ABRERTURA DE NOVOS MERCADOS": 'Permitir abertura de novos mercados',
        "PERMITIR ABERTURA DE NOVOS MERCADOS": 'Permitir abertura de novos mercados',
        "PERMITIR CONTROLAR ASPECTOS LIGADOS À SAÚDE E/OU À SEGURANÇA": 'Permitir controlar aspectos ligados à saúde e/ou à segurança',
        "SEGURANÇA": 'Permitir controlar aspectos ligados à saúde e/ou à segurança',
        "PERMITIR MANTER A PARTICIPAÇÃO DA EMPRESA NO MERCADO": 'Permitir manter a participação da empresa no mercado',
        "PERMITIR REDUZIR O IMPACTO SOBRE O MEIO AMBIENTE": 'Permitir reduzir o impacto sobre o meio ambiente',
        "REDUZIR O CONSUMO DE ÁGUA": 'Reduzir o consumo de água',
        "REDUZIR O CONSUMO DE ENERGIA": 'Reduzir o consumo de energia',
        "REDUZIR O CONSUMO DE MATÉRIAS-PRIMAS": 'Reduzir o consumo de matérias-primas',
        "REDUZIR OS CUSTOS DE PRODUÇÃO OU DOS SERVIÇOS PRESTADOS": 'Reduzir os custos de produção ou dos serviços prestados',
        "REDUZIR OS CUSTOS DO TRABALHO": 'Reduzir os custos do trabalho',
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU PERIGOSAS": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "MENOS CONTAMINANTES OU PERIGOSAS": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "CONTAMINANTES OU PERIGOSAS": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "PERIGOSAS": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS CONTAMINANTES OU ": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "SUBSTITUIR (TOTAL OU PARCIAL) MATÉRIAS-PRIMAS POR OUTRAS MENOS": 'Substituir (total ou parcial) matérias-primas por outras menos contaminantes ou perigosas',
        "SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA RENOVÁVEIS": 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        "SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA": 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        "SUBSTITUIR (TOTAL OU PARCIAL) ENERGIA PROVENIENTE DE COMBUSTÍVEIS FÓSSEIS POR FONTES DE": 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        "ENERGIA RENOVÁVEIS": 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        "RENOVÁVEIS": 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        "COMBUSTÍVEIS FÓSSEIS POR FONTES DE ENERGIA RENOVÁVEIS": 'Substituir (total ou parcial) energia proveniente de combustíveis fósseis por fontes de energia renováveis',
        "REDUZIR RUÍDOS OU A CONTAMINAÇÃO DO SOLO, DA ÁGUA OU DO AR": 'Reduzir ruídos ou a contaminação do solo, da água ou do ar',
        "RECICLAGEM DE RESÍDUOS, ÁGUAS RESIDUAIS OU MATERIAIS PARA VENDA E/OU REUTILIZAÇÃO": 'Reciclagem de resíduos, águas residuais ou materiais para venda e/ou reutilização',
        "VENDA E/OU REUTILIZAÇÃO": 'Reciclagem de resíduos, águas residuais ou materiais para venda e/ou reutilização',
        "REDUÇÃO DA 'PEGADA' DE CO (PRODUÇÃO TOTAL DE CO) DE SUA EMPRESA": 'Redução da pegada de CO (produção total de CO) de sua empresa',
        "EMPRESA:": 'Redução da pegada de CO (produção total de CO) de sua empresa'
    }

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

    # Aplicando as renomeações nas chaves
    df['pergunta'] = df['pergunta'].replace(renomear_chaves)

    # Filtrar o DataFrame
    df_filtrado = df[df['pergunta'].isin(chaves_desejadas)]

    # Salvando na pasta de saída
    df_filtrado.to_excel(os.path.join(STEP2, "info_complementares_pdfs.xlsx"), index=False)

    # Juntando os dois
    df_final2 = neg.merge(df_filtrado, left_on='fundsapp_ticket_monitoring', right_on='ticket', how='right')
    df_final2 = df_final2[['arquivo', 'ticket', 'negotiation_code', 'pergunta', 'resposta']]
    info_final = pd.concat([info2, df_final2], ignore_index=True)
    info_final = info_final.drop_duplicates()
    info_final.to_excel(os.path.join(STEP2, 'info_complementares_novo.xlsx'), index=False)

def juntando_planilhas_geral():

    df = pd.read_excel(os.path.join(STEP2, 'dados_extraidos.xlsx'))
    geral = pd.read_excel(os.path.join(STEP2, 'info_gerais.xlsx'))

    renomear_chaves = {
        "UNIDADE EMBRAPII": 'unidade_embrapii',
        "CÓDIGO DE NEGOCIAÇÃO": 'codigo_negociacao',
        "MODALIDADE DE FINANCIAMENTO DO PROJETO": 'modalidade_financiamento',
        "FOCO DO CONTRATO BNDES/EMBRAPII DA SOLICITAÇÃO DE RESERVA": 'foco',
        "FONTE DE RECURSO SECUNDÁRIA": 'fonte_secundaria',
        "EMPRESA:": '',
        "RAZÃO SOCIAL DA 1ª EMPRESA": 'empresa',
        "RAZÃO SOCIAL DA 1º EMPRESA": 'empresa',
        "RAZÃO SOCIAL DA 2ª EMPRESA": 'empresa',
        "RAZÃO SOCIAL DA 3ª EMPRESA": 'empresa',
        "RAZÃO SOCIAL DA 4ª EMPRESA": 'empresa',
        "NOME FANTASIA": 'nome_fantasia',
        "CNPJ": 'cnpj',
        "UF DO CNPJ": 'uf',
        "NÚMERO DE FUNCIONÁRIOS NO ÚLTIMO ANO": 'num_funcionarios',
        "FAIXA DE ROB NO ÚLTIMO ANO": 'rob',
        "CNAE (GRUPO 3 DÍGITOS) DA EMPRESA": 'cnae',
        "VALOR TOTAL": 'valor_total',
        "VALOR APORTADO PELA EMBRAPII": 'valor_embrapii',
        "VALOR APORTADO PELA EMBRAPII/BNDES": 'valor_embrapii_bndes',
        "% VALOR APORTADO EMBRAPII": 'pct_aporte_embrapii',
        "% VALOR APORTADO EMBRAPII/BNDES": 'pct_aporte_embrapii_bndes',
        "VALOR APORTADO PELA(S) EMPRESA(S)": 'valor_empresa',
        "% VALOR APORTADO PELA(S) EMPRESA(S)": 'pct_aporte_empresa',
        "VALOR APORTADO PELO SEBRAE": 'valor_sebrae',
        "% VALOR APORTADO PEL0 SEBRAE": 'pct_aporte_sebrae',
        "% VALOR APORTADO PELO SEBRAE": 'pct_aporte_sebrae',
        "VALOR APORTADO PELA UNIDADE EMBRAPII": 'valor_unidade_embrapii',
        "% VALOR APORTADO PELA UNIDADE EMBRAPII": 'pct_aporte_unidade',
        "NOME DO PROJETO": 'projeto',
        "OBJETIVO DO PROJETO": 'objetivo',
        "TIPO DE IMPACTO PRODUTIVO ESPERADO COM O PROJETO": 'impacto_produtivo',
        "1ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I": 'areas_aplicacao',
        "2ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I": 'areas_aplicacao',
        "3ª ÁREA DE APLICAÇÃO ASSOCIADA AO PROJETO P,D&I": 'areas_aplicacao',
        "1ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I": 'tecnologias_habilitadoras',
        "2ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I": 'tecnologias_habilitadoras',
        "3ª TECNOLOGIA HABILITADORA ASSOCIADA AO PROJETO P,D&I": 'tecnologias_habilitadoras',
        "CASO TENHA ESCOLHIDO \"OUTROS\", PREENCHA AO LADO": 'outros',
        "Nº DE MACROENTREGAS PLANEJADAS": 'num_macroentregas',
        "ESCALA TRL DA 1ª MACROENTREGA DO PROJETO (NO INÍCIO DA SUA EXECUÇÃO)": 'trl_inicial',
        "ESCALA TRL DA 1ª MACROENTREGA DO PROJETO (NO INÍCIO DA SUA": 'trl_inicial',
        "EXECUÇÃO)": 'trl_inicial',
        "ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO DO PROJETO)": 'trl_final',
        "ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO DO": 'trl_final',
        "ESCALA TRL DA ÚLTIMA MACROENTREGA (ESPERADO NA CONCLUSÃO": 'trl_final',
        "RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO (DESCRITIVO - MÁX DE 500 CARACTERES)": 'resultados_esperados',
        "RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO (DESCRITIVO -": 'resultados_esperados',
        "RESULTADOS ESPERADOS COM A CONCLUSÃO DO PROJETO": 'resultados_esperados',
        "(DESCRITIVO - MÁX DE 500 CARACTERES)": 'resultados_esperados',
        "MÁX DE 500 CARACTERES)": 'resultados_esperados',
        "A CONCLUSÃO DO PROJETO)": 'tempo_chegada_mercado',
        "CONCLUSÃO DO PROJETO)": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃ": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃO": 'tempo_chegada_mercado',
        "EXPECTATIVA DE TEMPO ESPERADO PARA QUE A TECNOLOGIA CHEGUE AO MERCADO (EM Nº DE MESES APÓS A CONCLUSÃO DO PROJETO)": 'tempo_chegada_mercado',
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO,": 'impacto_tecnologia',
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO": 'impacto_tecnologia',
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU": 'impacto_tecnologia',
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE": 'impacto_tecnologia',
        "EXPECTATIVA DE IMPACTO ESPERADO DA(S) TECNOLOGIA(S) QUE SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU ALTO/DISRUPTIVO": 'impacto_tecnologia',
        "SERÁ(ÃO) DESENVOLVIDAS(S) - BAIXO, MÉDIO OU ALTO/DISRUPTIVO": 'impacto_tecnologia',
        "MÉDIO OU ALTO/DISRUPTIVO": 'impacto_tecnologia',
        "OU ALTO/DISRUPTIVO": 'impacto_tecnologia',
        "ALTO/DISRUPTIVO:": 'impacto_tecnologia',
        "QUAL É A EXPECTATIVA DE SIGNIFICÂNCIA DA(S) INOVAÇÃO(ÕES) QUE": 'significancia_inovacao',
        "QUAL É A EXPECTATIVA DE SIGNIFICÂNCIA DA(S) INOVAÇÃO(ÕES) QUE SERÁ(ÃO) GERADA(S) NO PROJETO?": 'significancia_inovacao',
        "O PROJETO IRÁ USAR RECURSOS DOS CONTRATOS SEBRAE": 'recursos_sebrae',
        "MODALIDADE DE APORTE DO PROJETO": 'modalidade_aporte',
    }

    # Aplicando as renomeações nas chaves
    df['pergunta'] = df['pergunta'].replace(renomear_chaves)

    # Filtrar o DataFrame
    df_filtrado = df[~df['resposta'].isin(['Alta', 'Média', 'Baixa', 'Não relevante'])]

    # Agrupando por Arquivo + Chave e juntando os valores com "; " se for o caso
    df_agrupado = df_filtrado.groupby(['arquivo', 'ticket', 'pergunta'])['resposta'].apply(lambda x: '; '.join(x.astype(str))).reset_index()

    # Pivotando
    df_pivot = df_agrupado.pivot(index=['arquivo', 'ticket'], columns='pergunta', values='resposta').reset_index()

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
        if df_pivot['trl_inicial'] in df_pivot.columns:
            df_pivot.loc[df_pivot['trl_inicial'].astype(str).str.contains(str(i+3), na=False), 'trl_inicial'] = trl[i]
        if df_pivot['trl_final'] in df_pivot.columns:
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

    for col in valores:
        if col in df_pivot.columns:
            df_pivot[col] = df_pivot[col].astype(str).apply(lambda x: x.replace('.', '') if 'R$ ' in x else x)
            df_pivot[col] = df_pivot[col].str.replace('R$', '', case=False)
            df_pivot[col] = df_pivot[col].str.replace(' ', '', case=False)
            df_pivot[col] = df_pivot[col].str.replace('-', '', case=False)
            df_pivot[col] = df_pivot[col].str.replace('%', '', case=False)
            df_pivot[col] = df_pivot[col].str.replace(',', '.', case=False)
            df_pivot[col] = pd.to_numeric(df_pivot[col], errors='coerce')

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

    # Mantém apenas colunas que existem no DataFrame
    colunas_existentes = [col for col in colunas_informacoes if col in df_pivot.columns]

    df_pivot = df_pivot[colunas_existentes]

    colunas_para_usar = df_pivot.columns.difference(['arquivo'])
    df_pivot = df_pivot.drop_duplicates(subset=colunas_para_usar)

    df_concat = pd.concat([df_pivot, geral], ignore_index=True)

    df_concat.to_excel(os.path.join(STEP2, 'info_gerais_novo.xlsx'), index=False)
    print(f'Arquivos salvos com sucesso na pasta {STEP2}')

def gerando_planilhas_final():
    
    ## INFORMAÇÕES GERAIS
    info_gerais_anterior = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'info_gerais.xlsx')))
    info_gerais_novo = pd.read_excel(os.path.abspath(os.path.join(STEP2, 'info_gerais_novo.xlsx')))

    ger_concat = pd.concat([info_gerais_anterior, info_gerais_novo], ignore_index=True).drop_duplicates()
    ger_concat.to_excel(os.path.join(STEP3, 'info_gerais.xlsx'), index=False)

    ### INFORMAÇÕES COMPLEMENTARES
    info_comp_anterior = pd.read_excel(os.path.abspath(os.path.join(STEP1, 'info_complementares.xlsx')))
    info_comp_novo = pd.read_excel(os.path.abspath(os.path.join(STEP2, 'info_complementares_novo.xlsx')))

    comp_concat = pd.concat([info_comp_anterior, info_comp_novo], ignore_index=True).drop_duplicates()
    comp_concat.to_excel(os.path.join(STEP3, 'info_complementares.xlsx'), index=False)

