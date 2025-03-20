"""
Configurações centralizadas para todos os módulos do sistema.
Cada módulo tem suas configurações específicas definidas aqui.
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ROOT = os.getenv("ROOT")

# Configurações para cada módulo
CONFIGS = {
    "google_sheets": {
        "url": "https://docs.google.com/spreadsheets/d/1x7IUvZnXg2MH2k3QE9Kiq-_Db4eA-2xwFGuswbTDYjg/edit?usp=sharing",
        "caminhos_arquivos": {
            "raw_portfolio": os.path.join(
                ROOT, "core", "projeto", "portfolio", "step_3_data_processed", "portfolio.xlsx"
            ),
            "raw_projetos_empresas": os.path.join(
                ROOT,
                "core",
                "projeto",
                "projetos_empresas",
                "step_3_data_processed",
                "projetos_empresas.xlsx",
            ),
            "raw_informacoes_empresas": os.path.join(
                ROOT,
                "core",
                "empresa",
                "info_empresas",
                "step_3_data_processed",
                "informacoes_empresas.xlsx",
            ),
            "raw_info_unidades_embrapii": os.path.join(
                ROOT,
                "core",
                "unidade_embrapii",
                "info_unidades",
                "step_3_data_processed",
                "info_unidades_embrapii.xlsx",
            ),
            "raw_ue_linhas_atuacao": os.path.join(
                ROOT,
                "core",
                "unidade_embrapii",
                "info_unidades",
                "step_3_data_processed",
                "ue_linhas_atuacao.xlsx",
            ),
            "raw_macroentregas": os.path.join(
                ROOT,
                "core",
                "projeto",
                "macroentregas",
                "step_3_data_processed",
                "macroentregas.xlsx",
            ),
            "raw_negociacoes_negociacoes": os.path.join(
                ROOT,
                "core",
                "negociacoes",
                "negociacoes",
                "step_3_data_processed",
                "negociacoes_negociacoes.xlsx",
            ),
            "raw_classificacao_projetos": os.path.join(
                ROOT,
                "core",
                "projeto",
                "classificacao_projeto",
                "step_3_data_processed",
                "classificacao_projeto.xlsx",
            ),
            "raw_projetos": os.path.join(
                ROOT, "core", "projeto", "projetos", "step_3_data_processed", "projetos.xlsx"
            ),
            "raw_prospeccao_prospeccao": os.path.join(
                ROOT,
                "core",
                "prospeccao",
                "prospeccao",
                "step_3_data_processed",
                "prospeccao_prospeccao.xlsx",
            ),
            "raw_cnae_ibge": os.path.join(ROOT, "core", "lookup_tables", "cnae_ibge.xlsx"),
        },
    },
    "info_empresas": {
        "link": "https://srinfo.embrapii.org.br/company/list/",
        "nome_arquivo": "info_empresas",
        "caminhos": {
            "current_dir": os.path.abspath(os.path.join(ROOT, "empresa", "info_empresas")),
            "step_1_data_raw": os.path.abspath(
                os.path.join(ROOT, "empresa", "info_empresas", "step_1_data_raw")
            ),
            "step_2_stage_area": os.path.abspath(
                os.path.join(ROOT, "empresa", "info_empresas", "step_2_stage_area")
            ),
            "step_3_data_processed": os.path.abspath(
                os.path.join(ROOT, "empresa", "info_empresas", "step_3_data_processed")
            ),
        },
        "campos_interesse": [
            "CNPJ",
            "Situação",
            "Status",
            "Tipo",
            "Natureza legal",
            "Data de abertura",
            "Nome da empresa",
            "Nome fantasia",
            "CNAE",
            "Atribuição",
            "Estado",
            "Município",
            "CEP",
            "Bairro",
            "Logradouro",
            "Número",
            "Complemento",
            "E-mail",
            "Pessoa Responsável",
            "Situação Especial",
            "Motivo para a situação",
            "Data da Situação Especial",
        ],
        "novos_nomes_e_ordem": {
            "CNPJ": "cnpj",
            "Situação": "situacao_cnpj",
            "Status": "status",
            "Tipo": "hierarquia",
            "Natureza legal": "natureza_legal",
            "Data de abertura": "data_abertura",
            "Nome da empresa": "razao_social",
            "Nome fantasia": "nome_fantasia",
            "CNAE": "cnae_principal",
            "Atribuição": "cnae_descricao",
            "Estado": "endereco_uf",
            "Município": "endereco_municipio",
            "CEP": "endereco_cep",
            "Bairro": "endereco_bairro",
            "Logradouro": "endereco_logradouro",
            "Número": "endereco_numero",
            "Complemento": "endereco_complemento",
            "E-mail": "contato_email",
            "Pessoa Responsável": "pessoa_responsavel",
            "Situação Especial": "recuperacao_judicial",
            "Motivo para a situação": "recuperacao_judicial_motivo",
            "Data da Situação Especial": "recuperacao_judicial_data",
        },
    },
    "cg_classificacao_projetos": {
        "sharepoint": {
            "site": os.getenv("sharepoint_url_site"),
            "site_name": os.getenv("sharepoint_site_name"),
            "doc_library": os.getenv("sharepoint_doc_library"),
        },
        "caminhos": {
            "current_dir": os.path.abspath(os.path.join(ROOT, "cg_classificacao_projetos")),
            "step_1_data_raw": os.path.abspath(
                os.path.join(ROOT, "cg_classificacao_projetos", "step_1_data_raw")
            ),
            "step_2_stage_area": os.path.abspath(
                os.path.join(ROOT, "cg_classificacao_projetos", "step_2_stage_area")
            ),
            "step_3_data_processed": os.path.abspath(
                os.path.join(ROOT, "cg_classificacao_projetos", "step_3_data_processed")
            ),
        },
        "arquivos": {
            "portfolio": "portfolio.xlsx",
            "classificacao_projeto": "classificacao_projeto.xlsx",
            "cg_classificacao_projetos": "CG_Classificação de Projetos.xlsx",
            "ue_fonte_prioritario": "ue_fonte_recurso_prioritario.xlsx",
        },
    },
    # Adicione configurações para outros módulos conforme necessário
}


def get_config(module_name):
    """
    Obtém a configuração para um módulo específico.

    Args:
        module_name: Nome do módulo para obter a configuração

    Returns:
        dict: Configuração do módulo ou None se não encontrado
    """
    return CONFIGS.get(module_name)
