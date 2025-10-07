import os
import sys
import pandas as pd
from dotenv import load_dotenv

# carregar .env
load_dotenv()
# Carrega o .env da raiz do projeto para obter ROOT_PIPELINE
load_dotenv(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"
    )
)
ROOT = os.getenv("ROOT_PIPELINE")

# Definição dos caminhos
PATH_ROOT = os.path.abspath(os.path.join(ROOT))
SCRIPTS_PUBLIC_PATH = os.path.abspath(os.path.join(ROOT, "scripts_public"))
CURRENT_DIR = os.path.abspath(os.path.join(ROOT, "projeto", "funil"))
DIRETORIO_ARQUIVOS_FINALIZADOS = os.path.abspath(os.path.join(CURRENT_DIR, "step_3_data_processed"))

# Adicionar caminhos ao sys.path
sys.path.append(PATH_ROOT)

# Importar módulos necessários
from scripts_public.copiar_e_renomear_arquivos import copiar_e_renomear_arquivos
from scripts_public.copiar_arquivos_finalizados_para_dwpii import (
    copiar_arquivos_finalizados_para_dwpii,
)

origens = {
    "prospeccoes": os.path.join(
        ROOT, "prospeccao", "prospeccao", "step_3_data_processed", "prospeccao_prospeccao.xlsx"
    ),
    "negociacoes": os.path.join(
        ROOT, "negociacoes", "negociacoes", "step_3_data_processed", "negociacoes_negociacoes.xlsx",
    ),
    "contratos": os.path.join(
        ROOT, "projeto", "contratos", "step_3_data_processed", "contratos.xlsx"
    ),
}

# Define o caminho relativo da pasta de destino
destino = os.path.join(CURRENT_DIR, "step_1_data_raw")

# Renomeia os arquivos ao copiar
renomeios = {
    "prospeccoes": "prospeccao_prospeccao.xlsx",
    "negociacoes": "negociacoes_negociacoes.xlsx",
    "contratos": "contratos.xlsx",
}

def criar_funil():
    df_prospeccoes = pd.read_excel(origens["prospeccoes"])
    df_negociacoes = pd.read_excel(origens["negociacoes"]) 
    df_contratos = pd.read_excel(origens["contratos"])

    #Ajustar prospeccoes e propostas
    df_prospeccoes = df_prospeccoes[["unidade_embrapii", "data_prospeccao", "sera_feita_proposta"]]
    df_prospeccoes = df_prospeccoes.rename(columns={
        "unidade_embrapii": "unidade_embrapii",
        "data_prospeccao": "data",
        "sera_feita_proposta": "proposta"
    })
    df_prospeccoes["id"] = range(1, len(df_prospeccoes) + 1)
    df_prospeccoes = df_prospeccoes[["id"] + [col for col in df_prospeccoes.columns if col != "id"]]
    df_propostas = df_prospeccoes[df_prospeccoes["proposta"] == "Sim"]
    df_propostas = df_propostas.drop(columns=["proposta"])
    df_propostas['tipo'] = 'Proposta'
    df_prospeccoes = df_prospeccoes.drop(columns=["proposta"])
    df_prospeccoes['tipo'] = 'Prospecção'

    #Ajustar negociacoes
    df_negociacoes = df_negociacoes[["codigo_negociacao", "unidade_embrapii", "data_prim_ver_prop_tec"]]
    df_negociacoes = df_negociacoes.rename(columns={
        "codigo_negociacao": "id",
        "unidade_embrapii": "unidade_embrapii",
        "data_prim_ver_prop_tec": "data"
    })
    df_negociacoes["tipo"] = "Negociação"

    #Ajustar contratos
    df_contratos = df_contratos[["codigo_projeto", "unidade_embrapii", "data_contrato"]]
    df_contratos = df_contratos.rename(columns={
        "codigo_projeto": "id",
        "unidade_embrapii": "unidade_embrapii",
        "data_contrato": "data"
    })
    df_contratos["tipo"] = "Contrato"

    #Concatenar
    df_funil = pd.concat([df_prospeccoes, df_propostas, df_negociacoes, df_contratos], ignore_index=True)
    df_funil = df_funil[["id", "tipo", "unidade_embrapii", "data"]]
    df_funil = df_funil.sort_values(by=["data", "unidade_embrapii", "tipo"])

    #Salvar
    df_funil.to_excel(os.path.join(DIRETORIO_ARQUIVOS_FINALIZADOS, "funil.xlsx"), index=False)

def main_funil():
    copiar_e_renomear_arquivos(origens, destino, renomeios)
    criar_funil()
    copiar_arquivos_finalizados_para_dwpii(DIRETORIO_ARQUIVOS_FINALIZADOS)


if __name__ == "__main__":
    main_funil()
