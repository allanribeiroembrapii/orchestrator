from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta
from flows.etl.extract_flows.empresa_extract import empresa_extract_flow

# Deployment apenas para extração de empresas (exemplo)
empresa_extract_deployment = Deployment.build_from_flow(
    flow=empresa_extract_flow,
    name="Extração de Empresas",
    schedule=IntervalSchedule(interval=timedelta(hours=6)),
    tags=["embrapii", "srinfo", "extract", "empresa"],
    description="Extração periódica de dados de empresas",
)

if __name__ == "__main__":
    empresa_extract_deployment.apply()
    print("Deployment de extração de empresas criado com sucesso!")
