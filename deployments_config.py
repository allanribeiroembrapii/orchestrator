"""
Este script foi substituído pelo uso do prefect.yaml e do comando 'prefect deploy'.

Para criar deployments, você pode:

1. Usar o comando CLI:
   prefect deploy

2. Ou descomente e use o método serve() no arquivo orchestrator_flow.py:
   orquestrador_diario.serve(
       name="EMBRAPII - Sequência Diária",
       cron="0 8 * * *",
       tags=["embrapii", "diario"],
       description="Executa diariamente os scripts pipeline_embrapii_srinfo, atualizar_google_sheets e api_datapii em sequência",
       work_pool_name="embrapii-pool",
   )

3. Ou execute o script setup_prefect.py:
   python setup_prefect.py
"""

print("Este script foi substituído pelo uso do prefect.yaml e do comando 'prefect deploy'.")
print("Por favor, use um dos métodos descritos no comentário do script.")
