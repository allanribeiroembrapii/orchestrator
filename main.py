import os
import sys
import time
from datetime import datetime, timedelta
import locale
from connect_vpn import connect_vpn, disconnect_vpn

# # Add directories to path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)
# sys.path.append(os.path.join(current_dir, 'core'))

# Import orchestrator logger
from logs.orchestrator_logs import OrchestratorLogger

# Import main functions from each module
# We'll import the actual functions, not the whole modules
from core.pipeline_embrapii_srinfo.main import main_pipeline_srinfo as pipeline_main
from core.atualizar_google_sheets.main import main as google_sheets_main
from core.api_datapii.main import main as api_datapii_main
from core.cg_classificacao_projetos_do.main import main as cg_classificacao_projetos_do
from core.pipeline_embrapii_srinfo.scripts_public.comparar_excel import comparar_excel
from core.qim_ues.main import qim_ues
from core.clickhouse_saldo_bancario.main import main_agfinanceiro
from core.clickhouse_querys.main import clickhouse_querys
from core.servdata_bmaisp.main import main_bmaisp as bmaisp
from core.rvg_repositorio_visuais_graficos.main import main_rvg
from core.classificacao_financeira.main import main_classificacao_financeira
from core.classifier_gepes.main import main_classifier_gepes
from core.portfolio2.main import main_portfolio2
from logs.teams_notifier import enviar_notificacao_teams

