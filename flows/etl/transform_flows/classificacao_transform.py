from prefect import flow, task, get_run_logger
import os
import sys
from datetime import datetime

# Importar caminho raiz
sys.path.append(os.getenv('ROOT'))

@task(name="Criar Nova Classificação")
def nova_classificacao_task():
    """Task para criar nova classificação de projetos."""
    from projeto.classificacao_projeto.scripts.new_classificacao_projeto import new_classificacao_projeto
    return new_classificacao_projeto()

@task(name="Atualizar Classificação")
def atualizar_classificacao_task():
    """Task para atualizar classificação de projetos."""
    from projeto.classificacao_projeto.scripts.atualizacao_classificacao_projeto import atualizacao_classificao_projeto
    return atualizacao_classificao_projeto()

@flow(name="Transformação de Classificação de Projetos")
def classificacao_transform_flow():
    """Flow para transformar dados de classificação de projetos."""
    logger = get_run_logger()
    logger.info("Iniciando transformação de classificação de projetos")
    
    # Copiar arquivos necessários
    from scripts_public.copiar_e_renomear_arquivos import copiar_e_renomear_arquivos
    
    # Definir origens e destinos
    ROOT = os.getenv('ROOT')
    origens = {
        'projetos_contratados': os.path.join(ROOT, 'analises_relatorios', 'projetos_contratados', 'step_1_data_raw', 'raw_relatorio_projetos_contratados_1.xlsx'),
        'projetos_empresas': os.path.join(ROOT, 'projeto', 'projetos_empresas', 'step_3_data_processed', 'projetos_empresas.xlsx'),
        # [...]
    }
    destino = os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_1_data_raw')
    renomeios = {
        'projetos_contratados': 'raw_projetos_contratados.xlsx',
        # [...]
    }
    
    # Executar cópia
    copiar_e_renomear_arquivos(origens, destino, renomeios)
    
    # Processamento
    nova_classificacao_task()
    atualizar_classificacao_task()
    
    # Copiar resultado para DWPII
    from scripts_public.copiar_arquivos_finalizados_para_dwpii import copiar_arquivos_finalizados_para_dwpii
    copiar_arquivos_finalizados_para_dwpii(os.path.join(ROOT, 'projeto', 'classificacao_projeto', 'step_3_data_processed'))
    
    return {"status": "success", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    # Permite executar este flow individualmente para testes
    classificacao_transform_flow()