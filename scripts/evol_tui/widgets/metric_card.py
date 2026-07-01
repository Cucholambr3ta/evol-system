"""Card de métrica reutilizable."""
from textual.widget import Widget


class MetricCard(Widget):
    DEFAULT_CSS = """
    MetricCard {
        width: 1fr;
        height: 6;
        border: solid $primary-darken-2;
        padding: 0 1;
    }
    """

    def __init__(self, label: str, value: str, delta: str = "", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.delta = delta

    def render(self) -> str:
        return f"[dim]{self.label}[/dim]\n[bold]{self.value}[/bold]\n[green]{self.delta}[/green]"
