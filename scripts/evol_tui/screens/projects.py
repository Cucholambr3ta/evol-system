"""Pantalla Proyectos — tablero de proyectos EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Vertical
from .base import BaseScreen
from ..widgets.drawer import Drawer
from ..data.mock_data import PROJECTS

PROJECTS_BY_ID = {p["id"]: p for p in PROJECTS}

PHASE_COLORS = {
    "Briefing": "cyan",
    "Spec":     "blue",
    "Plan":     "yellow",
    "Build":    "magenta",
    "QA":       "orange3",
    "Retro":    "green",
}

HEALTH_THRESHOLDS = [
    (90, "bold green"),
    (75, "green"),
    (60, "yellow"),
    (0,  "red"),
]


def _health_color(value: int) -> str:
    for threshold, color in HEALTH_THRESHOLDS:
        if value >= threshold:
            return color
    return "red"


class ProjectsScreen(BaseScreen):
    """Tablero de proyectos con fases y métricas."""

    SCREEN_ID = "2"

    DEFAULT_CSS = """
    ProjectsScreen {
        layout: vertical;
        padding: 1;
    }
    #proj-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #proj-summary {
        height: 1;
        margin-bottom: 1;
    }
    #proj-table {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]EVOL-DD · Proyectos[/bold]", id="proj-title")
        yield Static(
            f"  [dim]{len(PROJECTS)} proyectos activos[/dim]",
            id="proj-summary",
        )
        table = DataTable(id="proj-table")
        yield table
        yield Drawer(id="proj-drawer")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Nombre", "Fase", "Salud", "Tareas")
        for proj in PROJECTS:
            phase = proj["phase"]
            phase_color = PHASE_COLORS.get(phase, "white")
            health_val = proj["health"]
            health_color = _health_color(health_val)
            table.add_row(
                proj["id"],
                proj["name"],
                f"[{phase_color}]{phase}[/{phase_color}]",
                f"[{health_color}]{health_val}%[/{health_color}]",
                str(proj["tasks"]),
                key=proj["id"],
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value if event.row_key is not None else None
        proj = PROJECTS_BY_ID.get(row_key)
        if proj is None:
            return
        drawer = self.query_one("#proj-drawer", Drawer)
        content = (
            f"ID: {proj['id']}\n"
            f"Fase: {proj['phase']}\n"
            f"Salud: {proj['health']}%\n"
            f"Tareas activas: {proj['tasks']}\n\n"
            f"[dim]Detalle del proyecto seleccionado.[/dim]"
        )
        drawer.open_with(proj["name"], content)

    def action_go_back(self) -> None:
        drawer = self.query_one("#proj-drawer", Drawer)
        if "open" in drawer.classes:
            drawer.close()
            return
        super().action_go_back()
