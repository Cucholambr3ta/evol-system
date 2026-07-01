"""Pantalla Memory — consolidación y drawers EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Vertical, Horizontal
from .base import BaseScreen
from ..data.mock_data import MEMORY_DRAWERS

TIER_COLORS = {
    "raw":        "dim",
    "memory":     "cyan",
    "knowledge":  "green",
    "compressed": "yellow",
}

CONSOLIDATION_BAR = """\
  [bold]Niveles de consolidación:[/bold]

  RAW        [red]████[/red][dim]░░░░░░░░░░░░░░░░[/dim]  14 items
  MEMORY     [cyan]████████████[/cyan][dim]░░░░░░░░[/dim]  73 items
  KNOWLEDGE  [green]██████████[/green][dim]░░░░░░░░░░[/dim]  62 items
  COMPRESSED [yellow]████[/yellow][dim]░░░░░░░░░░░░░░░░[/dim]  21 items
"""


class MemoryScreen(BaseScreen):
    """Pantalla de memoria persistente y drawers."""

    SCREEN_ID = "5"

    DEFAULT_CSS = """
    MemoryScreen {
        layout: vertical;
        padding: 1;
    }
    #mem-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #mem-stats {
        height: 1;
        margin-bottom: 1;
    }
    #mem-cols {
        height: 1fr;
    }
    #mem-table {
        width: 2fr;
        border: solid $primary-darken-2;
        margin-right: 1;
    }
    #mem-consolidation {
        width: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        total_items = sum(d["items"] for d in MEMORY_DRAWERS)
        total_vectors = sum(d["vectors"] for d in MEMORY_DRAWERS)
        yield Static("[bold]EVOL-DD · Memoria[/bold]", id="mem-title")
        yield Static(
            f"  [dim]{total_items} items totales · {total_vectors} vectores · "
            f"{len(MEMORY_DRAWERS)} drawers[/dim]",
            id="mem-stats",
        )
        with Horizontal(id="mem-cols"):
            table = DataTable(id="mem-table")
            yield table
            yield Static(CONSOLIDATION_BAR, id="mem-consolidation")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Drawer", "Items", "Tier", "Vectores")
        for drawer in MEMORY_DRAWERS:
            tier = drawer["tier"]
            color = TIER_COLORS.get(tier, "white")
            table.add_row(
                drawer["id"],
                str(drawer["items"]),
                f"[{color}]{tier}[/{color}]",
                str(drawer["vectors"]),
            )
