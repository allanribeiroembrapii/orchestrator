# Pipeline Sebrae UFs

Este diretório contém um pipeline automatizado para processamento e integração de dados do Sebrae UFs com o SharePoint, facilitando a geração e upload de planilhas processadas.

## Objetivo

Automatizar o fluxo de:
1. Download de arquivos do SharePoint
2. Geração de planilha geral consolidada
3. Processamento do banco de dados `BD_portfolio`
4. Upload do resultado processado de volta ao SharePoint

## Estrutura

- `main.py`: Script principal que executa o pipeline completo.
- `scripts/`: Funções auxiliares para busca de arquivos e geração de planilhas.
- `office365_api/`: Funções para integração com o SharePoint (upload de arquivos).
- `.env.example`: Exemplo de configuração das variáveis de ambiente necessárias.

## Pré-requisitos

- Python 3.8+
- Instalar as dependências listadas no `requirements.txt` da raiz do projeto:
  ```
  pip install -r requirements.txt
  ```

## Configuração

1. Copie o arquivo `.env.example` para `.env`:
   ```
   cp .env.example .env
   ```
2. Edite o arquivo `.env` e preencha com seus dados:
   - `ROOT`: Caminho raiz dos dados do pipeline
   - `sharepoint_email`: Seu e-mail de acesso ao SharePoint
   - `sharepoint_password`: Sua senha do SharePoint
   - `sharepoint_url_site`: URL do site SharePoint
   - `sharepoint_site_name`: Nome do site SharePoint
   - `sharepoint_doc_library`: Nome da biblioteca de documentos

## Execução

No terminal, execute o script principal:
```
python main.py
```

O pipeline executa as seguintes etapas:
1. **Busca arquivos do SharePoint**: Baixa os arquivos necessários.
2. **Gera planilha geral**: Consolida os dados em uma planilha.
3. **Processa BD_portfolio**: Realiza o processamento dos dados.
4. **Upload para SharePoint**: Envia o resultado processado para a pasta `DWPII/sebrae_ufs` no SharePoint.

## Observações

- Certifique-se de que as credenciais do SharePoint estejam corretas e tenham permissão de leitura e escrita.
- O caminho definido em `ROOT` deve existir e ser acessível pelo script.
- Para dúvidas sobre as funções auxiliares, consulte os scripts em `scripts/` e `office365_api/`.

---
