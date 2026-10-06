"""
CLI Interativa Moderna do Time Editorial Motonomads Redatores.
Permite selecionar artigos base (URL ou arquivo), escolher o pilar especialista e acompanhar a redação em tempo real.
"""

import os
import sys
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import MotonomadsOrchestrator


if HAS_RICH:
    console = Console()
else:
    class DummyConsole:
        def print(self, *args, **kwargs):
            text = " ".join(str(a) for a in args)
            for tag in ["[bold orange1]", "[/bold orange1]", "[bold cyan]", "[/bold cyan]",
                        "[bold yellow]", "[/bold yellow]", "[bold green]", "[/bold green]",
                        "[bold white]", "[/bold white]", "[bold red]", "[/bold red]",
                        "[cyan]", "[/cyan]", "[yellow]", "[/yellow]", "[green]", "[/green]", "[red]", "[/red]", "[dim]", "[/dim]"]:
                text = text.replace(tag, "")
            print(text)

        def status(self, *args, **kwargs):
            from contextlib import nullcontext
            return nullcontext()

    class DummyPrompt:
        @staticmethod
        def ask(prompt_text, choices=None, default=None):
            clean_prompt = prompt_text
            for tag in ["[bold cyan]", "[/bold cyan]", "[bold yellow]", "[/bold yellow]", "[bold white]", "[/bold white]"]:
                clean_prompt = clean_prompt.replace(tag, "")
            msg = f"{clean_prompt} "
            if choices:
                msg += f"({', '.join(choices)}) "
            if default:
                msg += f"[{default}]: "
            else:
                msg += ": "
            val = input(msg).strip()
            return val if val else (default or "")

    class DummyTable:
        def __init__(self, title="", **kwargs):
            self.title = title
            self.rows = []
        def add_column(self, *args, **kwargs): pass
        def add_row(self, *args): self.rows.append(args)
        def __str__(self):
            lines = [f"\n--- {self.title} ---"]
            for r in self.rows:
                lines.append(" | ".join(str(x) for x in r))
            return "\n".join(lines)

    class DummyPanel:
        def __init__(self, content, title="", subtitle="", **kwargs):
            self.content = content
            self.title = title
            self.subtitle = subtitle
        def __str__(self):
            return f"\n=== {self.title} ===\n{self.content}\n=== {self.subtitle} ==="

    console = DummyConsole()
    Prompt = DummyPrompt()
    Table = DummyTable
    Panel = DummyPanel


def show_banner():
    banner_text = """
 [bold orange1]__  __       _                                 _     [/bold orange1]
[bold orange1]|  \\/  | ___ | |_ ___  _ __   ___  _ __ ___   __ _  __| |___ [/bold orange1]
[bold orange1]| |\\/| |/ _ \\| __/ _ \\| '_ \\ / _ \\| '_ ` _ \\ / _` |/ _` / __|[/bold orange1]
[bold orange1]| |  | | (_) | || (_) | | | | (_) | | | | | | (_| | (_| \\__ \\[/bold orange1]
[bold orange1]|_|  |_|\\___/ \\__\\___/|_| |_|\\___/|_| |_| |_|\\__,_|\\__,_|___/[/bold orange1]
 [bold cyan]SQUAD DE REDAÇÃO & ENRIQUECIMENTO JORNALÍSTICO (GEO & SEO)[/bold cyan]
    """
    console.print(Panel(banner_text, border_style="orange1", subtitle="[green]v1.0.0 — Standalone Editorial Engine[/green]"))


def show_pillars_table():
    table = Table(title="[bold yellow]Pilares Especialistas Motonomads[/bold yellow]", border_style="cyan")
    table.add_column("Opção", justify="center", style="bold green", width=8)
    table.add_column("Pilar Editorial", style="bold white", width=22)
    table.add_column("Especialista Responsável", style="magenta", width=24)
    table.add_column("Foco & Habilidades", style="dim", width=42)

    table.add_row(
        "1",
        "Mototurismo 🏍️",
        "Rodrigo Mototurismo",
        "Pilotagem em duas rodas, Big Trail, curvas, autonomia e equipamentos CE.",
    )
    table.add_row(
        "2",
        "4x4 & Overlanding 🚙",
        "Bruno Off-Road",
        "Tração reduzida (4L), bloqueio, calibragem PSI, resgate e camping de teto.",
    )
    table.add_row(
        "3",
        "Aventura & Outdoor 🧗",
        "Clara Aventura",
        "Trekking, travessias em parques, altimetria, conduta Leave No Trace.",
    )
    table.add_row(
        "4",
        "Turismo & Destinos 🗺️",
        "Lucas Turismo",
        "Cidades-base, gastronomia regional, temporadas de visitação e logística.",
    )
    console.print(table)


