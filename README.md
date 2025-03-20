# Orquestrador de Pipeline EMBRAPII SRInfo

Este projeto implementa um orquestrador baseado em [Prefect](https://www.prefect.io/) para o pipeline de extração, transformação e carregamento (ETL) de dados do SRInfo da EMBRAPII. O orquestrador automatiza a coleta, processamento e disponibilização de dados de diversas fontes, permitindo a geração de relatórios e análises.

## Estrutura do Projeto

```
orchestrator/
├── config/                  # Configurações do projeto
│   ├── module_configs.py    # Configurações específicas de cada módulo
│   ├── schedules.py         # Agendamentos para os deployments
│   └── settings.py          # Configurações gerais
├── core/                    # Scripts originais de processamento
│   ├── analises_relatorios/ # Scripts para análises e relatórios
│   ├── atualizar_google_sheets/ # Scripts para atualização do Google Sheets
│   ├── cg_classificacao_projetos/ # Scripts para classificação CG de projetos
│   ├── consultas_clickhouse/ # Scripts para consultas ao ClickHouse
│   ├── empresa/             # Scripts para processamento de empresas
│   ├── negociacoes/         # Scripts para processamento de negociações
│   ├── office365_api/       # Scripts para interação com Office 365
│   ├── projeto/             # Scripts para processamento de projetos
│   ├── prospeccao/          # Scripts para processamento de prospecção
│   ├── qim_ues/             # Scripts para processamento de QIM UES
│   ├── scripts_public/      # Scripts utilitários compartilhados
│   ├── ue_peo/              # Scripts para processamento de UE PEO
│   └── unidade_embrapii/    # Scripts para processamento de unidades EMBRAPII
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
│   ├── utils_flow.py        # Funções utilitárias
│   ├── data/                # Flows relacionados a dados
│   └── etl/                 # Flows de ETL (extract, transform, load)
│       ├── extract_flows/   # Flows de extração
│       ├── transform_flows/ # Flows de transformação
│       └── load_flows/      # Flows de carregamento
├── monitoring/              # Monitoramento
│   ├── alerts.py            # Sistema de alertas
│   └── health_check.py      # Verificação de saúde do sistema
├── tasks/                   # Tasks reutilizáveis
│   ├── browser/             # Tasks relacionadas ao WebDriver
│   ├── data_processing/     # Tasks de processamento de dados
│   ├── notification/        # Tasks de notificação
│   └── sharepoint/          # Tasks relacionadas ao SharePoint
├── .env                     # Variáveis de ambiente (local)
├── .env.example             # Exemplo de variáveis de ambiente
├── api_google_sheets.json   # Credenciais da API do Google Sheets
├── prefect.yaml             # Configuração do Prefect
├── pyproject.toml           # Configuração do projeto Python
├── requirements.txt         # Dependências do projeto
└── run_pipeline.py          # Script para execução do pipeline
```

## Módulos Disponíveis

O pipeline é composto pelos seguintes módulos:

1. **SharePoint**: Busca e envio de arquivos para o SharePoint

   - `buscar_arquivos_sharepoint`: Baixa arquivos do SharePoint
   - `levar_arquivos_sharepoint`: Envia arquivos para o SharePoint

2. **Empresas**: Informações de empresas

   - `info_empresas`: Extração de informações de empresas
   - `empresas_contratantes`: Análise de empresas contratantes

3. **Unidades EMBRAPII**: Informações de unidades

   - `info_unidades`: Informações gerais de unidades
   - `equipe_ue`: Informações de equipes das unidades
   - `termos_cooperacao`: Termos de cooperação
   - `plano_acao`: Planos de ação
   - `ue_peo`: Classificação PEO das unidades

4. **Projetos**: Informações de projetos

   - `sebrae`: Projetos Sebrae
   - `projetos_contratados`: Projetos contratados
   - `projetos_empresas`: Projetos de empresas
   - `projetos`: Informações gerais de projetos
   - `contratos`: Contratos de projetos
   - `estudantes`: Estudantes envolvidos em projetos
   - `pedidos_pi`: Pedidos de propriedade intelectual
   - `macroentregas`: Macroentregas de projetos

5. **Prospecção**: Informações de prospecção

   - `comunicacao`: Comunicações
   - `eventos_srinfo`: Eventos registrados no SRInfo
   - `prospeccao`: Dados de prospecção

6. **Negociações**: Informações de negociações

   - `negociacoes`: Negociações em andamento
   - `propostas_tecnicas`: Propostas técnicas
   - `planos_trabalho`: Planos de trabalho

7. **Classificação**: Classificação de projetos

   - `classificacao_projetos`: Classificação geral de projetos
   - `cg_classificacao_projetos`: Classificação CG de projetos

8. **Portfolio**: Processamento de portfolio

   - `portfolio`: Análise e processamento de portfolio

9. **ClickHouse**: Consultas ao banco de dados ClickHouse

   - `consultas_clickhouse`: Execução de consultas e exportação de dados

10. **QIM UES**: Processamento de QIM UES

    - `qim_ues`: Processamento de dados QIM UES

11. **Google Sheets**: Atualização de planilhas no Google Sheets
    - `atualizar_google_sheets`: Atualização de planilhas com dados processados

## Configuração

1. Clone o repositório:

   ```bash
   git clone <url-do-repositorio>
   cd orchestrator
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente copiando o arquivo `.env.example` para `.env` e preenchendo os valores:

   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

   Exemplo de configuração do arquivo `.env`:

   ```
   ROOT=caminho/para/orchestrator
   SRINFO_USERNAME=seu_usuario
   PASSWORD=sua_senha
   PASTA_DOWNLOAD=caminho/para/downloads
   sharepoint_url_site=url_do_sharepoint
   sharepoint_site_name=nome_do_site
   sharepoint_doc_library=biblioteca_de_documentos
   sharepoint_email=seu_email
   sharepoint_password=sua_senha
   ```

4. Configure as credenciais do Google Sheets (se necessário):

   ```bash
   cp api_google_sheets.json.example api_google_sheets.json
   # Edite o arquivo api_google_sheets.json com suas credenciais
   ```

## Execução

### Execução via Linha de Comando

Para executar o pipeline via linha de comando:

```bash
# Executar com todos os módulos
python run_pipeline.py

# Executar com módulos específicos
python run_pipeline.py --modules sharepoint info_empresas projetos classificacao_projetos

# Executar com snapshot e notificação WhatsApp
python run_pipeline.py --snapshot --whatsapp
```

Opções disponíveis:

- `--modules`: Lista de módulos a serem executados (se não especificado, executa todos)
- `--plano-metas`: Executa o processamento do plano de metas
- `--snapshot`: Gera snapshot ao final da execução
- `--whatsapp`: Envia notificação pelo WhatsApp
- `--teams`: Envia notificação pelo Microsoft Teams (ativado por padrão)

### Execução Programática

Para executar o pipeline programaticamente em um script Python:

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
    enviar_wpp=True,
    enviar_teams=True
)
```

### Deployments

Para criar deployments no servidor Prefect:

```bash
python deployments/main_deployment.py
```

Isso criará dois deployments:

- **Pipeline SRInfo - Diário**: Executa um conjunto reduzido de módulos nos dias de semana (segunda a sexta às 8h)
- **Pipeline SRInfo - Fim de Semana**: Executa todos os módulos nos fins de semana (sábado e domingo às 10h)

Para criar um deployment específico para extração de empresas:

```bash
python deployments/daily_extract_deployment.py
```

## Guia de Desenvolvimento

### Criando uma Nova Task

Para criar uma nova task, siga estes passos:

1. Crie um novo arquivo Python no diretório `tasks/` ou em um subdiretório apropriado
2. Defina a task usando o decorador `@task` do Prefect

Exemplo:

```python
# tasks/data_processing/nova_task.py
from prefect import task, get_run_logger

@task(name="Minha Nova Task", retries=2, retry_delay_seconds=60)
def minha_nova_task(parametro1, parametro2=None):
    """
    Descrição da task e seus parâmetros.

    Args:
        parametro1: Descrição do parâmetro 1
        parametro2: Descrição do parâmetro 2 (opcional)

    Returns:
        Descrição do retorno
    """
    logger = get_run_logger()
    logger.info(f"Executando minha nova task com {parametro1}")

    # Lógica da task
    resultado = parametro1 + (parametro2 or 0)

    return resultado
```

### Criando um Novo Flow

Para criar um novo flow, siga estes passos:

1. Crie um novo arquivo Python no diretório `flows/` ou em um subdiretório apropriado
2. Defina o flow usando o decorador `@flow` do Prefect
3. Importe e utilize as tasks necessárias

Exemplo:

```python
# flows/meu_novo_flow.py
from prefect import flow, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar tasks
from tasks.data_processing.nova_task import minha_nova_task
from tasks.sharepoint.download_tasks import download_arquivo_task

@flow(name="Meu Novo Pipeline")
def meu_novo_flow(parametro="valor_padrao"):
    """
    Flow para executar meu novo pipeline.

    Args:
        parametro: Parâmetro de configuração

    Returns:
        Resultado do flow
    """
    logger = get_run_logger()
    logger.info(f"Iniciando meu novo flow com {parametro}")

    # Executar tasks
    arquivo = download_arquivo_task("caminho/do/arquivo")
    resultado = minha_nova_task(arquivo, parametro2=10)

    return resultado

# Permitir execução direta para testes
if __name__ == "__main__":
    meu_novo_flow()
```

### Implementando um Novo Script no Modelo

Para implementar um novo script no modelo, siga estes passos:

1. Crie um novo diretório no `core/` para seu módulo (se necessário)
2. Crie a estrutura de diretórios para o processamento de dados:
   - `step_1_data_raw/`: Dados brutos
   - `step_2_stage_area/`: Área de staging
   - `step_3_data_processed/`: Dados processados
3. Implemente o script principal no diretório do módulo

Exemplo:

```python
# core/meu_modulo/main_meu_modulo.py
import os
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")

def processar_dados(caminho_entrada, caminho_saida):
    """Processa os dados de entrada e salva no caminho de saída."""
    # Carregar dados
    df = pd.read_excel(caminho_entrada)

    # Processar dados
    df_processado = df.copy()
    # ... lógica de processamento ...

    # Salvar resultado
    df_processado.to_excel(caminho_saida, index=False)
    return True

def main(driver=None):
    """Função principal do módulo."""
    # Definir caminhos
    current_dir = os.path.join(ROOT, "meu_modulo")
    raw_dir = os.path.join(current_dir, "step_1_data_raw")
    stage_dir = os.path.join(current_dir, "step_2_stage_area")
    processed_dir = os.path.join(current_dir, "step_3_data_processed")

    # Criar diretórios se não existirem
    for dir_path in [raw_dir, stage_dir, processed_dir]:
        os.makedirs(dir_path, exist_ok=True)

    # Definir caminhos de arquivos
    arquivo_entrada = os.path.join(raw_dir, "dados_entrada.xlsx")
    arquivo_saida = os.path.join(processed_dir, "dados_processados.xlsx")

    # Processar dados
    resultado = processar_dados(arquivo_entrada, arquivo_saida)

    return resultado

if __name__ == "__main__":
    main()
```

4. Crie um flow correspondente para integrar o script ao orquestrador:

```python
# flows/meu_modulo_flow.py
from prefect import flow, task, get_run_logger
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")
sys.path.append(ROOT)

# Importar o script original
from core.meu_modulo.main_meu_modulo import main as main_meu_modulo

@task(name="Processar Meu Módulo", retries=2)
def processar_meu_modulo_task(driver=None):
    """Task para processar meu módulo."""
    logger = get_run_logger()
    logger.info("Processando meu módulo...")

    resultado = main_meu_modulo(driver=driver)

    if resultado:
        logger.info("Processamento do meu módulo concluído com sucesso.")
    else:
        logger.error("Falha no processamento do meu módulo.")

    return resultado

@flow(name="Pipeline do Meu Módulo")
def meu_modulo_flow(driver=None, log=None, selected_modules=None):
    """
    Flow para processar dados do meu módulo.

    Args:
        driver: WebDriver configurado
        log: Lista de logs para registrar
        selected_modules: Lista de módulos selecionados para execução

    Returns:
        log: Lista atualizada de logs
    """
    logger = get_run_logger()

    if log is None:
        log = []

    if selected_modules is None or "meu_modulo" in selected_modules:
        logger.info("Executando módulo: meu_modulo")
        processar_meu_modulo_task(driver)
        log.append("meu_modulo")

    return log

if __name__ == "__main__":
    meu_modulo_flow()
```

5. Adicione o módulo à lista de módulos disponíveis no `main_flow.py`:

```python
# Adicionar à lista de imports
from flows.meu_modulo_flow import meu_modulo_flow

# Adicionar à lista de módulos disponíveis
if selected_modules is None:
    selected_modules = [
        # ... módulos existentes ...
        "meu_modulo",
        # ... outros módulos ...
    ]

# Adicionar à seção de execução
if "meu_modulo" in selected_modules:
    logger.info("Processando meu módulo...")
    log = meu_modulo_flow(driver, log, selected_modules)
```

### Criando Novos Agendamentos

Para criar um novo agendamento, siga estes passos:

1. Adicione a definição do agendamento no arquivo `config/schedules.py`:

```python
# Agendamento para execução semanal às segundas-feiras
WEEKLY_MONDAY_SCHEDULE = CronSchedule(
    cron="0 7 * * 1", timezone="America/Sao_Paulo"  # Segunda-feira às 7h
)
```

2. Crie um novo deployment no arquivo de deployment existente ou crie um novo arquivo:

```python
# deployments/weekly_deployment.py
from prefect.deployments import Deployment
from flows.main_flow import main_pipeline_flow
from config.schedules import WEEKLY_MONDAY_SCHEDULE

# Módulos para execução semanal
weekly_modules = [
    "sharepoint",
    "meu_modulo",
    "portfolio",
    "levar_arquivos_sharepoint",
]

# Deployment semanal
weekly_deployment = Deployment.build_from_flow(
    flow=main_pipeline_flow,
    name="Pipeline SRInfo - Semanal",
    parameters={
        "selected_modules": weekly_modules,
        "gerar_snapshot": True,
        "enviar_wpp": True,
        "enviar_teams": True,
    },
    schedule=WEEKLY_MONDAY_SCHEDULE,
    tags=["embrapii", "srinfo", "semanal"],
    description="Pipeline semanal executado às segundas-feiras",
)

if __name__ == "__main__":
    weekly_deployment.apply()
    print("Deployment semanal criado com sucesso!")
```

3. Atualize o arquivo `prefect.yaml` para incluir o novo deployment:

```yaml
deployments:
  # ... deployments existentes ...

  - name: pipeline-srinfo-semanal
    entrypoint: deployments/weekly_deployment.py:weekly_deployment
    work_pool:
      name: default-agent-pool
      work_queue_name: default
    schedule:
      cron: "0 7 * * 1"
      timezone: "America/Sao_Paulo"
    tags:
      - embrapii
      - srinfo
      - semanal
```

### Adicionando Módulos a Agendamentos Existentes

Para adicionar um novo módulo a um agendamento existente, edite o arquivo de deployment correspondente:

```python
# deployments/main_deployment.py

# Módulos para execução diária (dias de semana)
daily_modules = [
    # ... módulos existentes ...
    "meu_modulo",  # Adicionar o novo módulo
    # ... outros módulos ...
]
```

## Framework Prefect

O [Prefect](https://www.prefect.io/) é um framework de orquestração de fluxos de trabalho que permite automatizar, monitorar e gerenciar pipelines de dados. Neste projeto, utilizamos o Prefect 2.x para orquestrar o pipeline de ETL.

### Conceitos Principais

1. **Task**: Unidade básica de trabalho, representada por uma função Python decorada com `@task`. Tasks podem ter configurações como número de tentativas, atrasos entre tentativas, e timeout.

2. **Flow**: Coleção de tasks organizadas em um fluxo de trabalho, representada por uma função Python decorada com `@flow`. Flows podem chamar outros flows, criando uma hierarquia.

3. **Deployment**: Configuração que define como um flow deve ser executado, incluindo agendamento, parâmetros e tags.

4. **Agent**: Processo que executa flows agendados em um work pool.

5. **Work Pool**: Grupo de recursos computacionais onde os flows são executados.

### Estrutura de Flows no Projeto

No orquestrador, os flows são organizados hierarquicamente:

- `main_pipeline_flow`: Flow principal que orquestra todo o pipeline
  - Flows secundários por domínio (empresa, projeto, etc.)
    - Tasks específicas para cada operação

Esta estrutura permite:

- Execução modular (apenas partes específicas do pipeline)
- Reutilização de código
- Melhor organização e manutenção

## Monitoramento

O monitoramento do pipeline é realizado através de:

1. **Interface do Prefect**: Acesse a interface web do Prefect para visualizar o status dos flows, logs e métricas.

2. **Logs**: Os logs são gerados durante a execução e podem ser consultados na interface do Prefect ou nos arquivos de log.

3. **Notificações**:

   - **Microsoft Teams**: Notificações são enviadas para um canal do Teams ao final da execução
   - **WhatsApp**: Notificações podem ser enviadas via WhatsApp (opcional)

4. **Health Checks**: O módulo `monitoring/health_check.py` implementa verificações de saúde do sistema.

5. **Alertas**: O módulo `monitoring/alerts.py` implementa um sistema de alertas para notificar sobre problemas.

## Contribuição

Para contribuir com o projeto:

1. Crie um branch para sua feature ou correção
2. Implemente as mudanças seguindo as convenções do projeto
3. Adicione testes para suas mudanças
4. Envie um pull request

## Licença

Este projeto é propriedade da EMBRAPII e seu uso é restrito conforme os termos estabelecidos pela organização.
