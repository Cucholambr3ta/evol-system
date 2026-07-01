"""Pantalla Analytics — métricas del pipeline EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from .base import BaseScreen
from ..data.mock_data import ANALYTICS, PROJECTS


def _ascii_bar(value: int, max_val: int, width: int = 20) -> str:
    filled = int((value / max_val) * width) if max_val > 0 else 0
    empty = width - filled
    return "█" * filled + "░" * empty


def _build_velocity_chart(sprints: list, values: list) -> str:
    max_val = max(values) if values else 1
    lines = []
    lines.append("  [bold]Velocidad por sprint:[/bold]")
    lines.append("")
    for sprint, val in zip(sprints, values):
        bar = _ascii_bar(val, max_val, 24)
        lines.append(f"  {sprint}  [cyan]{bar}[/cyan]  [bold]{val}[/bold] pts")
    return "\n".join(lines)


def _build_health_chart(sprints: list, values: list) -> str:
    max_val = 100
    lines = []
    lines.append("  [bold]Índice de salud:[/bold]")
    lines.append("")
    for sprint, val in zip(sprints, values):
        bar = _ascii_bar(val, max_val, 24)
        color = "green" if val >= 80 else ("yellow" if val >= 60 else "red")
        lines.append(f"  {sprint}  [{color}]{bar}[/{color}]  [bold]{val}%[/bold]")
    return "\n".join(lines)


class AnalyticsScreen(BaseScreen):
    """Métricas del pipeline con gráficos ASCII."""

    SCREEN_ID = "9"

    DEFAULT_CSS = """
    AnalyticsScreen {
        layout: vertical;
        padding: 1;
    }
    #an-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #an-kpis {
        height: 4;
        margin-bottom: 1;
    }
    .kpi-card {
        width: 1fr;
        height: 3;
        border: solid $primary-darken-2;
        padding: 0 1;
        margin: 0 1;
        content-align: center middle;
    }
    #an-charts {
        height: 1fr;
    }
    #an-velocity {
        width: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
        margin-right: 1;
        overflow-y: auto;
    }
    #an-health {
        width: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
        overflow-y: auto;
    }
    """

    def compose(self) -> ComposeResult:
        vel = ANALYTICS["velocity_current"]
        health = ANALYTICS["health_current"]
        blocked = ANALYTICS["blocked"]
        total_tasks = sum(p["tasks"] for p in PROJECTS)

        yield Static("[bold]EVOL-DD · Analítica[/bold]", id="an-title")
        with Horizontal(id="an-kpis"):
            yield Static(
                f"Velocidad\n[bold cyan]{vel}[/bold cyan]\n[dim]pts / sprint[/dim]",
                classes="kpi-card",
            )
            yield Static(
                f"Salud\n[bold green]{health}%[/bold green]\n[dim]Bueno[/dim]",
                classes="kpi-card",
            )
            yield Static(
                f"Bloqueadas\n[bold red]{blocked}[/bold red]\n[dim]tareas[/dim]",
                classes="kpi-card",
            )
            yield Static(
                f"Total tareas\n[bold]{total_tasks}[/bold]\n[dim]activas[/dim]",
                classes="kpi-card",
            )

        velocity_chart = _build_velocity_chart(
            ANALYTICS["sprints"], ANALYTICS["velocity"]
        )
        health_chart = _build_health_chart(
            ANALYTICS["sprints"], ANALYTICS["health"]
        )
        with Horizontal(id="an-charts"):
            yield Static(velocity_chart, id="an-velocity")
            yield Static(health_chart, id="an-health")
