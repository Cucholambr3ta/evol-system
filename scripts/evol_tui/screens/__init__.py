"""Pantallas EVOL-DD TUI."""
from .dashboard import DashboardScreen
from .projects import ProjectsScreen
from .knowledge_graph import KnowledgeGraphScreen
from .dev_graph import DevGraphScreen
from .memory import MemoryScreen
from .agents import AgentsScreen
from .skills import SkillsScreen
from .disciplines import DisciplinesScreen
from .analytics import AnalyticsScreen
from .search import SearchScreen

__all__ = [
    "DashboardScreen",
    "ProjectsScreen",
    "KnowledgeGraphScreen",
    "DevGraphScreen",
    "MemoryScreen",
    "AgentsScreen",
    "SkillsScreen",
    "DisciplinesScreen",
    "AnalyticsScreen",
    "SearchScreen",
]
