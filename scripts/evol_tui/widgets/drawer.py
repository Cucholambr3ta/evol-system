"""Drawer lateral de detalle."""
from textual.widget import Widget
from textual.reactive import reactive
from typing import Optional


class Drawer(Widget):
    DEFAULT_CSS = """
    Drawer {
        width: 40;
        height: 100%;
        background: $surface;
        border-left: solid $primary-darken-2;
        padding: 1;
        display: none;
    }
    Drawer.open {
        display: block;
    }
    """

    title: reactive = reactive("")
    content: reactive = reactive("")

    def open_with(self, title: str, content: str) -> None:
        self.title = title
        self.content = content
        self.add_class("open")

    def close(self) -> None:
        self.remove_class("open")

    def render(self) -> str:
        if not self.title:
            return ""
        return f"[bold]{self.title}[/bold]\n{'─' * 36}\n{self.content}"
