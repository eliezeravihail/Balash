"""Entry point so the tool runs as ``python -m tasktool``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
