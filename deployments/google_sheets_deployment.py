from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.google_sheets_flow import google_sheets_flow
from config.schedules import DAILY_MORNING_SCHEDULE

# Deployment do Google Sheets
google_sheets_deployment = Deployment.build_from_flow(
    flow=google_sheets_flow,
    name="Google Sheets - Atualização",
    parameters={},
    schedule=DAILY_MORNING_SCHEDULE,
    tags=["embrapii", "google_sheets"],
    description="Atualização diária das planilhas no Google Sheets",
)

# Aplicar deployment
if __name__ == "__main__":
    google_sheets_deployment.apply()
    print("Deployment do Google Sheets criado com sucesso!")
