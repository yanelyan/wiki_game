from __future__ import annotations

from .db import DbConfig
from .utils import normalize_title


class PostgresLinkProvider:
    def __init__(self, config: DbConfig):
        self._config = config

    def get_links(self, title: str) -> list[str]:
        title = normalize_title(title)
        query = """
            SELECT dst.title
            FROM pages src
            JOIN links l ON l.from_page_id = src.id
            JOIN pages dst ON dst.id = l.to_page_id
            WHERE src.title = %s
            ORDER BY dst.title
        """
        with self._config.connect() as conn, conn.cursor() as cur:
            cur.execute(query, (title,))
            return [row[0] for row in cur.fetchall()]

    def get_backlinks(self, title: str) -> list[str]:
        title = normalize_title(title)
        query = """
            SELECT src.title
            FROM pages dst
            JOIN links l ON l.to_page_id = dst.id
            JOIN pages src ON src.id = l.from_page_id
            WHERE dst.title = %s
            ORDER BY src.title
        """
        with self._config.connect() as conn, conn.cursor() as cur:
            cur.execute(query, (title,))
            return [row[0] for row in cur.fetchall()]
