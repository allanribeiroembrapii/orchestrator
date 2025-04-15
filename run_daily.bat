@echo off
rem Define codificação UTF-8 para o console
chcp 65001 > nul

title Orquestrador Embrapii
echo ========================================
echo EMBRAPII ORCHESTRATOR - EXECUCAO MANUAL
echo Data e hora: %date% %time%
echo ========================================
echo.

rem Configuração de caminhos absolutos
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
set ROOT_PIPELINE=%ROOT%\core\pipeline_embrapii_srinfo
set ROOT_GSHET=%ROOT%\core\atualizar_google_sheets
set ROOT_DATAPII=%ROOT%\core\api_datapii
set LOG_DIR=%ROOT%\logs
set LOG_FILE=%LOG_DIR%\exec_%date:~6,4%%date:~3,2%%date:~0,2%.log

echo Diretórios configurados:
echo - Raiz: %ROOT%
echo - Pipeline: %ROOT_PIPELINE%
echo - Google Sheets: %ROOT_GSHET%
echo - API DataPII: %ROOT_DATAPII%
echo - Log: %LOG_FILE%
echo.

rem Verifica e cria pasta de logs se não existir
if not exist "%LOG_DIR%" (
    echo Criando diretório de logs...
    mkdir "%LOG_DIR%"
)

echo Iniciando execucao em %date% %time% > %LOG_FILE%
echo Diretorio raiz: %ROOT% >> %LOG_FILE%

rem Verificar os diretórios principais
echo Verificando diretórios...

if not exist "%ROOT_PIPELINE%" (
    echo ERRO: Diretório pipeline_embrapii_srinfo não encontrado
    echo ERRO: Diretório pipeline_embrapii_srinfo não encontrado >> %LOG_FILE%
    goto erro
)

if not exist "%ROOT_GSHET%" (
    echo ERRO: Diretório atualizar_google_sheets não encontrado
    echo ERRO: Diretório atualizar_google_sheets não encontrado >> %LOG_FILE%
    goto erro
)

if not exist "%ROOT_DATAPII%" (
    echo ERRO: Diretório api_datapii não encontrado
    echo ERRO: Diretório api_datapii não encontrado >> %LOG_FILE%
    goto erro
)

rem ==== 1. Executar pipeline_embrapii_srinfo ====
echo.
echo 1. Executando pipeline_embrapii_srinfo...
echo 1. Executando pipeline_embrapii_srinfo... >> %LOG_FILE%

cd /d "%ROOT_PIPELINE%"
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível acessar o diretório pipeline_embrapii_srinfo
    echo ERRO: Não foi possível acessar o diretório pipeline_embrapii_srinfo >> %LOG_FILE%
    goto erro
)

echo Diretório atual: %CD%
echo Diretório atual: %CD% >> %LOG_FILE%

if not exist "main.py" (
    echo ERRO: main.py não encontrado em %CD%
    echo ERRO: main.py não encontrado em %CD% >> %LOG_FILE%
    goto erro
)

echo Executando pipeline_embrapii_srinfo/main.py...
echo Executando pipeline_embrapii_srinfo/main.py... >> %LOG_FILE%

rem Ativar ambiente virtual se existir
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call "%ROOT%\venv\Scripts\activate.bat"
    echo Ambiente virtual ativado
    echo Ambiente virtual ativado >> %LOG_FILE%
)

python main.py
if %errorlevel% neq 0 (
    echo ERRO: pipeline_embrapii_srinfo falhou com código %errorlevel%
    echo ERRO: pipeline_embrapii_srinfo falhou com código %errorlevel% >> %LOG_FILE%
    goto erro
)

echo pipeline_embrapii_srinfo executado com sucesso
echo pipeline_embrapii_srinfo executado com sucesso >> %LOG_FILE%

rem ==== 2. Executar atualizar_google_sheets ====
echo.
echo 2. Executando atualizar_google_sheets...
echo 2. Executando atualizar_google_sheets... >> %LOG_FILE%

cd /d "%ROOT_GSHET%"
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível acessar o diretório atualizar_google_sheets
    echo ERRO: Não foi possível acessar o diretório atualizar_google_sheets >> %LOG_FILE%
    goto erro
)

echo Diretório atual: %CD%
echo Diretório atual: %CD% >> %LOG_FILE%

if not exist "main.py" (
    echo ERRO: main.py não encontrado em %CD%
    echo ERRO: main.py não encontrado em %CD% >> %LOG_FILE%
    goto erro
)

