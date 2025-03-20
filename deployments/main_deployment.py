from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.main_flow import main_pipeline_flow
from config.schedules import DAILY_MORNING_SCHEDULE, WEEKEND_SCHEDULE

# Módulos para execução diária (dias de semana)
daily_modules = [
    "sharepoint",
    "info_empresas",
    "empresas_contratantes",
    "info_unidades",
    "projetos",
    "contratos",
    "classificacao_projetos",
    "portfolio",
    "levar_arquivos_sharepoint",
    "consultas_clickhouse",
]

# Deployment diário (dias de semana)
daily_deployment = Deployment.build_from_flow(
    flow=main_pipeline_flow,
    name="Pipeline SRInfo - Diário",
    parameters={
        "selected_modules": daily_modules,
        "plano_metas": False,
        "gerar_snapshot": True,
        "enviar_wpp": True,
        "enviar_teams": True,
    },
    schedule=DAILY_MORNING_SCHEDULE,
    tags=["embrapii", "srinfo", "diario"],
    description="Pipeline diário (dias de semana) de extração e processamento de dados do SRInfo",
)

# Deployment de fim de semana (com plano de metas e todos os módulos)
weekend_deployment = Deployment.build_from_flow(
    flow=main_pipeline_flow,
    name="Pipeline SRInfo - Fim de Semana",
    parameters={
        "selected_modules": None,  # Todos os módulos
        "plano_metas": True,
        "gerar_snapshot": True,
        "enviar_wpp": True,
        "enviar_teams": True,
    },
    schedule=WEEKEND_SCHEDULE,
    tags=["embrapii", "srinfo", "fim-de-semana", "plano-metas"],
    description="Pipeline de fim de semana com processamento de plano de metas",
)

# Aplicar deployments
if __name__ == "__main__":
    daily_deployment.apply()
    weekend_deployment.apply()
    print("Deployments do Pipeline SRInfo criados com sucesso!")
