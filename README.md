# Instruções de Instalação e Configuração do Orquestrador

## Pré-requisitos

- Python 3.8 ou superior

## Passos de Instalação

1. **Instalar os requisitos do projeto**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar as variáveis de ambiente**:

   Copie o arquivo `.env.example` para `.env` e preencha com as configurações necessárias.

   ```bash
   cp .env.example .env
   ```

## Execução do Orquestrador

O orquestrador pode ser executado de duas formas:

1. **Execução completa** - Usando o script `run_daily.bat`:

   ```bash
   run_daily.bat
   ```

   Este script executa todos os módulos em sequência e registra os logs detalhados.

2. **Execução básica** - Usando o script `execute.bat`:

   ```bash
   execute.bat
   ```

   Este script realiza uma verificação básica dos componentes sem executar os módulos.

## Uso e Monitoramento

- Os logs de execução são armazenados no diretório `logs`.
- Você pode verificar os logs para monitorar o status das execuções.
- Notificações são enviadas via Microsoft Teams após cada execução.

## Sistema de Logs JSON

O orquestrador inclui um sistema de logs em formato JSON que registra detalhadamente a execução dos três módulos principais:

1. `orchestrator_embrapii_srinfo`
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

- Verifique os logs para identificar possíveis erros.
- Certifique-se de que os caminhos para os scripts estão corretos.
- Para problemas específicos com os módulos, consulte os logs JSON para obter informações detalhadas sobre a execução.
