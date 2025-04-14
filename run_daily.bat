@echo on
echo ========================================
echo EMBRAPII ORCHESTRATOR - EXECUCAO MANUAL
echo Data e hora: %date% %time%
echo ========================================

set ROOT=%~dp0
set ROOT_PIPELINE=%ROOT%core\pipeline_embrapii_srinfo
set ROOT_GSHET=%ROOT%core\atualizar_google_sheets
set ROOT_DATAPII=%ROOT%core\api_datapii
set LOG_FILE=%ROOT%logs\exec_%date:~-4%%date:~3,2%%date:~0,2%.log

REM Configurar PYTHONPATH para incluir diretório raiz e logs
set PYTHONPATH=%ROOT%;%ROOT%logs

REM Verifica e cria pasta de logs se não existir
if not exist "%ROOT%logs" mkdir "%ROOT%logs"

echo Iniciando execucao em %date% %time% > %LOG_FILE%
echo Diretorio raiz: %ROOT% >> %LOG_FILE%
echo Diretorio pipeline: %ROOT_PIPELINE% >> %LOG_FILE%
echo Diretorio google sheets: %ROOT_GSHET% >> %LOG_FILE%
echo Diretorio datapii: %ROOT_DATAPII% >> %LOG_FILE%
echo PYTHONPATH: %PYTHONPATH% >> %LOG_FILE%

REM Inicializar o logger JSON
echo Inicializando logger JSON...
python "%ROOT%logs\init_logger.py" "%ROOT%"
if %errorlevel% neq 0 (
    echo ERRO: Falha ao inicializar o logger JSON
    echo ERRO: Falha ao inicializar o logger JSON >> %LOG_FILE%
    goto :erro
)
echo Logger JSON inicializado com sucesso >> %LOG_FILE%

REM Verificar se os diretórios existem antes de tentar acessá-los
echo Verificando diretórios...
echo Verificando diretórios... >> %LOG_FILE%
if not exist "%ROOT%core\pipeline_embrapii_srinfo" (
    echo ERRO: Diretório %ROOT%core\pipeline_embrapii_srinfo não encontrado
    echo Caminho atual: %CD%
    echo ERRO: Diretório %ROOT%core\pipeline_embrapii_srinfo não encontrado >> %LOG_FILE%
    echo Caminho atual: %CD% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "verificar_diretorios" "Diretório pipeline_embrapii_srinfo não encontrado"
    goto :erro
)
echo Diretório pipeline_embrapii_srinfo encontrado >> %LOG_FILE%

if not exist "%ROOT%core\atualizar_google_sheets" (
    echo ERRO: Diretório %ROOT%core\atualizar_google_sheets não encontrado
    echo Caminho atual: %CD%
    echo ERRO: Diretório %ROOT%core\atualizar_google_sheets não encontrado >> %LOG_FILE%
    echo Caminho atual: %CD% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "verificar_diretorios" "Diretório atualizar_google_sheets não encontrado"
    goto :erro
)
echo Diretório atualizar_google_sheets encontrado >> %LOG_FILE%

if not exist "%ROOT%core\api_datapii" (
    echo ERRO: Diretório %ROOT%core\api_datapii não encontrado
    echo Caminho atual: %CD%
    echo ERRO: Diretório %ROOT%core\api_datapii não encontrado >> %LOG_FILE%
    echo Caminho atual: %CD% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "verificar_diretorios" "Diretório api_datapii não encontrado"
    goto :erro
)
echo Diretório api_datapii encontrado >> %LOG_FILE%

REM Executa os scripts em sequência
echo 1. Executando pipeline_embrapii_srinfo...
echo 1. Executando pipeline_embrapii_srinfo... >> %LOG_FILE%

cd /d "%ROOT%core\pipeline_embrapii_srinfo"
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível acessar o diretório pipeline_embrapii_srinfo
    echo ERRO: Não foi possível acessar o diretório pipeline_embrapii_srinfo >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "acessar_diretorio_pipeline" "Não foi possível acessar o diretório pipeline_embrapii_srinfo"
    goto :erro
)

echo Diretório atual: %CD%
echo Diretório atual: %CD% >> %LOG_FILE%
if not exist "main.py" (
    echo ERRO: main.py não encontrado em %CD%
    echo ERRO: main.py não encontrado em %CD% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "verificar_arquivo_pipeline" "main.py não encontrado"
    goto :erro
)

