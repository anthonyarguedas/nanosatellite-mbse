"""Explicit legacy workspace conversion entry point."""

from .migrate import main

if __name__ == "__main__":
    raise SystemExit(main())
