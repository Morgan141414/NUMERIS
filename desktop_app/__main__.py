"""Launch NUMERIS with ``python -m desktop_app``."""

from .app import main as _app_main


def main() -> int:
    """Delegate to the Tkinter application entrypoint."""
    return _app_main()


if __name__ == "__main__":
    raise SystemExit(main())
