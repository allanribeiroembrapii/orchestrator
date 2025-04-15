@echo off
rem Define codificação UTF-8 para o console
chcp 65001 > nul

title Orquestrador Embrapii - Versao Basica
echo ========================================
echo EMBRAPII ORCHESTRATOR - VERSAO BASICA
echo Data e hora: %date% %time%
echo ========================================
echo.

rem Definir caminhos básicos
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
set ROOT_PIPELINE=%ROOT%\core\pipeline_embrapii_srinfo
set ROOT_GSHET=%ROOT%\core\atualizar_google_sheets
set ROOT_DATAPII=%ROOT%\core\api_datapii

echo Verificando diretórios...
echo.

if not exist "%ROOT_PIPELINE%" (
    echo ERRO: Diretório pipeline_embrapii_srinfo não encontrado em:
    echo %ROOT_PIPELINE%
    goto fim
)

if not exist "%ROOT_GSHET%" (
    echo ERRO: Diretório atualizar_google_sheets não encontrado em:
    echo %ROOT_GSHET%
    goto fim
)

if not exist "%ROOT_DATAPII%" (
    echo ERRO: Diretório api_datapii não encontrado em:
    echo %ROOT_DATAPII%
    goto fim
)

echo VERIFICACAO INICIAL: OK
echo Todos os diretórios principais foram encontrados.
echo.

rem Verificar Python
echo Verificando instalação do Python...
where python 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado no PATH do sistema.
    goto fim
)

echo Python encontrado:
python --version
echo.

rem Apenas para teste - não executa os módulos reais
echo TESTE CONCLUÍDO COM SUCESSO
echo Todos os componentes básicos foram verificados.
echo.
echo Para executar os módulos reais, edite este script para remover "goto fim" abaixo.
goto fim

rem ===== EXECUÇÃO DOS MÓDULOS =====

echo 1. Executando pipeline_embrapii_srinfo...
cd /d "%ROOT_PIPELINE%"
if not exist "main.py" (
    echo ERRO: main.py não encontrado.
    goto fim
)
python main.py
if %errorlevel% neq 0 (
    echo ERRO: Falha ao executar pipeline_embrapii_srinfo.
    goto fim
)
echo.

echo 2. Executando atualizar_google_sheets...
cd /d "%ROOT_GSHET%"
if not exist "main.py" (
    echo ERRO: main.py não encontrado.
    goto fim
)
python main.py
if %errorlevel% neq 0 (
    echo ERRO: Falha ao executar atualizar_google_sheets.
    goto fim
)
echo.

echo 3. Executando api_datapii...
cd /d "%ROOT_DATAPII%"
if not exist "main.py" (
    echo ERRO: main.py não encontrado.
    goto fim
)
python main.py
if %errorlevel% neq 0 (
    echo ERRO: Falha ao executar api_datapii.
    goto fim
)
echo.

echo TODOS OS MÓDULOS EXECUTADOS COM SUCESSO!

:fim
echo.
echo Execução finalizada. 
echo Pressione qualquer tecla para sair...
pause > nul