import pandas as pd

PLANO_METAS = 'unidade_embrapii\plano_metas\step_3_data_processed\plano_metas.xlsx'
IDS = 'unidade_embrapii\plano_metas\step_1_data_raw\ids_tabela_plano_metas.xlsx'

def join_ids_plano_metas():
    plano_metas = pd.read_excel(PLANO_METAS)
    ids = pd.read_excel(IDS)

    # Adicionar nova coluna 'id_plano_meta' em plano_metas
    plano_metas['id_plano_meta'] = ids['ID']

    # Salvar a nova versão de plano_metas no mesmo local da original
    plano_metas.to_excel(PLANO_METAS, index=False)
    print(f"Arquivo atualizado salvo em {PLANO_METAS}")