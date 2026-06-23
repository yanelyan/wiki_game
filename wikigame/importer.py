from __future__ import annotations

import gzip
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .utils import normalize_title

if TYPE_CHECKING:
    from psycopg import Connection


@dataclass(frozen=True)
class ImportStats:
    pages_inserted: int
    link_targets_inserted: int
    links_inserted: int


def ensure_schema(conn: Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                from_page_id INTEGER NOT NULL,
                to_page_id INTEGER NOT NULL,
                PRIMARY KEY (from_page_id, to_page_id)
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pages_title ON pages(title)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_links_to_page_id ON links(to_page_id)")
    conn.commit()


def import_wikimedia_dumps(
    conn: Connection,
    *,
    page_dump_path: str | Path,
    pagelinks_dump_path: str | Path,
    truncate: bool = False,
    batch_size: int = 5_000,
) -> ImportStats:
    ensure_schema(conn)
    _prepare_import_tables(conn, truncate=truncate)

    pages_inserted = _import_pages(conn, Path(page_dump_path), batch_size=batch_size)
    link_targets_inserted = _import_pagelinks(conn, Path(pagelinks_dump_path), batch_size=batch_size)
    links_inserted = _materialize_links(conn)

    return ImportStats(
        pages_inserted=pages_inserted,
        link_targets_inserted=link_targets_inserted,
        links_inserted=links_inserted,
    )


def _prepare_import_tables(conn: Connection, *, truncate: bool) -> None:
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS link_targets")
        cur.execute(
            """
            CREATE TEMP TABLE link_targets (
                from_page_id INTEGER NOT NULL,
                to_title TEXT NOT NULL
            )
            """
        )
        if truncate:
            cur.execute("TRUNCATE TABLE links, pages")
    conn.commit()


def _import_pages(conn: Connection, path: Path, *, batch_size: int) -> int:
    inserted = 0
    batch: list[tuple[int, str]] = []

    for fields in iter_insert_rows(path, "page"):
        if len(fields) < 3:
            continue

        page_id = _parse_int(fields[0])
        namespace = _parse_int(fields[1])
        title = fields[2]

        if page_id is None or namespace != 0 or title is None:
            continue

        batch.append((page_id, normalize_title(title)))
        if len(batch) >= batch_size:
            inserted += _insert_pages_batch(conn, batch)
            batch.clear()

    if batch:
        inserted += _insert_pages_batch(conn, batch)

    return inserted


def _insert_pages_batch(conn: Connection, rows: list[tuple[int, str]]) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO pages (id, title)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def _import_pagelinks(conn: Connection, path: Path, *, batch_size: int) -> int:
    inserted = 0
    batch: list[tuple[int, str]] = []

    for fields in iter_insert_rows(path, "pagelinks"):
        if len(fields) < 3:
            continue

        from_page_id = _parse_int(fields[0])
        namespace = _parse_int(fields[1])
        title = fields[2]
        from_namespace = _parse_int(fields[3]) if len(fields) > 3 else 0

        if from_page_id is None or namespace != 0 or from_namespace not in (None, 0) or title is None:
            continue

        batch.append((from_page_id, normalize_title(title)))
        if len(batch) >= batch_size:
            inserted += _insert_link_targets_batch(conn, batch)
            batch.clear()

    if batch:
        inserted += _insert_link_targets_batch(conn, batch)

    return inserted


def _insert_link_targets_batch(conn: Connection, rows: list[tuple[int, str]]) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO link_targets (from_page_id, to_title) VALUES (%s, %s)",
            rows,
        )
    conn.commit()
    return len(rows)


def _materialize_links(conn: Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_link_targets_to_title ON link_targets(to_title)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_link_targets_from_page_id ON link_targets(from_page_id)")
        cur.execute(
            """
            INSERT INTO links (from_page_id, to_page_id)
            SELECT lt.from_page_id, p.id
            FROM link_targets lt
            JOIN pages p ON p.title = lt.to_title
            ON CONFLICT (from_page_id, to_page_id) DO NOTHING
            """
        )
        rowcount = cur.rowcount
    conn.commit()
    return max(rowcount, 0)


def iter_insert_rows(path: Path, table_name: str) -> Iterator[list[str | None]]:
    prefix_plain = f"INSERT INTO {table_name} VALUES "
    prefix_quoted = f"INSERT INTO `{table_name}` VALUES "

    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(prefix_plain):
                values_sql = line[len(prefix_plain) :].rstrip()
            elif line.startswith(prefix_quoted):
                values_sql = line[len(prefix_quoted) :].rstrip()
            else:
                continue

            yield from _parse_values_sql(values_sql)


def _parse_values_sql(values_sql: str) -> Iterator[list[str | None]]:
    current_row: list[str | None] | None = None
    current_field: list[str] = []
    in_string = False
    escape = False

    for ch in values_sql:
        if current_row is None:
            if ch == "(":
                current_row = []
                current_field = []
            continue

        if in_string:
            if escape:
                current_field.append(_decode_escape(ch))
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == "'":
                in_string = False
                continue
            current_field.append(ch)
            continue

        if ch == "'":
            in_string = True
            continue
        if ch == ",":
            current_row.append(_coerce_field("".join(current_field)))
            current_field = []
            continue
        if ch == ")":
            current_row.append(_coerce_field("".join(current_field)))
            yield current_row
            current_row = None
            current_field = []
            continue
        if ch == ";":
            continue
        current_field.append(ch)


def _coerce_field(raw: str) -> str | None:
    value = raw.strip()
    if value == "NULL":
        return None
    return value


def _decode_escape(ch: str) -> str:
    escape_map = {
        "0": "\0",
        "b": "\b",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "Z": "\x1a",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }
    return escape_map.get(ch, ch)


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
