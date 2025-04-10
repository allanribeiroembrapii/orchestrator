# pipeline_embrapii_srinfo

## Objetivo

O **pipeline_embrapii_srinfo** tem como objetivo realizar a extração, transformação e carga de dados do SRInfo da Embrapii para o DWPII.

## Sequência lógica do script

1. **Faz uma cópia dos dados do DWPII**  
   Acessa a pasta do SharePoint e faz cópia dos arquivos atuais.

2. **Baixa os dados do SRInfo**  
   Acessa o SRInfo e baixa os dados das diferentes tabelas.

3. **Cria as tabelas normalizadas**  
   Processa os dados: retirada de dados redundantes, padronização do nome dos campos e das chaves primárias e secundárias e criação das tabelas normalizadas.

4. **Registra os logs**  
   Registra as operações realizadas em uma tabela de logs.

5. **Carrega os dados no DWPII backup**  
   Cria um arquivo .zip com as planilhas atuais que foram baixadas no início do script e salva em uma pasta específica do SharePoint.

6. **Carrega os dados no DWPII**  
   Carrega os novos arquivos processados na pasta do SharePoint.
   
7. **Envia mensagem no WhatsApp**  
   Encaminha mensagem com resumo da operação para o grupo do WhatsApp.

- Ver o `main_pipeline_srinfo.py`

## Como usar

1. Clone o repositório: `git clone https://github.com/allanribeiro91/pipeline_embrapii_srinfo.git`
2. `cd pipeline_embrapii_srinfo`
3. `virtualenv .venv`
4. `source .venv/bin/activate` (ou `.venv\Scripts\Activate` no Windows)
5. `pip install -r requirements.txt`
6. `python main_pipeline_srinfo.py`

## Requisito

- Criar o arquivo `.env`:

```env
USERNAME=<incluir o nome de usuário de acesso ao SRInfo>
PASSWORD=<incluir a senha de acesso ao SRInfo>

PASTA_DOWNLOAD=<incluir o caminho para a pasta downloads (onde os arquivos serão baixados)>
ROOT=<incluir o caminho da pasta root do projeto>

sharepoint_email=<incluir o email de acesso ao SharePoint>
sharepoint_password=<incluir a senha de acesso ao SharePoint>
sharepoint_url_site="https://embrapii.sharepoint.com/sites/GEEDD"
sharepoint_site_name="GEEDD"
sharepoint_doc_library="Documentos Compartilhados/"
