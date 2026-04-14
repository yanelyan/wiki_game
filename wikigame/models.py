from __future__ import annotations

from typing import Protocol


class LinkProvider(Protocol):
    def get_links(self, title: str) -> list[str]:
        ...

    def get_backlinks(self, title: str) -> list[str]:
        ...