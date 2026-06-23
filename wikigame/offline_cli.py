from __future__ import annotations

import argparse

from .bfs import SearchResult
from .bfs import find_path_bidirectional_bfs
from .db import DbConfig
from .postgres_provider import PostgresLinkProvider
from .utils import Timer


def _build_parser() -> argparse.ArgumentParser:
    defaults = DbConfig.from_env()
    p = argparse.ArgumentParser(prog="wikigame-offline", description="WikiGame path finder via PostgreSQL")
    p.add_argument("--start", required=True, help="Стартовая статья")
    p.add_argument("--goal", required=True, help="Целевая статья")
    p.add_argument("--max-depth", type=int, default=5)
    p.add_argument("--max-pages", type=int, default=20_000)
    p.add_argument("--db-host", default=defaults.host)
    p.add_argument("--db-port", type=int, default=defaults.port)
    p.add_argument("--db-name", default=defaults.dbname)
    p.add_argument("--db-user", default=defaults.user)
    p.add_argument("--db-password", default=defaults.password)
    return p


def _build_db_config(args: argparse.Namespace) -> DbConfig:
    return DbConfig(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password,
    )


def _print_result(result: SearchResult | None, seconds: float) -> int:
    if result is None:
        print(f"Path not found. (time={seconds:.2f}s)")
        return 2

    print("Path found:")
    print(" -> ".join(result.path))
    print(f"Clicks: {len(result.path) - 1}")
    print(f"Expanded pages: {result.visited_pages}")
    print(f"Time: {seconds:.2f}s")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = _build_db_config(args)
    provider = PostgresLinkProvider(config)

    t = Timer.start()
    result = find_path_bidirectional_bfs(
        args.start,
        args.goal,
        provider,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
    )
    return _print_result(result, t.seconds())


if __name__ == "__main__":
    raise SystemExit(main())
