# Instruções de Instalação e Configuração do Orquestrador

## Pré-requisitos

- Python 3.8 ou superior
- Prefect 2.x instalado

## Passos de Instalação

1. **Instalar o Prefect**:

   ```bash
   pip install prefect>=2.13.0
   ```

2. **Iniciar o servidor Prefect**:

   ```bash
   prefect server start
   ```

3. **Instalar os requisitos adicionais do projeto**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar os deployments**:
   ```bash
   python deployments_config.py
   ```

## Configuração para inicialização automática no Windows

1. Pressione `Win + R` e digite `shell:startup` para abrir a pasta de inicialização do Windows.

2. Copie o arquivo `iniciar_prefect.bat` para esta pasta ou crie um atalho para este arquivo nesta pasta.

3. O Prefect agent agora iniciará automaticamente quando você fizer login no Windows.

## Verificação da Instalação

1. Verifique se os deployments foram criados com sucesso:

   ```bash
   prefect deployment ls
   ```

2. Execute manualmente o flow para testar:
   ```bash
   python orchestrator_flow.py
   ```

## Uso e Monitoramento

- Acesse a interface do Prefect em `http://localhost:4200` para monitorar as execuções.
- Você pode verificar os logs das execuções e o status dos flows.
- Para modificar os agendamentos, edite o arquivo `deployments_config.py` e execute-o novamente.

## Sistema de Logs JSON

O orquestrador agora inclui um sistema de logs em formato JSON que registra detalhadamente a execução dos três módulos principais:

1. `pipeline_embrapii_srinfo`
2. `atualizar_google_sheets`
3. `api_datapii`

### Características do Sistema de Logs

- **Logs Consolidados**: Todos os logs são armazenados em um único arquivo JSON por dia de execução.
- **Estrutura Hierárquica**: Os logs são organizados em uma estrutura hierárquica que facilita a análise.
- **Rastreamento de Erros**: Em caso de falha, o sistema registra informações detalhadas sobre o erro.
- **Métricas de Tempo**: O sistema registra o tempo de início, fim e duração de cada módulo e da execução completa.

### Localização dos Logs

Os logs são armazenados no diretório `logs` com o formato `orchestrator_YYYYMMDD.json`, onde `YYYYMMDD` é a data da execução.

### Visualização dos Logs

Para visualizar os logs, você pode usar qualquer editor de texto ou ferramenta que suporte JSON. Recomendamos o uso do VSCode ou de ferramentas específicas para visualização de JSON.

Para mais detalhes sobre o sistema de logs, consulte o arquivo [logs/README.md](logs/README.md).

## Solução de Problemas

- Se o script não iniciar automaticamente, verifique se o Prefect server está em execução.
- Verifique os logs do Prefect para identificar possíveis erros.
- Certifique-se de que os caminhos para os scripts estão corretos em `orchestrator_flow.py`.
- Para problemas específicos com os módulos, consulte os logs JSON para obter informações detalhadas sobre a execução.
