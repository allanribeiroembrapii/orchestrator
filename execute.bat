@echo off
chcp 65001 > nul
title Orquestrador Embrapii

echo ========================================
echo         EMBRAPII ORCHESTRATOR
echo ========================================
echo Data e hora: %date% %time%
echo.

rem Caminho raiz
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

rem Ativar ambiente virtual
call "%ROOT%\.venv\Scripts\activate.bat"

rem Confirmar Python do venv
echo Python do ambiente virtual:
python --version
echo.

rem Executar o orquestrador
cd /d "%ROOT%"
echo Executando orquestrador...
python main.py
if %errorlevel% neq 0 (
    echo ERRO: Falha na execução do orquestrador.
    goto fim
)
echo.

echo TODOS OS MÓDULOS EXECUTADOS COM SUCESSO!

:fim
echo.
echo Execução finalizada. Pressione qualquer tecla para sair...
pause > nul
