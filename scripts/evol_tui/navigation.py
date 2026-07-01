"""Mapa de navegación centralizado para EVOL-DD TUI."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScreenRoute:
    id: str
    name_key: str
    screen_class: str
    breadcrumb_key: str
    is_fullscreen: bool = False
    description_es: str = ""


ROUTES: Dict[str, ScreenRoute] = {
    "1": ScreenRoute("1", "nav.dashboard",    "DashboardScreen",      "breadcrumb.dashboard",    False, "Resumen general"),
    "2": ScreenRoute("2", "nav.projects",     "ProjectsScreen",       "breadcrumb.projects",     False, "Tablero de proyectos"),
    "3": ScreenRoute("3", "nav.knowledge",    "KnowledgeGraphScreen", "breadcrumb.knowledgeGraph", True, "Grafo de navegación"),
    "4": ScreenRoute("4", "nav.devGraph",     "DevGraphScreen",       "breadcrumb.devGraph",     True,  "Grafo de código"),
    "5": ScreenRoute("5", "nav.memory",       "MemoryScreen",         "breadcrumb.memory",       False, "Consolidación"),
    "6": ScreenRoute("6", "nav.agents",       "AgentsScreen",         "breadcrumb.agents",       False, "Workspace de agentes"),
    "7": ScreenRoute("7", "nav.skills",       "SkillsScreen",         "breadcrumb.skills",       False, "Skills registradas"),
    "8": ScreenRoute("8", "nav.disciplines",  "DisciplinesScreen",    "breadcrumb.disciplines",  False, "52 disciplinas"),
    "9": ScreenRoute("9", "nav.analytics",    "AnalyticsScreen",      "breadcrumb.analytics",    False, "Métricas del pipeline"),
    "/": ScreenRoute("/", "nav.search",       "SearchScreen",         "breadcrumb.search",       False, "Búsqueda global"),
}


class NavigationManager:
    def __init__(self) -> None:
        self.history: List[str] = []
        self.current: str = "1"

    def goto(self, screen_id: str) -> Optional[ScreenRoute]:
        if screen_id not in ROUTES:
            return None
        if screen_id != self.current:
            self.history.append(self.current)
            self.current = screen_id
        return ROUTES[screen_id]

    def back(self) -> Optional[str]:
        if self.history:
            prev = self.history.pop()
            self.current = prev
            return prev
        return None

    def get_breadcrumb(self, i18n: "I18n") -> str:  # type: ignore[name-defined]
        parts = [i18n.t("breadcrumb.dashboard")]
        if self.current != "1":
            route = ROUTES.get(self.current)
            if route:
                parts.append(i18n.t(route.breadcrumb_key))
        return " / ".join(parts)