rem Verificar se o arquivo de credenciais está disponível
if exist "%ROOT%\api_google_sheets.json" (
    echo Arquivo api_google_sheets.json encontrado na raiz do projeto
    
    rem Copiar para o diretório atual se não existir
    if not exist "api_google_sheets.json" (
        copy "%ROOT%\api_google_sheets.json" .
        echo Arquivo api_google_sheets.json copiado para o diretório atual
    )
) else (
    echo AVISO: Arquivo api_google_sheets.json não encontrado na raiz do projeto
)

echo Executando atualizar_google_sheets/main.py...
echo Executando atualizar_google_sheets/main.py... >> %LOG_FILE%

python main.py
if %errorlevel% neq 0 (
    echo ERRO: atualizar_google_sheets falhou com código %errorlevel%
    echo ERRO: atualizar_google_sheets falhou com código %errorlevel% >> %LOG_FILE%
    goto erro
)

echo atualizar_google_sheets executado com sucesso
echo atualizar_google_sheets executado com sucesso >> %LOG_FILE%

rem ==== 3. Executar api_datapii ====
echo.
echo 3. Executando api_datapii...
echo 3. Executando api_datapii... >> %LOG_FILE%

cd /d "%ROOT_DATAPII%"
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível acessar o diretório api_datapii
    echo ERRO: Não foi possível acessar o diretório api_datapii >> %LOG_FILE%
    goto erro
)

echo Diretório atual: %CD%
echo Diretório atual: %CD% >> %LOG_FILE%

if not exist "main.py" (
    echo ERRO: main.py não encontrado em %CD%
    echo ERRO: main.py não encontrado em %CD% >> %LOG_FILE%
    goto erro
)

echo Executando api_datapii/main.py...
echo Executando api_datapii/main.py... >> %LOG_FILE%

python main.py
if %errorlevel% neq 0 (
    echo ERRO: api_datapii falhou com código %errorlevel%
    echo ERRO: api_datapii falhou com código %errorlevel% >> %LOG_FILE%
    goto erro
)

echo api_datapii executado com sucesso
echo api_datapii executado com sucesso >> %LOG_FILE%

rem Desativar ambiente virtual se foi ativado
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call deactivate
    echo Ambiente virtual desativado
    echo Ambiente virtual desativado >> %LOG_FILE%
)

rem ==== CONCLUSÃO BEM-SUCEDIDA ====
echo.
echo ========================================
echo EXECUCAO CONCLUIDA COM SUCESSO
echo Data e hora: %date% %time%
echo ========================================
echo EXECUCAO CONCLUIDA COM SUCESSO >> %LOG_FILE%
echo Data e hora: %date% %time% >> %LOG_FILE%

rem Enviar notificação via webhook
echo Enviando notificação via webhook...
(
echo ^{^"text^":^"✅ **EXECUÇÃO CONCLUÍDA COM SUCESSO** - %date% %time%\n\nTodos os módulos foram executados com sucesso:^"^}
) > %TEMP%\teams_message.json

curl -H "Content-Type: application/json" -d @"%TEMP%\teams_message.json" "https://prod-07.brazilsouth.logic.azure.com:443/workflows/ab16e58e66774488a997f828f1fe56e6/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=N4Q5CYnieqFvVwhc4gOfW31zfDa4kz9XCFSq35mCqlY"

if %errorlevel% equ 0 (
    echo Notificação enviada com sucesso.
) else (
    echo Falha ao enviar notificação.
)

del %TEMP%\teams_message.json 2>nul
goto fim

:erro
echo.
echo ========================================
echo ERRO NA EXECUCAO
echo Verifique os logs para mais detalhes
echo ========================================
echo ERRO NA EXECUCAO >> %LOG_FILE%
echo Data e hora do erro: %date% %time% >> %LOG_FILE%
echo Diretório atual no momento do erro: %CD% >> %LOG_FILE%

rem Desativar ambiente virtual se foi ativado
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call deactivate
    echo Ambiente virtual desativado
    echo Ambiente virtual desativado >> %LOG_FILE%
)

rem Enviar notificação de erro via webhook
echo Enviando notificação de erro via webhook...
(
echo ^{^"text^":^"❌ **ERRO NA EXECUÇÃO** - %date% %time%\n\nOcorreu um erro durante a execução do orquestrador.\nLocalização: %CD%^"^}
) > %TEMP%\teams_error.json

curl -H "Content-Type: application/json" -d @"%TEMP%\teams_error.json" "https://prod-19.brazilsouth.logic.azure.com:443/workflows/7020ca7ed0b64e9bbd57761e96165beb/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%%2Ftriggers%%2Fmanual%%2Frun&sv=1.0&sig=RMG1cStKRn7822ipPN_PvaNRTxLk2fmAp2mZCglkupc"

del %TEMP%\teams_error.json 2>nul

:fim
echo.
echo Execução finalizada.
echo Pressione qualquer tecla para sair...
pause > nul