echo Executando pipeline_embrapii_srinfo/main.py...
echo Executando pipeline_embrapii_srinfo/main.py... >> %LOG_FILE%
python main.py
if %errorlevel% neq 0 (
    echo ERRO: pipeline_embrapii_srinfo falhou com código %errorlevel%
    echo ERRO: pipeline_embrapii_srinfo falhou com código %errorlevel% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "executar_pipeline" "pipeline_embrapii_srinfo falhou com código %errorlevel%"
    goto :erro
)

echo pipeline_embrapii_srinfo executado com sucesso
echo pipeline_embrapii_srinfo executado com sucesso >> %LOG_FILE%

REM Retornar ao diretório raiz
cd /d "%ROOT%"
echo Retornando ao diretório raiz: %CD%
echo Retornando ao diretório raiz: %CD% >> %LOG_FILE%

REM Executar atualizar_google_sheets
echo 2. Executando atualizar_google_sheets...
echo 2. Executando atualizar_google_sheets... >> %LOG_FILE%

REM Reinicializar o logger para o próximo módulo
echo Reinicializando o logger para o próximo módulo...
echo Reinicializando o logger para o próximo módulo... >> %LOG_FILE%
python "%ROOT%logs\init_logger.py" "%ROOT%"
if %errorlevel% neq 0 (
    echo AVISO: Falha ao reinicializar o logger JSON, continuando mesmo assim...
    echo AVISO: Falha ao reinicializar o logger JSON, continuando mesmo assim... >> %LOG_FILE%
)

cd /d "%ROOT%core\atualizar_google_sheets"
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível acessar o diretório atualizar_google_sheets
    echo ERRO: Não foi possível acessar o diretório atualizar_google_sheets >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "acessar_diretorio_gsheets" "Não foi possível acessar o diretório atualizar_google_sheets"
    goto :erro
)

echo Diretório atual: %CD%
echo Diretório atual: %CD% >> %LOG_FILE%
if not exist "main.py" (
    echo ERRO: main.py não encontrado em %CD%
    echo ERRO: main.py não encontrado em %CD% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "verificar_arquivo_gsheets" "main.py não encontrado"
    goto :erro
)

echo Executando atualizar_google_sheets/main.py...
echo Executando atualizar_google_sheets/main.py... >> %LOG_FILE%
REM Copiar o arquivo api_google_sheets.json para o diretório atual se necessário
if exist "%ROOT%api_google_sheets.json" (
    echo Arquivo api_google_sheets.json encontrado na raiz do projeto
    echo Arquivo api_google_sheets.json encontrado na raiz do projeto >> %LOG_FILE%
) else (
    echo AVISO: Arquivo api_google_sheets.json não encontrado na raiz do projeto
    echo AVISO: Arquivo api_google_sheets.json não encontrado na raiz do projeto >> %LOG_FILE%
)
python main.py
if %errorlevel% neq 0 (
    echo ERRO: atualizar_google_sheets falhou com código %errorlevel%
    echo ERRO: atualizar_google_sheets falhou com código %errorlevel% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "executar_gsheets" "atualizar_google_sheets falhou com código %errorlevel%"
    goto :erro
)

echo atualizar_google_sheets executado com sucesso
echo atualizar_google_sheets executado com sucesso >> %LOG_FILE%

REM Retornar ao diretório raiz
cd /d "%ROOT%"
echo Retornando ao diretório raiz: %CD%
echo Retornando ao diretório raiz: %CD% >> %LOG_FILE%

REM Executar api_datapii
echo 3. Executando api_datapii...
echo 3. Executando api_datapii... >> %LOG_FILE%

REM Reinicializar o logger para o próximo módulo
echo Reinicializando o logger para o próximo módulo...
echo Reinicializando o logger para o próximo módulo... >> %LOG_FILE%
python "%ROOT%logs\init_logger.py" "%ROOT%"
if %errorlevel% neq 0 (
    echo AVISO: Falha ao reinicializar o logger JSON, continuando mesmo assim...
    echo AVISO: Falha ao reinicializar o logger JSON, continuando mesmo assim... >> %LOG_FILE%
)

cd /d "%ROOT%core\api_datapii"
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível acessar o diretório api_datapii
    echo ERRO: Não foi possível acessar o diretório api_datapii >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "acessar_diretorio_api" "Não foi possível acessar o diretório api_datapii"
    goto :erro
)

echo Diretório atual: %CD%
echo Diretório atual: %CD% >> %LOG_FILE%
if not exist "main.py" (
    echo ERRO: main.py não encontrado em %CD%
    echo ERRO: main.py não encontrado em %CD% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "verificar_arquivo_api" "main.py não encontrado"
    goto :erro
)

