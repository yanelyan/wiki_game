from __future__ import annotations

import argparse
from pathlib import Path

from .db import DbConfig
from .importer import ImportStats
from .importer import import_wikimedia_dumps


def _build_parser() -> argparse.ArgumentParser:
    defaults = DbConfig.from_env()
    p = argparse.ArgumentParser(prog="wikigame-import", description="Import Wikimedia SQL dumps into PostgreSQL")
    p.add_argument("--page-dump", required=True, help="Path to ruwiki-latest-page.sql.gz")
    p.add_argument("--pagelinks-dump", required=True, help="Path to ruwiki-latest-pagelinks.sql.gz")
    p.add_argument("--db-host", default=defaults.host)
    p.add_argument("--db-port", type=int, default=defaults.port)
    p.add_argument("--db-name", default=defaults.dbname)
    p.add_argument("--db-user", default=defaults.user)
    p.add_argument("--db-password", default=defaults.password)
    p.add_argument("--truncate", action="store_true", help="Очистить pages и links перед импортом")
    p.add_argument("--batch-size", type=int, default=5_000)
    return p


def _build_db_config(args: argparse.Namespace) -> DbConfig:
    return DbConfig(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password,
    )


def _print_stats(stats: ImportStats) -> None:
    print("Import completed.")
    print(f"Pages processed: {stats.pages_inserted}")
    print(f"Pagelinks processed: {stats.link_targets_inserted}")
    print(f"Resolved links inserted: {stats.links_inserted}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = _build_db_config(args)

    with config.connect() as conn:
        stats = import_wikimedia_dumps(
            conn,
            page_dump_path=Path(args.page_dump),
            pagelinks_dump_path=Path(args.pagelinks_dump),
            truncate=args.truncate,
            batch_size=args.batch_size,
        )

    _print_stats(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