def execute_module(module_name, module_function, logger, module_idx=None, frequency=None):
    """Execute a module and handle logging"""

    if not should_execute_today(frequency):
        print(f"\nSkipping {module_name} due to frequency setting: '{frequency}'")
        return True
    
    start_time = datetime.now()
    print(f"\n{'='*50}")
    print(f"Executing {module_name}...")
    print(f"Start time: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*50}")
    
    if module_idx is None:
        module_idx = logger.start_module(module_name)
    
    try:
        module_function()
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n{module_name} completed successfully!")
        print(f"End time: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Duration: {duration}")
        logger.end_module(module_idx, "success")
        return True
    except Exception as e:
        end_time = datetime.now()
        print(f"\nError in {module_name}: {str(e)}")
        print(f"End time: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
        logger.end_module(module_idx, "error", error=e)
        
        # Special case: If the error is about URL exceeding Excel's maximum length,
        # log it but continue with the pipeline
        if "URL exceeds Excel's maximum length" in str(e):
            print(f"Note: Ignoring 'URL exceeds Excel's maximum length' error and continuing pipeline execution.")
            return True
        
        return False

def should_execute_today(frequency: str | int | None) -> bool:
    if frequency is None:
        return True  # Executa sempre se não há frequência definida

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    today = datetime.today()
    weekday = today.strftime('%A').lower()
    day_of_month = today.day

    if isinstance(frequency, str):
        frequency = frequency.strip().lower()

        # Frequência diária
        if frequency == "daily":
            return True

        # Dia da semana
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if frequency in weekdays:
            return frequency == weekday

        # Dia do mês (ex: "15")
        if frequency.isdigit():
            return int(frequency) == day_of_month

        # Novo formato: N-ésimo dia útil (ex: "5º")
        if frequency.endswith("º"):
            try:
                nth = int(frequency[:-1])  # remove "º" e converte
                return is_nth_business_day(today, nth)
            except ValueError:
                return False  # formato inválido

    elif isinstance(frequency, int):
        return frequency == day_of_month

    return False

def is_nth_business_day(date: datetime, n: int) -> bool:
    """Verifica se a data atual é o enésimo dia útil do mês"""
    current = date.replace(day=1)
    count = 0
    while current.month == date.month:
        if current.weekday() < 5:  # 0 = segunda, ..., 4 = sexta
            count += 1
            if count == n:
                return current.date() == date.date()
        current += timedelta(days=1)
    return False

def main():
    """Main orchestrator function"""
    # Initialize the logger
    logger = OrchestratorLogger.get_instance()
    
    # Record start time
    start_time = datetime.now()
    print(f"Starting orchestration at {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Execute modules in sequence
    success = True
    
    # #pipeline_embrapii_srinfo
    if success:
        success = execute_module("pipeline_embrapii_srinfo", pipeline_main, logger, frequency='daily')
  
    # qim_ues
    if success:
        success = execute_module("qim_ues", qim_ues, logger, frequency='monday')

    # atualizar_google_sheets
    if success:
        success = execute_module("atualizar_google_sheets", google_sheets_main, logger, frequency='daily')

    # CG Classificação de Projetos - Validação Diretoria de Operações
    if success:
        success = execute_module("cg_classificacao_projetos_do", cg_classificacao_projetos_do, logger, frequency='monday')
    
    # Classificação Financeira dos Projetos Modelo Embrapii
    if success:
        success = execute_module("classificacao_financeira", main_classificacao_financeira, logger, frequency='daily')
    
    # Brasil Mais Produtivo
    if success:
        success = execute_module("bmaisp", bmaisp, logger, frequency='monday')

    # api_datapii
    if success:
        success = execute_module("api_datapii", api_datapii_main, logger, frequency='daily')

    if success:
        connect_vpn()

        # Agenda de Dados Financeiros - Saldo Financeiro
        if success:
            success = execute_module("main_agfinanceiro", main_agfinanceiro, logger, frequency='daily')

        # Clickhouse querys
        if success:
            success = execute_module("clickhouse_querys", clickhouse_querys, logger, frequency='daily')

        # Repositório de visuais gráficos
        # if success:
        #     success = execute_module("rvg", main_rvg, logger, frequency='daily')
        #     return

        disconnect_vpn()
    
    # Classifier
    if success:
        success = execute_module("classifier_gepes", main_classifier_gepes, logger, frequency='daily')

    # Portfolio2
    if success:
        success = execute_module("portfolio2", main_portfolio2, logger, frequency='daily')

    # Mensagem de Finalização
    if success:
        finalizacao_mensagem(success, start_time)
        
    # End the execution in the logger
    logger.end_execution("success" if success else "error")
    
    return 0 if success else 1


def finalizacao_mensagem(success, start_time):
    end_time = datetime.now()
    duration = end_time - start_time
    duration_str = f"{duration.seconds//3600:02}:{(duration.seconds//60)%60:02}:{duration.seconds%60:02}"
    print(f"\n{'='*50}")
    print(f"Orchestration {'completed successfully' if success else 'failed'}")
    print(f"Start time: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Total duration: {duration_str}")
    print(f"{'='*50}")

    try:
        if success:
            # Get statistics for successful execution
            stats = comparar_excel()
            novos_projetos, novas_empresas, projetos_sem_classificacao = stats
                
            # Send Teams notification for success
            try:
                # Prepare stats for Teams notification
                teams_stats = {
                    "status": "success",
                    "inicio": start_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "fim": end_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "duracao": duration_str,
                    "novos_projetos": novos_projetos,
                    "novas_empresas": novas_empresas,
                    "projetos_sem_classificacao": projetos_sem_classificacao
                }
                
                # Send the notification
                enviar_notificacao_teams(teams_stats)
                print("Teams notification sent successfully")
            except Exception as e:
                print(f"Error sending Teams notification: {str(e)}")
        else:
            # Send Teams notification for failure
            try:
                # Prepare error stats for Teams notification
                error_stats = {
                    "status": "error",
                    "inicio": start_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "fim": end_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "duracao": duration_str,
                    "error_msg": "Orchestrator execution failed. Check logs for details."
                }
                
                # Send the notification
                enviar_notificacao_teams(error_stats)
                print("Teams error notification sent successfully")
            except Exception as e:
                print(f"Error sending Teams error notification: {str(e)}")
    except Exception as e:
        print(f"Error in notification process: {str(e)}")

if __name__ == "__main__":
    sys.exit(main())
