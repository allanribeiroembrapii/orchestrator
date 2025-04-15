from dotenv import load_dotenv
import os
from scripts.apagar_arquivos_pasta import apagar_arquivos_pasta
from scripts.mover_arquivos import mover_arquivos_excel, mover_arquivo_especifico
from scripts.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from scripts.levar_arquivos_sharepoint import levar_arquivos_sharepoint
from atrasos.mensagem_chat_teams import mensagem_teams_atrasos, enviar_mensagem_teams_atrasos
from mover.mensagem_chat_teams import mensagem_teams_mover, enviar_mensagem_teams_mover
from scripts.registro_alertas import registrar_envio
import inspect
from datetime import datetime

# Carregar as variáveis de ambiente
load_dotenv()
ROOT = os.getenv('ROOT')
PLANILHAS_ATRASOS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'planilhas'))
ANTERIOR_ATRASOS = os.path.abspath(os.path.join(ROOT, 'atrasos', 'anterior'))
PLANILHAS = os.path.abspath(os.path.join(ROOT, 'copy_sharepoint_atual'))
ANTERIOR = os.path.abspath(os.path.join(ROOT, 'copy_sharepoint_anterior'))
UP = os.path.abspath(os.path.join(ROOT, 'up'))

def main():
    """
    Função geral para atualizar as planilhas de referência, obter os dados e enviar mensagem no Teams.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        hoje = datetime.today().weekday()

        ## MOVENDO ARQUIVOS E BUSCANDO NOVOS ARQUIVOS NO SHAREPOINT ##
        # Apagar arquivos da pasta "copy_sharepoint_anterior"
        apagar_arquivos_pasta(ANTERIOR)

        # Mover arquivos de "copy_sharepoint_atual" para "copy_sharepoint_anterior"
        mover_arquivos_excel(1, PLANILHAS, ANTERIOR)

        # Buscar arquivos no Sharepoint
        buscar_arquivos_sharepoint()


        ## MOVER - PROJETOS NOVOS COM MAIS DE R$5 MILHÕES ##
        mensagem_mover = mensagem_teams_mover()

        if mensagem_mover:
            enviar_mensagem_teams_mover(mensagem_mover)
            registrar_envio(2, mensagem_mover)

        
        ## TODA SEGUNDA - MANDAR ALERTA DE ATRASOS ##
        if hoje == 0:
            # Apagar arquivos da pasta "anterior"
            apagar_arquivos_pasta(ANTERIOR_ATRASOS)

            # Mover arquivos de "planilhas" para "anterior"
            mover_arquivos_excel(2, PLANILHAS_ATRASOS, ANTERIOR_ATRASOS)

            # Mover arquivos de "copy_sharepoint_atual" para "planilhas"
            mover_arquivos_excel(3, PLANILHAS, PLANILHAS_ATRASOS)
        
            # Mensagem
            mensagem_atrasos = mensagem_teams_atrasos()
        
            enviar_mensagem_teams_atrasos(mensagem_atrasos)
            registrar_envio(1, mensagem_atrasos)


        ## REGISTRO DE ALERTAS ##
        # Apagar arquivos da pasta "up"
        apagar_arquivos_pasta(UP)

        # Movendo o arquivo 'registro_alertas.xlsx' para a pasta 'up'
        mover_arquivo_especifico('registro_alertas.xlsx', PLANILHAS, UP)

        # Levando o arquivo 'registro_alertas.xlsx' para o Sharepoint
        levar_arquivos_sharepoint()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")

if __name__ == '__main__':
    main()