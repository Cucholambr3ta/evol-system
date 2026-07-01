"""Pantalla Skills — catálogo de skills EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static, DataTable, Input
from textual.containers import Vertical
from .base import BaseScreen
from ..data.mock_data import SKILLS

CATEGORY_COLORS = {
    "discipline": "cyan",
    "core":       "green",
    "domain":     "yellow",
    "game":       "magenta",
    "transfer":   "blue",
}


class SkillsScreen(BaseScreen):
    """Catálogo de skills con filtro."""

    SCREEN_ID = "7"

    DEFAULT_CSS = """
    SkillsScreen {
        layout: vertical;
        padding: 1;
    }
    #sk-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #sk-filter {
        height: 3;
        margin-bottom: 1;
    }
    #sk-stats {
        height: 1;
        margin-bottom: 1;
    }
    #sk-table {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    """

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._filter_text = ""

    def compose(self) -> ComposeResult:
        yield Static("[bold]EVOL-DD · Skills[/bold]", id="sk-title")
        yield Input(placeholder="Filtrar skills...", id="sk-filter")
        yield Static(
            f"  [dim]{len(SKILLS)} skills registradas[/dim]",
            id="sk-stats",
        )
        table = DataTable(id="sk-table")
        yield table

    def on_mount(self) -> None:
        self._populate_table(SKILLS)

    def _populate_table(self, data: list) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Categoría", "Descripción", "Fase")
        for skill in data:
            cat = skill["category"]
            color = CATEGORY_COLORS.get(cat, "white")
            table.add_row(
                skill["id"],
                f"[{color}]{cat}[/{color}]",
                skill["desc"],
                skill["phase"],
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        self._filter_text = event.value.lower()
        if self._filter_text:
            filtered = [
                s for s in SKILLS
                if self._filter_text in s["id"].lower()
                or self._filter_text in s["desc"].lower()
                or self._filter_text in s["category"].lower()
            ]
        else:
            filtered = SKILLS
        self._populate_table(filtered)
        stats = self.query_one("#sk-stats", Static)
        stats.update(f"  [dim]{len(filtered)} skills (de {len(SKILLS)})[/dim]")