def main_menu():
    show_banner()
    orchestrator = MotonomadsOrchestrator(base_dir=os.path.dirname(os.path.abspath(__file__)))

    while True:
        console.print("\n[bold cyan]Menu Principal:[/bold cyan]")
        console.print("1. [bold white]Processar nova matéria (URL ou arquivo local)[/bold white]")
        console.print("2. [bold white]Ver Tabela de Tom de Voz da Marca[/bold white]")
        console.print("3. [bold white]Ver Normas de Publicação GEO e SEO[/bold white]")
        console.print("4. [bold white]Listar matérias geradas na pasta output/[/bold white]")
        console.print("5. [bold red]Sair[/bold red]")

        choice = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            console.print("\n[bold yellow]─── Iniciar Produção de Matéria ───[/bold yellow]")
            source = Prompt.ask("Digite a [bold cyan]URL do artigo já publicado[/bold cyan] ou o [bold cyan]caminho do arquivo local[/bold cyan]")

            show_pillars_table()
            pilar_opt = Prompt.ask("Selecione o Pilar Especialista", choices=["1", "2", "3", "4"], default="1")
            pilar_map = {
                "1": "mototurismo",
                "2": "offroad_4x4",
                "3": "aventura_outdoor",
                "4": "turismo_cultura",
            }
            pillar = pilar_map[pilar_opt]

            keyword = Prompt.ask("Palavra-chave foco para SEO/GEO (opcional, pressione Enter para pular)", default="")

            console.print("\n[bold green]Iniciando pipeline dos agentes Motonomads...[/bold green]\n")

            with console.status("[bold green]Executando pipeline multi-agente...", spinner="dots"):
                result = orchestrator.run_pipeline(
                    source=source,
                    pillar=pillar,
                    target_keyword=keyword,
                    on_step_callback=lambda event: console.print(f"[bold cyan]>[/bold cyan] {event['message'] if isinstance(event, dict) else event}"),
                )

            if result.get("status") == "error":
                console.print(f"[bold red]❌ Erro:[/bold red] {result.get('error')}")
            else:
                console.print("\n" + "=" * 60)
                console.print("[bold green]✅ MATÉRIA PROCESSADA E AUDITADA COM SUCESSO![/bold green]")
                console.print(f"📄 [bold white]Artigo final salvo em:[/bold white] [cyan]{result['article_file']}[/cyan]")
                console.print(f"📋 [bold white]Auditoria salva em:[/bold white] [cyan]{result['audit_file']}[/cyan]")
                console.print(f"🌐 [bold white]Painel Visual HTML em:[/bold white] [bold green]{result['html_file']}[/bold green]")
                console.print(f"🏍️ [bold white]Especialista que redigiu:[/bold white] {result['specialist']}")
                console.print(f"📊 [bold white]Score Tom de Voz (algorítmico):[/bold white] [yellow]{result['local_tone_score']}/100[/yellow]")
                console.print(f"🎯 [bold white]Score GEO/SEO (algorítmico):[/bold white] [yellow]{result['local_geo_score']}/100[/yellow]")

                if result.get("local_findings"):
                    console.print("\n[bold yellow]Observações da Auditoria Técnica:[/bold yellow]")
                    for finding in result["local_findings"]:
                        console.print(f"  • {finding}")

        elif choice == "2":
            matrix_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/tone_matrix_reference.md")
            if os.path.exists(matrix_path):
                with open(matrix_path, "r", encoding="utf-8") as f:
                    console.print(Panel(f.read()[:2000] + "\n\n... (consulte o arquivo data/tone_matrix_reference.md para o texto na íntegra)", title="Matriz de Tom de Voz"))
            else:
                console.print("[red]Arquivo não encontrado.[/red]")

        elif choice == "3":
            geo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/geo_seo_standards.md")
            if os.path.exists(geo_path):
                with open(geo_path, "r", encoding="utf-8") as f:
                    console.print(Panel(f.read()[:2000] + "\n\n... (consulte o arquivo data/geo_seo_standards.md para o texto na íntegra)", title="Normas GEO & SEO"))
            else:
                console.print("[red]Arquivo não encontrado.[/red]")

        elif choice == "4":
            out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            files = [f for f in os.listdir(out_dir) if f.endswith(".md")]
            if not files:
                console.print("[yellow]Nenhum artigo gerado ainda na pasta output/.[/yellow]")
            else:
                console.print("[bold green]Arquivos gerados:[/bold green]")
                for f in files:
                    console.print(f"  • [cyan]{f}[/cyan]")

        elif choice == "5":
            console.print("[bold green]Até a próxima viagem! 🏍️💨[/bold green]")
            break


if __name__ == "__main__":
    main_menu()
