"""App principal EVOL-DD TUI."""
import os
from pathlib import Path
from typing import Dict, Optional, Type
from textual.app import App, ComposeResult
from textual.reactive import reactive

from .i18n import I18n
from .navigation import NavigationManager, ROUTES
from .widgets.theme_picker import ThemePicker, THEMES
from .screens.dashboard import DashboardScreen
from .screens.projects import ProjectsScreen
from .screens.knowledge_graph import KnowledgeGraphScreen
from .screens.dev_graph import DevGraphScreen
from .screens.memory import MemoryScreen
from .screens.agents import AgentsScreen
from .screens.skills import SkillsScreen
from .screens.disciplines import DisciplinesScreen
from .screens.analytics import AnalyticsScreen
from .screens.search import SearchScreen
from .screens.base import BaseScreen


def detect_terminal() -> Dict[str, bool]:
    """Detecta capacidades del terminal anfitrión.

    - ghostty / kitty: vía $TERM_PROGRAM
    - truecolor: vía $COLORTERM
    - kitty_graphics: protocolo gráfico Kitty (kitty, ghostty, wezterm lo soportan)
    - basic_ansi: fallback cuando no hay truecolor (sigue funcionando la app)
    """
    term_program = os.environ.get("TERM_PROGRAM", "")
    term = os.environ.get("TERM", "")
    colorterm = os.environ.get("COLORTERM", "")
    kitty_graphics = term_program in ("kitty", "ghostty", "WezTerm") or "kitty" in term
    truecolor = "truecolor" in colorterm or "24bit" in colorterm
    return {
        "ghostty":        term_program == "ghostty",
        "kitty":          term_program == "kitty",
        "truecolor":      truecolor,
        "kitty_graphics": kitty_graphics,
        "basic_ansi":     not truecolor,
    }


def _caps_label(caps: Dict[str, bool]) -> str:
    """Etiqueta corta de capacidades detectadas para la barra de estado."""
    if caps.get("ghostty"):
        name = "Ghostty"
    elif caps.get("kitty"):
        name = "Kitty"
    else:
        name = "Terminal"
    extras = []
    if caps.get("truecolor"):
        extras.append("truecolor")
    else:
        extras.append("ansi básico")
    if caps.get("kitty_graphics"):
        extras.append("gfx-kitty")
    return "{0} · {1}".format(name, " · ".join(extras))


SCREEN_MAP: Dict[str, Type[BaseScreen]] = {
    "1": DashboardScreen,
    "2": ProjectsScreen,
    "3": KnowledgeGraphScreen,
    "4": DevGraphScreen,
    "5": MemoryScreen,
    "6": AgentsScreen,
    "7": SkillsScreen,
    "8": DisciplinesScreen,
    "9": AnalyticsScreen,
    "/": SearchScreen,
}


class EvolDDApp(App):
    """App principal EVOL-DD TUI."""

    CSS_PATH = "styles/main.tcss"
    TITLE = "EVOL-DD"
    SUB_TITLE = "Enterprise Development Framework"

    current_lang: reactive = reactive("es")
    evol_theme: reactive = reactive("bruma")

    def __init__(self) -> None:
        super().__init__()
        self.i18n = I18n("es")
        self.nav = NavigationManager()
        self.caps = detect_terminal()
        self.caps_label = _caps_label(self.caps)
        self._theme_dir = Path(__file__).parent / "styles" / "themes"
        self.i18n.on_change(self._on_lang_change)

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())
        self._apply_theme(self.evol_theme)

    def _apply_theme(self, theme_name: str) -> None:
        """Aplica el TCSS del tema seleccionado, agregándolo al stylesheet."""
        theme_path = self._theme_dir / "{0}.tcss".format(theme_name)
        if not theme_path.exists():
            return
        try:
            self.stylesheet.read(str(theme_path))
            self.stylesheet.apply(self)
        except Exception:
            pass

    def action_cycle_theme(self) -> None:
        try:
            idx = THEMES.index(self.evol_theme)
        except ValueError:
            idx = 0
        self.evol_theme = THEMES[(idx + 1) % len(THEMES)]
        self._apply_theme(self.evol_theme)
        self.refresh()

    def _on_lang_change(self, lang: str) -> None:
        self.current_lang = lang
        self.refresh()

    def action_goto_screen(self, screen_id: str) -> None:
        if screen_id == self.nav.current:
            return
        route = self.nav.goto(screen_id)
        if route is None:
            return
        screen_cls = SCREEN_MAP.get(screen_id)
        if screen_cls is not None:
            if len(self._screen_stack) > 1:
                self.pop_screen()
            self.push_screen(screen_cls())

    def action_go_back(self) -> None:
        prev = self.nav.back()
        if prev is not None and len(self._screen_stack) > 1:
            self.pop_screen()

    def action_cycle_lang(self) -> None:
        self.i18n.cycle_lang()
