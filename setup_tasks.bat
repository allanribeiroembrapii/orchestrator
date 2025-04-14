@echo off
echo Configurando tarefas no Agendador de Tarefas do Windows...

REM Obter caminho absoluto do projeto
set PROJECT_DIR=%~dp0
set PROJECT_DIR=%PROJECT_DIR:~0,-1%

REM Criar tarefa para execução diária às 6:00
schtasks /Create /TN "PipelinesDiarios" ^
        /TR "%PROJECT_DIR%\run_daily.bat" ^
        /SC DAILY /ST 06:00 ^
        /RL HIGHEST /F

REM Criar tarefa para execução na inicialização (opcional)
schtasks /Create /TN "PipelinesNaInicializacao" ^
        /TR "%PROJECT_DIR%\run_daily.bat" ^
        /SC ONSTART /DELAY 0010:00 ^
        /RL HIGHEST /F

echo Tarefas configuradas com sucesso!
echo - PipelinesDiarios: Executa diariamente às 06:00
echo - PipelinesNaInicializacao: Executa 10 minutos após a inicialização do Windows

echo.
echo Use o comando abaixo para visualizar as tarefas configuradas:
echo schtasks /Query /TN "PipelinesDiarios"
echo schtasks /Query /TN "PipelinesNaInicializacao"