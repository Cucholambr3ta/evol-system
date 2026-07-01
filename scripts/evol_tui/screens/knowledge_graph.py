"""Pantalla Knowledge Graph — grafo de conocimiento EVOL-DD TUI.

Intenta renderizar un grafo real con netext + networkx. Si esas
dependencias no están disponibles, recurre a un dibujo ASCII estático.
"""
from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from .base import BaseScreen
from ..data.mock_data import PROJECTS, SKILLS

try:
    import networkx as nx
    from netext import ConsoleGraph
    NETEXT_AVAILABLE = True
except ImportError:
    nx = None
    ConsoleGraph = None
    NETEXT_AVAILABLE = False

ASCII_GRAPH = """\
  ┌─────────────────────────────────────────────────────────────┐
  │                  [bold]Grafo de Conocimiento[/bold]                       │
  │                                                             │
  │    [cyan]SaaS Platform[/cyan]──────[yellow]auth-domain[/yellow]──────[cyan]API Gateway[/cyan]         │
  │         │                   │               │               │
  │    [green]SDD[/green]·[green]BDD[/green]·[green]DDD[/green]         [green]TDD[/green]·[green]SecDD[/green]       [green]ODD_API[/green]·[green]SLO[/green]      │
  │         │                   │               │               │
  │    [magenta]evol-builder[/magenta]         [magenta]evol-sec[/magenta]       [magenta]evol-architect[/magenta]   │
  │                                                             │
  │    [cyan]Payment Domain[/cyan]──────[yellow]Analytics[/yellow]                            │
  │         │                   │                               │
  │    [green]CCDD[/green]·[green]ESDD[/green]         [green]PDD[/green]·[green]EDA[/green]                           │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
"""

LEGEND = """\
  [bold]Leyenda:[/bold]
  [cyan]■[/cyan] Proyecto / hub de dominio    [yellow]■[/yellow] Módulo de dominio
  [green]■[/green] Disciplina activa            [magenta]■[/magenta] Agente asignado
"""


def _build_knowledge_graph():
    """Construye un DiGraph proyectos → skills relacionadas (muestra)."""
    graph = nx.DiGraph()
    sample_skills = SKILLS[:6]
    for proj in PROJECTS:
        graph.add_node(proj["id"], label=proj["name"], kind="project")
    for skill in sample_skills:
        graph.add_node(skill["id"], label=skill["id"], kind="skill")
    # enlaces de muestra: cada proyecto se conecta con 1-2 skills
    links = [
        (PROJECTS[0]["id"], sample_skills[0]["id"]),
        (PROJECTS[0]["id"], sample_skills[1]["id"]),
        (PROJECTS[1]["id"], sample_skills[2]["id"]),
        (PROJECTS[2]["id"], sample_skills[3]["id"]),
        (PROJECTS[3]["id"], sample_skills[4]["id"]),
        (PROJECTS[4]["id"], sample_skills[5]["id"]),
    ]
    for src, dst in links:
        if src in graph and dst in graph:
            graph.add_edge(src, dst)
    return graph


def _render_graph_to_text() -> Optional[str]:
    """Renderiza el grafo con netext a texto enriquecido. None si falla."""
    if not NETEXT_AVAILABLE:
        return None
    try:
        from rich.console import Console
        graph = _build_knowledge_graph()
        console_graph = ConsoleGraph(graph)
        console = Console(record=True, width=80)
        console.print(console_graph)
        return console.export_text(styles=True)
    except Exception:
        return None


class KnowledgeGraphScreen(BaseScreen):
    """Visualización del grafo de conocimiento (netext o ASCII fallback)."""

    SCREEN_ID = "3"

    DEFAULT_CSS = """
    KnowledgeGraphScreen {
        layout: vertical;
        padding: 1;
    }
    #kg-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #kg-stats {
        height: 1;
        margin-bottom: 1;
    }
    #kg-graph {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
        overflow-y: auto;
    }
    #kg-legend {
        height: 6;
        border: solid $primary-darken-2;
        padding: 1;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        project_count = len(PROJECTS)
        skill_count = len(SKILLS)
        engine = "netext" if NETEXT_AVAILABLE else "ASCII (fallback)"
        yield Static("[bold]EVOL-DD · Grafo de Conocimiento[/bold]", id="kg-title")
        yield Static(
            f"  [dim]{project_count} proyectos · {skill_count} skills · "
            f"31 disciplinas · motor: {engine}[/dim]",
            id="kg-stats",
        )
        rendered = _render_graph_to_text()
        graph_text = rendered if rendered is not None else ASCII_GRAPH
        yield Static(graph_text, id="kg-graph")
        yield Static(LEGEND, id="kg-legend")
