"""Pantalla Dev Graph — grafo de desarrollo/código EVOL-DD TUI.

Intenta renderizar un grafo real con netext + networkx (módulos →
funciones). Si esas dependencias no están disponibles, recurre a un
dibujo ASCII estático.
"""
from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from .base import BaseScreen

try:
    import networkx as nx
    from netext import ConsoleGraph
    NETEXT_AVAILABLE = True
except ImportError:
    nx = None
    ConsoleGraph = None
    NETEXT_AVAILABLE = False

DEV_ASCII = """\
  ┌────────────────────────────────────────────────────────────────┐
  │                 [bold]Grafo de Desarrollo[/bold]                           │
  │                                                                │
  │  [cyan]evol-cli[/cyan]                                                     │
  │    ├── [yellow]src/evol_cli/[/yellow]                                          │
  │    │     ├── [green]__init__.py[/green]          [dim]entry point[/dim]              │
  │    │     ├── [green]agent/[/green]               [dim]workflows, prompts[/dim]       │
  │    │     ├── [green]scripts/[/green]             [dim]CLI tools[/dim]                │
  │    │     └── [green]skills/[/green]              [dim]skill catalog[/dim]            │
  │    ├── [yellow]scripts/[/yellow]                                                │
  │    │     ├── [green]evol-memory.py[/green]       [dim]memory store[/dim]             │
  │    │     ├── [green]evol-orchestrate.py[/green]  [dim]multi-agent[/dim]              │
  │    │     └── [green]evol_tui/[/green]            [dim]TUI EDMS ← aquí[/dim]          │
  │    ├── [yellow]prompts/agents/[/yellow]                                         │
  │    │     └── [green]registry.json[/green]        [dim]18 agentes núcleo[/dim]        │
  │    └── [yellow]acuerdos/memoria/[/yellow]                                      │
  │          └── [green]MEMORY.json[/green]          [dim]memoria persistente[/dim]      │
  │                                                                │
  │  [dim]Dependencias:[/dim]                                               │
  │    [magenta]textual[/magenta]>=0.80  [magenta]rich[/magenta]  [magenta]networkx[/magenta]>=3.0  [magenta]ladybugdb[/magenta]           │
  └────────────────────────────────────────────────────────────────┘
"""

CALL_GRAPH = """\
  [bold]Flujos de ejecución principales:[/bold]
  [cyan]evol build[/cyan] → evol-orchestrate → evol-builder → evol-qa → evol-sec
  [cyan]evol memory[/cyan] → evol-memory (LadybugDB / JSON fallback)
  [cyan]evol gate[/cyan]   → evol-gate (HMAC-SHA256)
  [cyan]evol tui[/cyan]    → evol_tui/__main__.py → EvolDDApp
"""

MODULES = [
    ("evol_cli", ["__init__", "agent", "scripts", "skills"]),
    ("scripts", ["evol-memory", "evol-orchestrate", "evol_tui"]),
    ("evol_tui", ["app", "navigation", "i18n"]),
]


def _build_dev_graph():
    """Construye un DiGraph módulos → funciones/submódulos (muestra)."""
    graph = nx.DiGraph()
    for module, children in MODULES:
        graph.add_node(module, label=module, kind="module")
        for child in children:
            node_id = "{0}.{1}".format(module, child)
            graph.add_node(node_id, label=child, kind="function")
            graph.add_edge(module, node_id)
    # enlace entre módulos para mostrar dependencia
    graph.add_edge("evol_cli", "scripts")
    graph.add_edge("scripts", "evol_tui")
    return graph


def _render_graph_to_text() -> Optional[str]:
    """Renderiza el grafo con netext a texto enriquecido. None si falla."""
    if not NETEXT_AVAILABLE:
        return None
    try:
        from rich.console import Console
        graph = _build_dev_graph()
        console_graph = ConsoleGraph(graph)
        console = Console(record=True, width=80)
        console.print(console_graph)
        return console.export_text(styles=True)
    except Exception:
        return None


class DevGraphScreen(BaseScreen):
    """Visualización del grafo de código del proyecto (netext o ASCII)."""

    SCREEN_ID = "4"

    DEFAULT_CSS = """
    DevGraphScreen {
        layout: vertical;
        padding: 1;
    }
    #dg-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #dg-graph {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
        overflow-y: auto;
    }
    #dg-flows {
        height: 8;
        border: solid $primary-darken-2;
        padding: 1;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        engine = "netext" if NETEXT_AVAILABLE else "ASCII (fallback)"
        yield Static("[bold]EVOL-DD · Grafo de Desarrollo[/bold]", id="dg-title")
        rendered = _render_graph_to_text()
        graph_text = rendered if rendered is not None else DEV_ASCII
        yield Static(
            "[dim]motor: {0}[/dim]\n{1}".format(engine, graph_text),
            id="dg-graph",
        )
        yield Static(CALL_GRAPH, id="dg-flows")
