"""Pantalla Agents — workspace de agentes EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Vertical, Horizontal
from .base import BaseScreen
from ..widgets.drawer import Drawer
from ..data.mock_data import AGENTS

AGENTS_BY_ID = {a["id"]: a for a in AGENTS}


def _status_markup(status: str) -> str:
    if status == "active":
        return "[bold green]● Activo[/bold green]"
    return "[dim]○ Inactivo[/dim]"


class AgentsScreen(BaseScreen):
    """Workspace de los 18 agentes núcleo."""

    SCREEN_ID = "6"

    DEFAULT_CSS = """
    AgentsScreen {
        layout: vertical;
        padding: 1;
    }
    #ag-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #ag-counts {
        height: 1;
        margin-bottom: 1;
    }
    #ag-table {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    """

    def compose(self) -> ComposeResult:
        active_count = sum(1 for a in AGENTS if a["status"] == "active")
        inactive_count = len(AGENTS) - active_count
        yield Static("[bold]EVOL-DD · Agentes Núcleo[/bold]", id="ag-title")
        yield Static(
            f"  [dim]{len(AGENTS)} permanentes · "
            f"[green]{active_count} activos[/green] · "
            f"[dim]{inactive_count} inactivos[/dim][/dim]",
            id="ag-counts",
        )
        table = DataTable(id="ag-table")
        yield table
        yield Drawer(id="ag-drawer")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Agente", "Especialidad", "Estado", "Ejecuciones", "Última")
        for agent in AGENTS:
            table.add_row(
                agent["id"],
                agent["specialty"],
                _status_markup(agent["status"]),
                str(agent["runs"]),
                agent["last"],
                key=agent["id"],
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value if event.row_key is not None else None
        agent = AGENTS_BY_ID.get(row_key)
        if agent is None:
            return
        drawer = self.query_one("#ag-drawer", Drawer)
        content = (
            f"Especialidad: {agent['specialty']}\n"
            f"Estado: {agent['status']}\n"
            f"Ejecuciones: {agent['runs']}\n"
            f"Última actividad: {agent['last']}\n\n"
            f"[dim]Detalle del agente seleccionado.[/dim]"
        )
        drawer.open_with(agent["id"], content)

    def action_go_back(self) -> None:
        drawer = self.query_one("#ag-drawer", Drawer)
        if "open" in drawer.classes:
            drawer.close()
            return
        super().action_go_back()
