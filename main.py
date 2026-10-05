"""
Ponto de entrada do projeto Motonomads Redatores.
Suporta execução direta via CLI interativa ou via parâmetros de linha de comando.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import MotonomadsOrchestrator
from cli import main_menu


def main():
    parser = argparse.ArgumentParser(description="Motonomads Redatores — Editorial Engine")
    parser.add_argument("--source", "-s", type=str, help="URL de artigo já publicado ou caminho de arquivo local (.md/.txt)")
    parser.add_argument("--pillar", "-p", type=str, default="mototurismo", choices=["mototurismo", "offroad_4x4", "aventura_outdoor", "turismo_cultura"], help="Pilar temático especialista")
    parser.add_argument("--keyword", "-k", type=str, default="", help="Palavra-chave foco para SEO e GEO")

    args = parser.parse_args()

    if args.source:
        orchestrator = MotonomadsOrchestrator(base_dir=os.path.dirname(os.path.abspath(__file__)))
        print(f"\n[Motonomads] Iniciando processamento de: {args.source}")
        print(f"[Motonomads] Pilar: {args.pillar} | Palavra-chave: {args.keyword or 'N/A'}\n")

        result = orchestrator.run_pipeline(
            source=args.source,
            pillar=args.pillar,
            target_keyword=args.keyword,
        )

        if result.get("status") == "error":
            print(f"\n❌ Erro: {result.get('error')}")
            sys.exit(1)
        else:
            print("\n" + "=" * 60)
            print("✅ MATÉRIA GERADA E AUDITADA COM SUCESSO!")
            print(f"📄 Artigo: {result['article_file']}")
            print(f"📋 Auditoria: {result['audit_file']}")
            print(f"🌐 Painel Visual HTML: {result['html_file']}")
            print(f"Score Tom de Voz: {result['local_tone_score']}/100")
            print(f"Score GEO/SEO: {result['local_geo_score']}/100")
            print("=" * 60)
    else:
        # Se nenhum argumento for passado, abre a CLI interativa
        main_menu()


if __name__ == "__main__":
    main()
