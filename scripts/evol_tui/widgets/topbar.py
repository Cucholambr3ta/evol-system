"""Topbar con breadcrumb."""
from textual.widget import Widget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..i18n import I18n


class Topbar(Widget):
    DEFAULT_CSS = """
    Topbar {
        height: 1;
        background: $surface-darken-1;
        padding: 0 1;
    }
    """

    def __init__(self, i18n: "I18n", breadcrumb: str = "", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.i18n = i18n
        self.breadcrumb = breadcrumb

    def render(self) -> str:
        return f" {self.breadcrumb}"
