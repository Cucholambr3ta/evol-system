"""Selector de idioma para EVOL-DD TUI."""
from textual.widget import Widget
from textual.reactive import reactive
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..i18n import I18n


class LangSelector(Widget):
    """Widget selector de idioma (es/en/pt)."""

    DEFAULT_CSS = """
    LangSelector {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    """

    current_lang: reactive = reactive("es")

    def __init__(self, i18n: "I18n", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.i18n = i18n
        self.current_lang = i18n.lang

    def render(self) -> str:
        langs = [("es", "ES"), ("en", "EN"), ("pt", "PT")]
        parts = []
        for code, label in langs:
            if code == self.current_lang:
                parts.append(f"[bold reverse] {label} [/bold reverse]")
            else:
                parts.append(f"[dim] {label} [/dim]")
        return " ".join(parts)

    def cycle(self) -> None:
        self.i18n.cycle_lang()
        self.current_lang = self.i18n.lang
