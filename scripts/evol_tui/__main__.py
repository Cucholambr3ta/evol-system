"""Entry point para evol_tui."""
from .app import EvolDDApp


def main() -> None:
    app = EvolDDApp()
    app.run()


if __name__ == "__main__":
    main()
