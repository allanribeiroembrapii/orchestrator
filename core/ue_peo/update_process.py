import pandas as pd
from datetime import datetime
import pytz
from core.ue_peo.config import Config
from core.office365_api.office365_api import SharePoint
from io import BytesIO
from pathlib import Path


def main():
    # 1. Configurar caminhos
    output_path = Config.OUTPUT_DIR / "dados_consolidados.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Garante que a pasta existe

    # 2. Carregar dados existentes ou inicializar DataFrame vazio
    if output_path.exists():
        df_existente = pd.read_excel(output_path)
        ultimo_id = df_existente["id"].max()
        print(
            f"🚩 Base existente carregada com {len(df_existente)} registros. Último ID: {ultimo_id}"
        )
    else:
        df_existente = pd.DataFrame()
        ultimo_id = 0
        print("🚩 Nenhum arquivo consolidado encontrado. Criando nova base.")

    # 3. Baixar e processar novos dados
    client = SharePoint()
    new_content = client.download_file(
        Config.SHAREPOINT_URL_SITE,
        Config.SHAREPOINT_SITE_NAME,
        Config.SHAREPOINT_DOC_LIBRARY,
        "classificacao_unidade.xlsx",
        "General/Lucas Pinheiro/classificacao_unidade",
    )
    df_novos = pd.read_excel(BytesIO(new_content))

    data_extracao = datetime.now(pytz.timezone("America/Sao_Paulo")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # 4. Preparar novos registros com IDs sequenciais
    novos_ids = range(ultimo_id + 1, ultimo_id + 1 + len(df_novos))
    df_processado = pd.DataFrame(
        {
            "id": novos_ids,
            "unidade_embrapii": df_novos["Unidade EMBRAPII"],
            "peo_classificacao": df_novos["Classificação Unidade"],
            "peo_aderiu": df_novos["Aderiu?"].map({True: "Sim", False: "Não"}),
            "data_extracao": data_extracao,
        }
    )
    print(
        f"🆕 {len(df_processado)} novos registros processados. Próximo ID: {novos_ids[-1] + 1}"
    )

    # 5. Consolidar e salvar
    df_final = pd.concat([df_existente, df_processado], ignore_index=True)

    # Ordenar colunas e salvar
    colunas = [
        "id",
        "unidade_embrapii",
        "peo_classificacao",
        "peo_aderiu",
        "data_extracao",
    ]
    df_final[colunas].to_excel(output_path, index=False)

    print(
        f"✅ Arquivo consolidado atualizado com sucesso! Total de registros: {len(df_final)}"
    )

    # 6. Upload para o SharePoint
    try:
        client = SharePoint()

        # Carregar arquivo local
        with open(output_path, "rb") as f:
            file_content = f.read()

        # Configurações dinâmicas
        target_folder = (
            Config.SHAREPOINT_OUTPUT_FOLDER
        )  # Ex: "General/Lucas Pinheiro/classificacao_unidade"
        target_file = Config.SHAREPOINT_OUTPUT_FILENAME  # Ex: "dados_consolidados.xlsx"

        # Verificar e apagar versão anterior
        if client.file_exists(target_folder, target_file):
            client.delete_file(target_folder, target_file)
            print(f"♻️ Arquivo anterior removido: {target_file}")

        # Fazer upload da nova versão com todos os parâmetros necessários
        new_file_url = client.upload_file(
            folder_name=target_folder,
            sharepoint_site=Config.SHAREPOINT_URL_SITE,
            sharepoint_site_name=Config.SHAREPOINT_SITE_NAME,
            sharepoint_doc=Config.SHAREPOINT_DOC_LIBRARY,
            file_name=target_file,
            content=file_content,
        )
        print(f"🚀 Upload concluído: {new_file_url}")

    except Exception as e:
        print(f"🔥 Erro crítico durante upload: {str(e)}")
        raise


if __name__ == "__main__":
    main()
