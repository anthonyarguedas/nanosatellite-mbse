"""The stable identity interface shared by requirements and domain elements."""

from typing import Protocol


# Explicit None selects no mode. Omission evaluates every configured mode.
ALL_MODES = object()


class Identified(Protocol):
    @property
    def key(self) -> str: ...

    @property
    def id(self) -> str: ...
