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

## Solução de Problemas

- Se o script não iniciar automaticamente, verifique se o Prefect server está em execução.
- Verifique os logs do Prefect para identificar possíveis erros.
- Certifique-se de que os caminhos para os scripts estão corretos em `orchestrator_flow.py`.
