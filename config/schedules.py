from prefect.server.schemas.schedules import CronSchedule

# Agendamento diário (dias de semana)
DAILY_MORNING_SCHEDULE = CronSchedule(
    cron="0 8 * * 1-5", timezone="America/Sao_Paulo"  # Segunda a sexta às 8h
)

# Agendamento de fim de semana
WEEKEND_SCHEDULE = CronSchedule(
    cron="0 10 * * 6,0", timezone="America/Sao_Paulo"  # Sábados e domingos às 10h
)

# Agendamento para execução a cada 6 horas
SIX_HOURLY_SCHEDULE = CronSchedule(
    cron="0 */6 * * *", timezone="America/Sao_Paulo"  # A cada 6 horas
)

# Agendamento para execução mensal
MONTHLY_SCHEDULE = CronSchedule(
    cron="0 9 1 * *", timezone="America/Sao_Paulo"  # Dia 1 de cada mês às 9h
)