echo Executando api_datapii/main.py...
echo Executando api_datapii/main.py... >> %LOG_FILE%
python main.py
if %errorlevel% neq 0 (
    echo ERRO: api_datapii falhou com código %errorlevel%
    echo ERRO: api_datapii falhou com código %errorlevel% >> %LOG_FILE%
    python "%ROOT%logs\log_error.py" "%ROOT%" "executar_api" "api_datapii falhou com código %errorlevel%"
    goto :erro
)

echo api_datapii executado com sucesso
echo api_datapii executado com sucesso >> %LOG_FILE%

REM Retornar ao diretório raiz
cd /d "%ROOT%"
echo Retornando ao diretório raiz: %CD%
echo Retornando ao diretório raiz: %CD% >> %LOG_FILE%

echo Todos os scripts executados com sucesso!
echo Todos os scripts executados com sucesso! >> %LOG_FILE%
python "%ROOT%logs\log_success.py" "%ROOT%"
goto :fim

:erro
echo ========================================
echo ERRO NA EXECUCAO
echo Verifique os logs para mais detalhes
echo ========================================
echo ERRO NA EXECUCAO >> %LOG_FILE%
echo Verifique os logs para mais detalhes >> %LOG_FILE%
echo Data e hora do erro: %date% %time% >> %LOG_FILE%
echo Diretório atual no momento do erro: %CD% >> %LOG_FILE%

REM Enviar notificação via webhook
echo Enviando notificação de erro via webhook...
cd /d "%ROOT%"
echo Diretório atual para envio de notificação: %CD%
set PYTHONPATH=%ROOT%;%ROOT%logs
python "%ROOT%logs\send_webhook_notification.py" "%ROOT%" "https://prod-19.brazilsouth.logic.azure.com:443/workflows/7020ca7ed0b64e9bbd57761e96165beb/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%%2Ftriggers%%2Fmanual%%2Frun&sv=1.0&sig=RMG1cStKRn7822ipPN_PvaNRTxLk2fmAp2mZCglkupc"
if %errorlevel% neq 0 (
    echo AVISO: Falha ao enviar notificação via webhook
    echo AVISO: Falha ao enviar notificação via webhook >> %LOG_FILE%
    echo Tentando enviar notificação simplificada...
    python -c "import requests; requests.post('https://prod-19.brazilsouth.logic.azure.com:443/workflows/7020ca7ed0b64e9bbd57761e96165beb/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%%2Ftriggers%%2Fmanual%%2Frun&sv=1.0&sig=RMG1cStKRn7822ipPN_PvaNRTxLk2fmAp2mZCglkupc', json={'text': '❌ **ERRO NA EXECUÇÃO** - %date% %time%\n\nVerifique os logs para mais detalhes.'}, headers={'Content-Type': 'application/json'})"
)

echo Pressione qualquer tecla para sair...
pause > nul
exit /b 1

:fim
echo ========================================
echo EXECUCAO CONCLUIDA COM SUCESSO
echo Data e hora: %date% %time%
echo ========================================
echo EXECUCAO CONCLUIDA COM SUCESSO >> %LOG_FILE%
echo Data e hora: %date% %time% >> %LOG_FILE%

REM Enviar notificação via webhook
echo Enviando notificação de sucesso via webhook...
cd /d "%ROOT%"
echo Diretório atual para envio de notificação: %CD%
set PYTHONPATH=%ROOT%;%ROOT%logs
python "%ROOT%logs\send_webhook_notification.py" "%ROOT%" "https://prod-19.brazilsouth.logic.azure.com:443/workflows/7020ca7ed0b64e9bbd57761e96165beb/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%%2Ftriggers%%2Fmanual%%2Frun&sv=1.0&sig=RMG1cStKRn7822ipPN_PvaNRTxLk2fmAp2mZCglkupc"
if %errorlevel% neq 0 (
    echo AVISO: Falha ao enviar notificação via webhook
    echo AVISO: Falha ao enviar notificação via webhook >> %LOG_FILE%
    echo Tentando enviar notificação simplificada...
    python -c "import requests; requests.post('https://prod-19.brazilsouth.logic.azure.com:443/workflows/7020ca7ed0b64e9bbd57761e96165beb/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%%2Ftriggers%%2Fmanual%%2Frun&sv=1.0&sig=RMG1cStKRn7822ipPN_PvaNRTxLk2fmAp2mZCglkupc', json={'text': '✅ **EXECUÇÃO CONCLUÍDA COM SUCESSO** - %date% %time%'}, headers={'Content-Type': 'application/json'})"
)

echo Pressione qualquer tecla para sair...
pause > nul
exit /b 0
