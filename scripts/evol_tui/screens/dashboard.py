"""Pantalla Dashboard — resumen general EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal, Vertical
from .base import BaseScreen
from ..data.mock_data import ACTIVITY_LOG, GATES, ANALYTICS


class DashboardScreen(BaseScreen):
    """Tablero general con métricas, actividad y gates."""

    SCREEN_ID = "1"

    DEFAULT_CSS = """
    DashboardScreen {
        layout: vertical;
        padding: 1;
    }
    #dash-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #dash-metrics {
        height: 6;
        margin-bottom: 1;
    }
    .metric-card {
        width: 1fr;
        height: 5;
        border: solid $primary-darken-2;
        padding: 0 1;
        margin: 0 1;
        content-align: center middle;
    }
    #dash-cols {
        height: 1fr;
    }
    #dash-activity {
        width: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
        margin-right: 1;
    }
    #dash-gates {
        width: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
    }
    .section-title {
        text-style: bold;
        color: $text-muted;
        margin-bottom: 1;
    }
    .activity-item {
        height: 1;
        margin-bottom: 0;
    }
    .gate-item {
        height: 1;
        margin-bottom: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]EVOL-DD · Tablero[/bold]", id="dash-title")
        with Horizontal(id="dash-metrics"):
            yield Static(
                "Proyectos\n[bold]24[/bold]\n[green]+2 este mes[/green]",
                classes="metric-card",
            )
            yield Static(
                "Agentes\n[bold]18[/bold]\n[dim]En ejecución[/dim]",
                classes="metric-card",
            )
            yield Static(
                "Gherkin\n[bold]184[/bold]\n[green]+12 sprint[/green]",
                classes="metric-card",
            )
            yield Static(
                "Tareas\n[bold]921[/bold]\n[red]47 bloq.[/red]",
                classes="metric-card",
            )
            yield Static(
                f"Salud\n[bold green]{ANALYTICS['health_current']}[/bold green]\n[green]Bueno[/green]",
                classes="metric-card",
            )
        with Horizontal(id="dash-cols"):
            with Vertical(id="dash-activity"):
                yield Static("[bold]Actividad reciente[/bold]", classes="section-title")
                for item in ACTIVITY_LOG[:5]:
                    yield Static(
                        f"  {item['text']}  [dim]{item['time']}[/dim]",
                        classes="activity-item",
                    )
            with Vertical(id="dash-gates"):
                yield Static("[bold]Próximos gates[/bold]", classes="section-title")
                for gate in GATES:
                    status_color = "yellow" if gate["status"] == "pending" else "green"
                    yield Static(
                        f"  {gate['project']}: [cyan]{gate['from_phase']}[/cyan] → "
                        f"[cyan]{gate['to_phase']}[/cyan]  [{status_color}]{gate['status']}[/{status_color}]",
                        classes="gate-item",
                    )
