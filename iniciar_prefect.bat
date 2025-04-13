@echo off
echo Iniciando Prefect para orchestrator EMBRAPII...

:: Mudar para o diretório do projeto
cd /d %~dp0

:: Ativar ambiente virtual (se estiver usando)
:: call venv\Scripts\activate

:: Verificar se o servidor Prefect está rodando
prefect config view >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando servidor Prefect...
    start /MIN cmd /c "prefect server start"
    timeout /t 10 /nobreak >nul
)

:: Iniciar Prefect Worker
start /MIN cmd /c "prefect worker start -p embrapii-pool"

echo Prefect worker iniciado com sucesso!
