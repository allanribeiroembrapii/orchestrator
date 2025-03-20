#!/usr/bin/env python
"""
Script para executar o pipeline principal do orquestrador EMBRAPII SRInfo.

Exemplos de uso:
    # Executar com todos os módulos
    python run_pipeline.py

    # Executar com módulos específicos
    python run_pipeline.py --modules sharepoint info_empresas projetos

    # Executar com snapshot e notificação WhatsApp
    python run_pipeline.py --snapshot --whatsapp
"""

import argparse
import sys
from datetime import datetime

from flows.main_flow import main_pipeline_flow


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Executa o pipeline EMBRAPII SRInfo")

    parser.add_argument(
        "--modules",
        nargs="*",
        help="Lista de módulos a serem executados (se não especificado, executa todos)",
    )

    parser.add_argument(
        "--plano-metas",
        action="store_true",
        help="Executa o processamento do plano de metas",
    )

    parser.add_argument(
        "--snapshot", action="store_true", help="Gera snapshot ao final da execução"
    )

    parser.add_argument("--whatsapp", action="store_true", help="Envia notificação pelo WhatsApp")

    parser.add_argument(
        "--teams",
        action="store_true",
        default=True,
        help="Envia notificação pelo Microsoft Teams",
    )

    return parser.parse_args()


def main():
    """Função principal."""
    args = parse_args()

    print(f"Iniciando pipeline em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Executar o pipeline
    result = main_pipeline_flow(
        selected_modules=args.modules,
        plano_metas=args.plano_metas,
        gerar_snapshot=args.snapshot,
        enviar_wpp=args.whatsapp,
        enviar_teams=args.teams,
    )

    # Exibir resultados
    print("\nResultados:")
    print(f"Início: {result['inicio']}")
    print(f"Fim: {result['fim']}")
    print(f"Duração: {result['duracao']}")
    print(f"Novos projetos: {result['novos_projetos']}")
    print(f"Novas empresas: {result['novas_empresas']}")
    print(f"Projetos sem classificação: {result['projetos_sem_classificacao']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
