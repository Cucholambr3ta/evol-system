"""Pantalla Disciplines — 31 disciplinas *-DD EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Vertical, Horizontal
from .base import BaseScreen
from ..widgets.drawer import Drawer
from ..data.mock_data import DISCIPLINES

DISCIPLINES_BY_ID = {d["id"]: d for d in DISCIPLINES}

TYPE_COLORS = {
    "base":     "green",
    "extended": "cyan",
}


class DisciplinesScreen(BaseScreen):
    """Catálogo de las 31 disciplinas *-Driven Development."""

    SCREEN_ID = "8"

    DEFAULT_CSS = """
    DisciplinesScreen {
        layout: vertical;
        padding: 1;
    }
    #disc-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #disc-stats {
        height: 1;
        margin-bottom: 1;
    }
    #disc-table {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    """

    def compose(self) -> ComposeResult:
        base_count = sum(1 for d in DISCIPLINES if d["type"] == "base")
        ext_count = sum(1 for d in DISCIPLINES if d["type"] == "extended")
        yield Static("[bold]EVOL-DD · Disciplinas[/bold]", id="disc-title")
        yield Static(
            f"  [dim]{len(DISCIPLINES)} disciplinas · "
            f"[green]{base_count} base[/green] · "
            f"[cyan]{ext_count} extendidas[/cyan][/dim]",
            id="disc-stats",
        )
        table = DataTable(id="disc-table")
        yield table
        yield Drawer(id="disc-drawer")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Tipo", "Nombre", "Fase", "Skill")
        for disc in DISCIPLINES:
            dtype = disc["type"]
            color = TYPE_COLORS.get(dtype, "white")
            table.add_row(
                disc["id"],
                f"[{color}]{dtype}[/{color}]",
                disc["name"],
                disc["phase"],
                disc["skill"],
                key=disc["id"],
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value if event.row_key is not None else None
        disc = DISCIPLINES_BY_ID.get(row_key)
        if disc is None:
            return
        drawer = self.query_one("#disc-drawer", Drawer)
        content = (
            f"Tipo: {disc['type']}\n"
            f"Fase: {disc['phase']}\n"
            f"Skill asociada: {disc['skill']}\n\n"
            f"[dim]{disc['name']}[/dim]"
        )
        drawer.open_with(disc["id"], content)

    def action_go_back(self) -> None:
        drawer = self.query_one("#disc-drawer", Drawer)
        if "open" in drawer.classes:
            drawer.close()
            return
        super().action_go_back()
