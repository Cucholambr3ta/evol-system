"""Sidebar persistente EVOL-DD TUI."""
from textual.widget import Widget
from textual.reactive import reactive
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..i18n import I18n


class Sidebar(Widget):
    """Sidebar con navegación, idioma y tema."""

    DEFAULT_CSS = """
    Sidebar {
        width: 24;
        height: 100%;
        background: $surface;
        border-right: solid $primary-darken-2;
        padding: 0;
        overflow: hidden;
    }
    """

    current_screen: reactive = reactive("1")
    current_lang: reactive = reactive("es")

    SCREEN_KEYS = [
        ("1", "nav.dashboard"),
        ("2", "nav.projects"),
        ("3", "nav.knowledge"),
        ("4", "nav.devGraph"),
        ("/", "nav.search"),
        ("5", "nav.memory"),
        ("6", "nav.agents"),
        ("7", "nav.skills"),
        ("8", "nav.disciplines"),
        ("9", "nav.analytics"),
    ]

    COUNTS = {
        "2": "24",
        "6": "18",
        "7": "17",
        "8": "31",
    }

    def __init__(self, i18n: "I18n", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.i18n = i18n

    def render(self) -> str:
        t = self.i18n.t
        lines = []
        lines.append(" [bold]EVOL-DD[/bold]")
        lines.append("─" * 22)
        lines.append(f" [dim]{t('nav.main')}[/dim]")

        main_keys = ["1", "2", "3", "4", "/"]
        for key, i18n_key in self.SCREEN_KEYS:
            if key not in main_keys:
                continue
            name = t(i18n_key)
            count = self.COUNTS.get(key, "")
            count_str = f" [dim]{count}[/dim]" if count else ""
            active = key == self.current_screen
            if active:
                lines.append(f" [bold reverse] [{key}] {name}{count_str}[/bold reverse]")
            else:
                lines.append(f" [{key}] {name}{count_str}")

        lines.append("")
        lines.append(f" [dim]{t('nav.workspace')}[/dim]")

        ws_keys = ["5", "6", "7", "8", "9"]
        for key, i18n_key in self.SCREEN_KEYS:
            if key not in ws_keys:
                continue
            name = t(i18n_key)
            count = self.COUNTS.get(key, "")
            count_str = f" [dim]{count}[/dim]" if count else ""
            active = key == self.current_screen
            if active:
                lines.append(f" [bold reverse] [{key}] {name}{count_str}[/bold reverse]")
            else:
                lines.append(f" [{key}] {name}{count_str}")

        lines.append("")
        lines.append("─" * 22)
        lang_upper = self.current_lang.upper()
        lines.append(f" [L] {t('topbar.lang')}: {lang_upper} ▾")
        lines.append(" [T] Tema ▾")
        lines.append("─" * 22)
        lines.append(" [dim]18 agentes · 70 sk[/dim]")
        return "\n".join(lines)
