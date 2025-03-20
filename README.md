# Orquestrador de Pipeline EMBRAPII SRInfo

Este projeto implementa um orquestrador baseado em Prefect para o pipeline de extração, transformação e carregamento de dados do SRInfo da EMBRAPII.

## Estrutura do Projeto

```
orchestrator/
├── config/                  # Configurações do projeto
│   ├── schedules.py         # Agendamentos para os deployments
│   └── settings.py          # Configurações gerais
├── core/                    # Scripts originais (não modificados)
├── deployments/             # Configurações de deployments
│   ├── main_deployment.py   # Deployment principal
│   └── daily_extract_deployment.py  # Deployment de extração diária
├── flows/                   # Flows do Prefect
│   ├── main_flow.py         # Flow principal
│   ├── empresa_flow.py      # Flow de empresas
│   ├── unidade_embrapii_flow.py  # Flow de unidades EMBRAPII
│   ├── projeto_flow.py      # Flow de projetos
│   ├── prospeccao_flow.py   # Flow de prospecção
│   ├── negociacoes_flow.py  # Flow de negociações
│   ├── classificacao_flow.py  # Flow de classificação de projetos
│   ├── portfolio_flow.py    # Flow de portfolio
│   ├── sharepoint_flow.py   # Flow de operações do SharePoint
│   ├── clickhouse_flow.py   # Flow de consultas ClickHouse
│   ├── qim_ues_flow.py      # Flow de QIM UES
│   ├── google_sheets_flow.py  # Flow de atualização do Google Sheets
│   ├── notification_flow.py  # Flow de notificações
│   └── utils_flow.py        # Funções utilitárias
├── monitoring/              # Monitoramento
├── tasks/                   # Tasks reutilizáveis
│   ├── browser/             # Tasks relacionadas ao WebDriver
│   └── sharepoint/          # Tasks relacionadas ao SharePoint
├── .env                     # Variáveis de ambiente
├── prefect.yaml             # Configuração do Prefect
├── pyproject.toml           # Configuração do projeto Python
└── requirements.txt         # Dependências do projeto
```

## Módulos Disponíveis

O pipeline é composto pelos seguintes módulos:

1. **SharePoint**: Busca e envio de arquivos para o SharePoint
2. **Empresas**: Informações de empresas e empresas contratantes
3. **Unidades EMBRAPII**: Informações de unidades, equipe, termos de cooperação, plano de ação e classificação PEO
4. **Projetos**: Sebrae, projetos contratados, projetos de empresas, projetos, contratos, estudantes, pedidos PI e macroentregas
5. **Prospecção**: Comunicação, eventos SRInfo e prospecção
6. **Negociações**: Negociações, propostas técnicas e planos de trabalho
7. **Classificação**: Classificação de projetos e classificação CG de projetos
8. **Portfolio**: Processamento de portfolio
9. **ClickHouse**: Consultas ao ClickHouse
10. **QIM UES**: Processamento de QIM UES
11. **Google Sheets**: Atualização de planilhas no Google Sheets

## Configuração

1. Instale as dependências:

   ```
   pip install -r requirements.txt
   ```

2. Configure as variáveis de ambiente no arquivo `.env`:
   ```
   ROOT=caminho/para/pipeline_embrapii_srinfo
   SRINFO_USERNAME=seu_usuario
   PASSWORD=sua_senha
   PASTA_DOWNLOAD=caminho/para/downloads
   sharepoint_url_site=url_do_sharepoint
   sharepoint_site_name=nome_do_site
   sharepoint_doc_library=biblioteca_de_documentos
   sharepoint_email=seu_email
   sharepoint_password=sua_senha
   ```

## Execução

### Execução Local

Para executar o pipeline localmente:

```python
from flows.main_flow import main_pipeline_flow

# Executar com todos os módulos
main_pipeline_flow()

# Executar com módulos específicos
main_pipeline_flow(
    selected_modules=[
        "sharepoint", "info_empresas", "projetos", "classificacao_projetos"
    ],
    gerar_snapshot=True,
    enviar_wpp=True
)
```

### Deployments

Para criar deployments no servidor Prefect:

```bash
python deployments/main_deployment.py
```

Isso criará dois deployments:

- **Pipeline SRInfo - Diário**: Executa um conjunto reduzido de módulos nos dias de semana
- **Pipeline SRInfo - Fim de Semana**: Executa todos os módulos nos fins de semana, incluindo o plano de metas

## Desenvolvimento

### Adicionando um Novo Módulo

1. Crie um novo arquivo de flow em `flows/`
2. Implemente as tasks necessárias
3. Adicione o flow ao `main_flow.py`
4. Atualize os deployments conforme necessário

### Testando um Módulo Específico

Para testar um módulo específico:

```python
from flows.nome_do_modulo_flow import nome_do_modulo_flow

# Executar o flow
nome_do_modulo_flow()
```

## Monitoramento

O monitoramento do pipeline pode ser feito através da interface do Prefect ou através dos logs gerados durante a execução.
