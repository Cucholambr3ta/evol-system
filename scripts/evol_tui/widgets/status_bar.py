"""Barra de estado inferior con atajos."""
from textual.widget import Widget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..i18n import I18n


class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $primary-darken-3;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, i18n: "I18n", caps_label: str = "", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.i18n = i18n
        self.caps_label = caps_label

    def render(self) -> str:
        base = " [1-9] Navegar  [/] Buscar  [L] Idioma  [T] Tema  [?] Ayuda  [q] Salir"
        if self.caps_label:
            return "{0}   [dim]· {1}[/dim]".format(base, self.caps_label)
        return base
