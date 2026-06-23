from __future__ import annotations

try:
    from .bfs import find_path_bidirectional_bfs
    from .db import DbConfig
    from .postgres_provider import PostgresLinkProvider
    from .utils import Timer
except ImportError:
    from wikigame.bfs import find_path_bidirectional_bfs
    from wikigame.db import DbConfig
    from wikigame.postgres_provider import PostgresLinkProvider
    from wikigame.utils import Timer


def main() -> int:
    print("WikiGame offline test")
    start = input("Start article: ").strip()
    goal = input("Goal article: ").strip()

    if not start or not goal:
        print("Both article titles are required.")
        return 1

    config = DbConfig.from_env()
    provider = PostgresLinkProvider(config)

    t = Timer.start()
    result = find_path_bidirectional_bfs(
        start,
        goal,
        provider,
        max_depth=6,
        max_pages=20_000,
    )

    if result is None:
        print(f"Path not found. (time={t.seconds():.2f}s)")
        return 2

    print(f"Shortest path length: {len(result.path) - 1}")
    print("Path:")
    print(" -> ".join(result.path))
    print(f"Expanded pages: {result.visited_pages}")
    print(f"Time: {t.seconds():.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
