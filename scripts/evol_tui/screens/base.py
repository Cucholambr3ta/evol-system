"""Pantalla base para todas las pantallas EDMS."""
from textual.screen import Screen
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..i18n import I18n
    from ..navigation import NavigationManager


class BaseScreen(Screen):
    """Pantalla base con bindings de navegación globales."""

    BINDINGS = [
        ("1", "goto_screen('1')", "Tablero"),
        ("2", "goto_screen('2')", "Proyectos"),
        ("3", "goto_screen('3')", "Conocimiento"),
        ("4", "goto_screen('4')", "Desarrollo"),
        ("5", "goto_screen('5')", "Memoria"),
        ("6", "goto_screen('6')", "Agentes"),
        ("7", "goto_screen('7')", "Skills"),
        ("8", "goto_screen('8')", "Disciplinas"),
        ("9", "goto_screen('9')", "Analítica"),
        ("/", "open_search", "Buscar"),
        ("ctrl+k", "open_search", "Buscar"),
        ("l", "cycle_lang", "Idioma"),
        ("t", "theme_menu", "Tema"),
        ("question_mark", "help_screen", "Ayuda"),
        ("q", "app.quit", "Salir"),
        ("escape", "go_back", "Volver"),
    ]

    def action_goto_screen(self, screen_id: str) -> None:
        self.app.action_goto_screen(screen_id)  # type: ignore[attr-defined]

    def action_open_search(self) -> None:
        self.app.action_goto_screen("/")  # type: ignore[attr-defined]

    def action_cycle_lang(self) -> None:
        self.app.action_cycle_lang()  # type: ignore[attr-defined]

    def action_theme_menu(self) -> None:
        self.app.action_cycle_theme()  # type: ignore[attr-defined]

    def action_help_screen(self) -> None:
        pass  # TODO: mostrar panel de ayuda

    def action_go_back(self) -> None:
        self.app.action_go_back()  # type: ignore[attr-defined]
