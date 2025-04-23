@echo off
rem Define codificação UTF-8 para o console
chcp 65001 > nul

title Orquestrador Embrapii - Centralizado
echo ========================================
echo EMBRAPII ORCHESTRATOR - CENTRALIZADO
echo Data e hora: %date% %time%
echo ========================================
echo.

rem Definir caminho raiz do projeto
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
echo Diretório raiz: %ROOT%
echo.

rem Verificar se o arquivo principal existe
if not exist "%ROOT%\main.py" (
    echo ERRO: main.py não encontrado na raiz do projeto.
    goto fim
)

echo Verificando instalação do Python...
where python 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado no PATH do sistema.
    goto fim
)

echo Python encontrado:
python --version
echo.

rem Ativar ambiente virtual se existir
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call "%ROOT%\venv\Scripts\activate.bat"
    echo Ambiente virtual ativado
)

rem Definir variáveis para acompanhar status
set PIPELINE_SUCCESS=0
set GSHEETS_SUCCESS=0
set DATAPII_SUCCESS=0
set ANY_SUCCESS=0

rem 1. Executar pipeline_embrapii_srinfo
echo.
echo Executando pipeline_embrapii_srinfo...
cd /d "%ROOT%\core\pipeline_embrapii_srinfo"
python main.py
if %errorlevel% equ 0 (
    echo pipeline_embrapii_srinfo executado com sucesso.
    set PIPELINE_SUCCESS=1
    set ANY_SUCCESS=1
) else (
    echo AVISO: pipeline_embrapii_srinfo completou com erros não críticos.
    echo Continuando com a execução...
)

rem 2. Executar atualizar_google_sheets
echo.
echo Executando atualizar_google_sheets...
cd /d "%ROOT%\core\atualizar_google_sheets"
python main.py
if %errorlevel% equ 0 (
    echo atualizar_google_sheets executado com sucesso.
    set GSHEETS_SUCCESS=1
    set ANY_SUCCESS=1
) else (
    echo AVISO: atualizar_google_sheets completou com erros não críticos.
    echo Continuando com a execução...
)

rem 3. Executar api_datapii
echo.
echo Executando api_datapii...
cd /d "%ROOT%\core\api_datapii"
python main.py
if %errorlevel% equ 0 (
    echo api_datapii executado com sucesso.
    set DATAPII_SUCCESS=1
    set ANY_SUCCESS=1
) else (
    echo AVISO: api_datapii completou com erros não críticos.
    echo Continuando com a execução...
)

rem Desativar ambiente virtual se foi ativado
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call deactivate
    echo Ambiente virtual desativado
)

rem Verificar status geral
if %ANY_SUCCESS% equ 0 (
    echo.
    echo ========================================
    echo ERRO CRÍTICO: Nenhum módulo foi executado com sucesso.
    echo ========================================
    goto fim
)

rem Enviar notificação com status
if %PIPELINE_SUCCESS% equ 1 if %GSHEETS_SUCCESS% equ 1 if %DATAPII_SUCCESS% equ 1 (
    python "%ROOT%\logs\send_teams_notification_fixed.py" --start "%date% %time%" --end "%date% %time%" --duration "00:30:00"
) else (
    python "%ROOT%\logs\send_teams_notification_fixed.py" --error --error-msg "Alguns módulos não foram executados com sucesso" --start "%date% %time%" --end "%date% %time%" --duration "00:30:00"
)

echo.
echo ========================================
echo EXECUCAO CONCLUIDA
if %PIPELINE_SUCCESS% equ 1 if %GSHEETS_SUCCESS% equ 1 if %DATAPII_SUCCESS% equ 1 (
    echo Todos os módulos foram executados com sucesso.
) else (
    echo Execução concluída com alguns avisos.
    echo pipeline_embrapii_srinfo: %PIPELINE_SUCCESS%
    echo atualizar_google_sheets: %GSHEETS_SUCCESS%
    echo api_datapii: %DATAPII_SUCCESS%
)
echo ========================================

:fim
echo.
echo Execução finalizada. 
echo Pressione qualquer tecla para sair...
pause > nul
