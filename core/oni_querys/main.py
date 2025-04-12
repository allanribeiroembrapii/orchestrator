import os
import inspect
from start_clean import start_clean
from connection.copy_sharepoint import copy_sharepoint
from querys.companies.main_companies import main_companies
from connection.up_sharepoint import up_sharepoint


def verificar_criar_pastas():
    """
    Verifica e cria as pastas necessárias para o funcionamento do pipeline.
    Evita erros de FileNotFoundError ao tentar acessar pastas que não existem.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Lista de diretórios base que precisam ter a estrutura padrão
    # Nota: Não incluímos "./data" aqui porque o start_clean() já cuida dessa pasta
    diretorios_base = [
        # Diretórios de projeto
        os.path.abspath("./projeto/sebrae"),
        os.path.abspath("./projeto/contratos"),
        os.path.abspath("./projeto/projetos"),
        os.path.abspath("./projeto/projetos_empresas"),
        os.path.abspath("./projeto/estudantes"),
        os.path.abspath("./projeto/pedidos_pi"),
        os.path.abspath("./projeto/macroentregas"),
        os.path.abspath("./projeto/portfolio"),
        os.path.abspath("./projeto/classificacao_projeto"),
        # Diretórios de análises e relatórios
        os.path.abspath("./analises_relatorios/empresas_contratantes"),
        os.path.abspath("./analises_relatorios/projetos_contratados"),
        # Diretórios de unidades
        os.path.abspath("./unidade_embrapii/equipe_ue"),
        os.path.abspath("./unidade_embrapii/info_unidades"),
        os.path.abspath("./unidade_embrapii/plano_acao"),
        os.path.abspath("./unidade_embrapii/termos_cooperacao"),
        os.path.abspath("./unidade_embrapii/plano_metas"),
        # Diretórios de prospecção
        os.path.abspath("./prospeccao/comunicacao"),
        os.path.abspath("./prospeccao/eventos_srinfo"),
        os.path.abspath("./prospeccao/prospeccao"),
        # Diretórios de negociações
        os.path.abspath("./negociacoes/negociacoes"),
        os.path.abspath("./negociacoes/planos_trabalho"),
        os.path.abspath("./negociacoes/propostas_tecnicas"),
        # Diretórios de empresa
        os.path.abspath("./empresa/info_empresas"),
    ]

    # Subpastas padrão que devem existir em cada diretório base
    subpastas = ["step_1_data_raw", "step_2_stage_area", "step_3_data_processed"]

    # Verifica e cria cada diretório base com suas subpastas
    for diretorio in diretorios_base:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio, exist_ok=True)
            print(f"  ✓ Criado diretório base: {diretorio}")

        # Cria as subpastas dentro do diretório base
        for subpasta in subpastas:
            caminho_completo = os.path.join(diretorio, subpasta)
            if not os.path.exists(caminho_completo):
                os.makedirs(caminho_completo, exist_ok=True)
                print(f"  ✓ Criada subpasta: {caminho_completo}")

    print("🟢 " + inspect.currentframe().f_code.co_name)


def oni_querys():
    # Verificar e criar pastas necessárias
    verificar_criar_pastas()

    # Start clean
    start_clean()

    # Buscar empresas no Sharepoint
    copy_sharepoint()

    # Executar querys
    main_companies()

    # Levar dados para o Sharepoint
    up_sharepoint()


if __name__ == "__main__":
    oni_querys()
