"""Pantalla Search — búsqueda global EVOL-DD TUI."""
from textual.app import ComposeResult
from textual.widgets import Static, Input, ListView, ListItem, Label
from textual.containers import Vertical
from typing import List, Dict, Any
from .base import BaseScreen
from ..data.mock_data import AGENTS, SKILLS, PROJECTS

PAGE_RESULTS: List[Dict[str, Any]] = [
    {"label": "Tablero",             "key": "1", "type": "page"},
    {"label": "Proyectos",           "key": "2", "type": "page"},
    {"label": "Grafo Conocimiento",  "key": "3", "type": "page"},
    {"label": "Grafo Desarrollo",    "key": "4", "type": "page"},
    {"label": "Memoria",             "key": "5", "type": "page"},
    {"label": "Agentes",             "key": "6", "type": "page"},
    {"label": "Skills",              "key": "7", "type": "page"},
    {"label": "Disciplinas",         "key": "8", "type": "page"},
    {"label": "Analítica",           "key": "9", "type": "page"},
]

ALL_ITEMS: List[Dict[str, Any]] = (
    PAGE_RESULTS
    + [{"label": a["id"], "key": "6", "type": "agent", "extra": a["specialty"]} for a in AGENTS]
    + [{"label": s["id"], "key": "7", "type": "skill",  "extra": s["desc"]}     for s in SKILLS]
    + [{"label": p["name"], "key": "2", "type": "project", "extra": p["phase"]} for p in PROJECTS]
)


def _search(query: str) -> List[Dict[str, Any]]:
    if not query:
        return ALL_ITEMS[:20]
    q = query.lower()
    return [
        item for item in ALL_ITEMS
        if q in item["label"].lower()
        or q in item.get("extra", "").lower()
        or q in item["type"].lower()
    ][:30]


def _item_markup(item: Dict[str, Any]) -> str:
    type_color = {
        "page":    "bold cyan",
        "agent":   "green",
        "skill":   "yellow",
        "project": "magenta",
    }.get(item["type"], "white")
    extra = item.get("extra", "")
    extra_str = f"  [dim]{extra}[/dim]" if extra else ""
    return f"  [{type_color}]{item['type']:8}[/{type_color}]  {item['label']}{extra_str}"


class SearchScreen(BaseScreen):
    """Búsqueda global sobre páginas, agentes, skills y proyectos."""

    SCREEN_ID = "/"

    DEFAULT_CSS = """
    SearchScreen {
        layout: vertical;
        padding: 1;
    }
    #search-title {
        height: 1;
        text-style: bold;
        background: $primary-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    #search-input {
        height: 3;
        margin-bottom: 1;
    }
    #search-count {
        height: 1;
        margin-bottom: 1;
    }
    #search-results {
        height: 1fr;
        border: solid $primary-darken-2;
        overflow-y: auto;
    }
    .result-item {
        height: 1;
    }
    """

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._results: List[Dict[str, Any]] = _search("")

    def compose(self) -> ComposeResult:
        yield Static("[bold]EVOL-DD · Búsqueda[/bold]", id="search-title")
        yield Input(
            placeholder="Buscar páginas, proyectos, agentes, skills...",
            id="search-input",
        )
        yield Static(
            f"  [dim]{len(self._results)} resultados[/dim]",
            id="search-count",
        )
        with Vertical(id="search-results"):
            for item in self._results:
                yield Static(_item_markup(item), classes="result-item")

    def on_input_changed(self, event: Input.Changed) -> None:
        self._results = _search(event.value)
        count_widget = self.query_one("#search-count", Static)
        count_widget.update(f"  [dim]{len(self._results)} resultados[/dim]")
        results_container = self.query_one("#search-results", Vertical)
        results_container.remove_children()
        if self._results:
            for item in self._results:
                results_container.mount(Static(_item_markup(item), classes="result-item"))
        else:
            results_container.mount(Static("  [dim]Sin resultados.[/dim]"))

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()
