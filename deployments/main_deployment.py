from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.main_flow import main_pipeline_flow
from config.schedules import DAILY_MORNING_SCHEDULE, WEEKEND_SCHEDULE

# Módulos para execução diária (dias de semana)
daily_modules = [
    "atualizar_google_sheets",
]

# Deployment diário (dias de semana)
daily_deployment = Deployment.build_from_flow(
    flow=main_pipeline_flow,
    name="Google Sheets - Atualização Diária",
    parameters={
        "selected_modules": daily_modules,
        "plano_metas": False,
        "gerar_snapshot": True,
        "enviar_wpp": True,
        "enviar_teams": True,
    },
    schedule=DAILY_MORNING_SCHEDULE,
    tags=["embrapii", "google-sheets", "diario"],
    description="Pipeline diário (dias de semana) para atualização do Google Sheets",
)

# Deployment de fim de semana (apenas Google Sheets)
weekend_deployment = Deployment.build_from_flow(
    flow=main_pipeline_flow,
    name="Google Sheets - Atualização Fim de Semana",
    parameters={
        "selected_modules": ["atualizar_google_sheets"],
        "plano_metas": False,
        "gerar_snapshot": True,
        "enviar_wpp": True,
        "enviar_teams": True,
    },
    schedule=WEEKEND_SCHEDULE,
    tags=["embrapii", "google-sheets", "fim-de-semana"],
    description="Pipeline de fim de semana para atualização do Google Sheets",
)

# Aplicar deployments
if __name__ == "__main__":
    daily_deployment.apply()
    weekend_deployment.apply()
    print("Deployments do Google Sheets criados com sucesso!")
