import os
import sys
import time
from datetime import datetime

# Add directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'core'))

# Import orchestrator logger
from logs.orchestrator_logs import OrchestratorLogger

# Import main functions from each module
# We'll import the actual functions, not the whole modules
from core.pipeline_embrapii_srinfo.main import main_pipeline_srinfo as pipeline_main
from core.atualizar_google_sheets.main import main as google_sheets_main
from core.api_datapii.main import main as api_datapii_main
from core.pipeline_embrapii_srinfo.scripts_public.comparar_excel import comparar_excel
from core.pipeline_embrapii_srinfo.scripts_public.whatsapp import enviar_whatsapp
from logs.teams_notifier import enviar_notificacao_teams

def execute_module(module_name, module_function, logger, module_idx=None):
    """Execute a module and handle logging"""
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

def main():
    """Main orchestrator function"""
    # Initialize the logger
    logger = OrchestratorLogger.get_instance()
    
    # Record start time
    start_time = datetime.now()
    print(f"Starting orchestration at {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Execute modules in sequence
    success = True
    
    # 1. Execute pipeline_embrapii_srinfo
    if success:
        success = execute_module("pipeline_embrapii_srinfo", pipeline_main, logger)
    
    # 2. Execute atualizar_google_sheets
    if success:
        success = execute_module("atualizar_google_sheets", google_sheets_main, logger)
    
    # 3. Execute api_datapii
    if success:
        success = execute_module("api_datapii", api_datapii_main, logger)
    
    # Calculate total execution time
    end_time = datetime.now()
    duration = end_time - start_time
    duration_str = f"{duration.seconds//3600:02}:{(duration.seconds//60)%60:02}:{duration.seconds%60:02}"
    
    print(f"\n{'='*50}")
    print(f"Orchestration {'completed successfully' if success else 'failed'}")
    print(f"Start time: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Total duration: {duration_str}")
    print(f"{'='*50}")
    
    # Get statistics and send notifications
    try:
        if success:
            # Get statistics for successful execution
            stats = comparar_excel()
            novos_projetos, novas_empresas, projetos_sem_classificacao = stats
            print(f"New projects: {novos_projetos}")
            print(f"New companies: {novas_empresas}")
            print(f"Projects without classification: {projetos_sem_classificacao}")
            
            # Send WhatsApp notification
            link = "https://embrapii.sharepoint.com/:x:/r/sites/GEPES/Documentos%20Compartilhados/DWPII/srinfo/classificacao_projeto.xlsx?d=wb7a7a439310f4d52a37728b9f1833961&csf=1&web=1&e=qXpfgA"
            link_snapshot = "https://embrapii.sharepoint.com/:f:/r/sites/GEPES/Documentos%20Compartilhados/Reports?csf=1&web=1&e=aVdkyL"
            mensagem = (
                f"*Pipeline SRInfo*\n"
                f'Iniciado em: {start_time.strftime("%d/%m/%Y %H:%M:%S")}\n'
                f'Finalizado em: {end_time.strftime("%d/%m/%Y %H:%M:%S")}\n'
                f"_Duração total: {duration_str}_\n\n"
                f"Novos projetos: {novos_projetos}\n"
                f"Novas empresas: {novas_empresas}\n"
                f"Projetos sem classificação: {projetos_sem_classificacao}\n\n"
                f"Relatório Executivo (snapshot): {link_snapshot}\n\n"
                f"Link para classificação dos projetos: {link}"
            )
            
            try:
                enviar_whatsapp(mensagem)
                print("WhatsApp notification sent successfully")
            except Exception as e:
                print(f"Error sending WhatsApp notification: {str(e)}")
                
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
                    "error_msg": "Pipeline execution failed. Check logs for details."
                }
                
                # Send the notification
                enviar_notificacao_teams(error_stats)
                print("Teams error notification sent successfully")
            except Exception as e:
                print(f"Error sending Teams error notification: {str(e)}")
    except Exception as e:
        print(f"Error in notification process: {str(e)}")
    
    # End the execution in the logger
    logger.end_execution("success" if success else "error")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
