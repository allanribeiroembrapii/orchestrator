# Sistema de Logs JSON para o Orquestrador EMBRAPII

Este diretório contém o sistema de logs em formato JSON para o Orquestrador EMBRAPII. O sistema registra a execução dos três módulos principais do orquestrador:

1. `orchestrator_embrapii_srinfo`
2. `atualizar_google_sheets`
3. `api_datapii`

## Estrutura dos Logs

Os logs são armazenados em arquivos JSON no formato `orchestrator_YYYYMMDD.json`, onde `YYYYMMDD` é a data da execução. Cada arquivo contém um registro de todas as execuções realizadas naquele dia.

A estrutura do arquivo JSON é a seguinte:

```json
{
  "executions": [
    {
      "execution_id": "20250413165012",
      "start_time": "2025-04-13T16:50:12",
      "end_time": "2025-04-13T17:30:45",
      "status": "success",
      "total_duration_seconds": 2433,
      "modules": [
        {
          "name": "orchestrator_embrapii_srinfo",
          "start_time": "2025-04-13T16:50:15",
          "end_time": "2025-04-13T17:10:22",
          "status": "success",
          "steps": [
            {
              "name": "verificar_criar_pastas",
              "time": "2025-04-13T16:50:16",
              "status": "success"
            }
            // Outros passos...
          ]
        }
        // Outros módulos...
      ]
    }
    // Outras execuções...
  ]
}
```

## Componentes do Sistema de Logs

### 1. `logs_handler.py`

Contém a classe `JsonLogger` que implementa a funcionalidade básica de logging em JSON.

### 2. `orchestrator_logs.py`

Implementa a classe `OrchestratorLogger` que gerencia os logs do orquestrador, consolidando os logs dos três módulos principais em um único arquivo JSON.

## Como Funciona

1. O script `run_daily.bat` inicializa o logger do orquestrador.
2. Cada módulo Python (`orchestrator_embrapii_srinfo`, `atualizar_google_sheets`, `api_datapii`) registra seu início, passos e conclusão no log.
3. O logger consolida todos os logs em um único arquivo JSON.
4. Em caso de erro, o logger registra informações detalhadas sobre o erro, incluindo o traceback.

## Vantagens do Sistema de Logs JSON

1. **Estruturado**: Os logs em formato JSON são estruturados, facilitando a análise e processamento automatizado.
2. **Consolidado**: Todos os logs são consolidados em um único arquivo, proporcionando uma visão completa da execução.
3. **Detalhado**: Cada passo da execução é registrado com timestamp, status e detalhes adicionais.
4. **Rastreável**: Em caso de erro, o sistema registra informações detalhadas para facilitar a depuração.

## Exemplo de Uso

Para visualizar os logs, você pode usar qualquer editor de texto ou ferramenta que suporte JSON. Recomendamos o uso do VSCode ou de ferramentas específicas para visualização de JSON, como o [JSON Viewer](https://jsonviewer.stack.hu/).

## Manutenção

Os arquivos de log são nomeados com a data da execução, facilitando a organização e limpeza. Recomenda-se implementar uma rotina de limpeza para remover logs antigos periodicamente.
