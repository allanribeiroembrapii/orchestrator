@echo off
rem Define codificação UTF-8 para o console
chcp 65001 > nul

title Teste de Notificação Teams
echo ========================================
echo TESTE DE NOTIFICAÇÃO TEAMS
echo Data e hora: %date% %time%
echo ========================================
echo.

rem Definir caminho raiz do projeto
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
echo Diretório raiz: %ROOT%
echo.

rem Ativar ambiente virtual se existir
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call "%ROOT%\venv\Scripts\activate.bat"
    echo Ambiente virtual ativado
)

rem Testar envio de notificação
echo Enviando notificação de teste para o Teams...
python "%ROOT%\logs\send_teams_notification_fixed.py" --start "%date% %time%" --end "%date% %time%" --duration "00:30:00"

rem Desativar ambiente virtual se foi ativado
if exist "%ROOT%\venv\Scripts\activate.bat" (
    call deactivate
    echo Ambiente virtual desativado
)

echo.
echo ========================================
echo TESTE CONCLUÍDO
echo ========================================

echo.
echo Execução finalizada. 
echo Pressione qualquer tecla para sair...
pause > nul
