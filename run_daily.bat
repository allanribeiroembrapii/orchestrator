@echo off
rem Define codificação UTF-8 para o console
chcp 65001 > nul

setlocal enabledelayedexpansion

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
echo - Alertas: %ROOT_DATAPII%
echo - Log: %LOG_FILE%
echo.

rem Salvar data e horário de início (separadamente)
set START_DATE=%date%
set START_TIME=%time%

rem Verifica e cria pasta de logs se não existir
if not exist "%LOG_DIR%" (
    echo Criando diretório de logs...
    mkdir "%LOG_DIR%"
)

echo Iniciando execucao em %START_DATE% %START_TIME% > %LOG_FILE%
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

rem Salvar data e horário de término (separadamente)
set END_DATE=%date%
set END_TIME=%time%

rem Obter informações sobre novos projetos e empresas da execução
cd /d "%ROOT%"
for /f "tokens=1,2,3" %%a in ('python -c "import sys; sys.path.append(r'%ROOT_PIPELINE%'); from scripts_public.comparar_excel import comparar_excel; result = comparar_excel(); print(result[0], result[1], result[2])"') do (
    set NOVOS_PROJETOS=%%a
    set NOVAS_EMPRESAS=%%b
    set PROJETOS_SEM_CLASSIFICACAO=%%c
)

echo.
echo ========================================
echo EXECUCAO CONCLUIDA COM SUCESSO
echo Data e hora: %END_DATE% %END_TIME%
echo ========================================
echo EXECUCAO CONCLUIDA COM SUCESSO >> %LOG_FILE%
echo Data e hora: %END_DATE% %END_TIME% >> %LOG_FILE%

rem Cálculo da duração (corrigido)
rem Extrair componentes de tempo (hora, minuto, segundo)
for /f "tokens=1-4 delims=:,. " %%a in ("%START_TIME%") do (
    set /a START_HOUR=%%a
    set /a START_MIN=%%b
    set /a START_SEC=%%c
)

for /f "tokens=1-4 delims=:,. " %%a in ("%END_TIME%") do (
    set /a END_HOUR=%%a
    set /a END_MIN=%%b
    set /a END_SEC=%%c
)

rem Calcular duração considerando diferentes dias
set /a DURACAO_DIAS=0
if not "%START_DATE%" == "%END_DATE%" (
    set /a DURACAO_DIAS=1
    rem Nota: este é um cálculo simplificado para execuções que cruzam apenas um dia
)

rem Calcular segundos totais
set /a START_TOTAL_SEC=(%START_HOUR% * 3600) + (%START_MIN% * 60) + %START_SEC%
set /a END_TOTAL_SEC=(%END_HOUR% * 3600) + (%END_MIN% * 60) + %END_SEC%

if %DURACAO_DIAS% GTR 0 (
    set /a END_TOTAL_SEC=END_TOTAL_SEC + (DURACAO_DIAS * 24 * 3600)
)

set /a DIFF_SEC=END_TOTAL_SEC - START_TOTAL_SEC
if %DIFF_SEC% LSS 0 (
    set /a DIFF_SEC=86400 + DIFF_SEC
)

rem Converter segundos totais para horas:minutos:segundos
set /a DURACAO_HORAS=DIFF_SEC / 3600
set /a DIFF_SEC=DIFF_SEC %% 3600
set /a DURACAO_MINUTOS=DIFF_SEC / 60
set /a DURACAO_SEGUNDOS=DIFF_SEC %% 60

rem Formatar com zeros à esquerda se necessário
if %DURACAO_HORAS% LSS 10 set DURACAO_HORAS=0%DURACAO_HORAS%
if %DURACAO_MINUTOS% LSS 10 set DURACAO_MINUTOS=0%DURACAO_MINUTOS%
if %DURACAO_SEGUNDOS% LSS 10 set DURACAO_SEGUNDOS=0%DURACAO_SEGUNDOS%

rem Definir a string formatada da duração
set DURACAO=%DURACAO_HORAS%:%DURACAO_MINUTOS%:%DURACAO_SEGUNDOS%

echo Duração da execução: %DURACAO%
echo Duração da execução: %DURACAO% >> %LOG_FILE%

rem Enviar notificação via Teams
echo Enviando notificação via Teams...
cd /d "%ROOT%"
python logs\send_teams_notification_fixed.py --start "%START_DATE% %START_TIME%" --end "%END_DATE% %END_TIME%" --duration "%DURACAO%"

if %errorlevel% equ 0 (
    echo Notificação enviada com sucesso.
) else (
    echo Falha ao enviar notificação.
)

goto fim

:erro
set END_DATE=%date%
set END_TIME=%time%
echo.
echo ========================================
echo ERRO NA EXECUCAO
echo Verifique os logs para mais detalhes
echo ========================================
echo ERRO NA EXECUCAO >> %LOG_FILE%
echo Data e hora do erro: %END_DATE% %END_TIME% >> %LOG_FILE%
echo Diretório atual no momento do erro: %CD% >> %LOG_FILE%

rem Desativar ambiente virtual se foi ativado
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call deactivate
    echo Ambiente virtual desativado
    echo Ambiente virtual desativado >> %LOG_FILE%
)

rem Enviar notificação de erro via Teams
echo Enviando notificação de erro via Teams...
cd /d "%ROOT%"
python logs\send_teams_notification_fixed.py --error --start "%START_DATE% %START_TIME%" --end "%END_DATE% %END_TIME%" --duration "%DURACAO%" --error-msg "Erro no diretório: %CD%. Verifique logs para mais detalhes."

:fim
echo.
echo Execução finalizada.
echo Pressione qualquer tecla para sair...
pause > nul
