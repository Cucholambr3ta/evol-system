"""Selector de tema para EVOL-DD TUI."""
from textual.widget import Widget
from textual.reactive import reactive
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..i18n import I18n

THEMES: List[str] = [
    "bruma",
    "lavanda",
    "marfil",
    "ambar",
    "nocturna",
    "bosque",
    "grafito",
    "salvia",
    "coral",
    "pizarra",
    "oceano",
    "arena",
    "violeta",
]

THEME_CYCLE = {t: THEMES[(i + 1) % len(THEMES)] for i, t in enumerate(THEMES)}


class ThemePicker(Widget):
    """Widget selector de tema visual."""

    DEFAULT_CSS = """
    ThemePicker {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    """

    current_theme: reactive = reactive("bruma")

    def __init__(self, i18n: "I18n", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.i18n = i18n

    def render(self) -> str:
        t = self.i18n.t
        key = f"theme.name.{self.current_theme}"
        name = t(key, fallback=self.current_theme.capitalize())
        return f"[bold]Tema:[/bold] {name} ▾"

    def cycle(self) -> None:
        self.current_theme = THEME_CYCLE.get(self.current_theme, THEMES[0])
