from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional

from .models import LinkProvider
from .utils import normalize_title


@dataclass(frozen=True)
class SearchResult:
    path: list[str]
    visited_pages: int


def build_reverse_graph(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    reversed_graph: dict[str, list[str]] = {}

    for node in graph:
        reversed_graph.setdefault(node, [])

    for src in graph:
        for dst in graph[src]:
            reversed_graph.setdefault(dst, []).append(src)

    return reversed_graph


def get_backlinks(
    provider: LinkProvider,
    title: str,
    reverse_graph: dict[str, list[str]],
) -> list[str]:
    if hasattr(provider, "get_backlinks"):
        return provider.get_backlinks(title)

    return reverse_graph.get(title, [])


def find_path_bfs(
    start: str,
    goal: str,
    provider: LinkProvider,
    *,
    max_depth: int = 5,
    max_pages: int = 500,
) -> Optional[SearchResult]:
    start = normalize_title(start)
    goal = normalize_title(goal)

    if start == goal:
        return SearchResult(path=[start], visited_pages=0)

    queue = deque([(start, 0)])
    visited = {start}
    parent = {start: None}
    visited_pages = 0

    while queue:
        current, depth = queue.popleft()

        if depth >= max_depth:
            continue

        if visited_pages >= max_pages:
            break

        links = provider.get_links(current)
        visited_pages += 1

        for neighbor in links:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current

                if neighbor == goal:
                    path = []
                    node = goal
                    while node is not None:
                        path.append(node)
                        node = parent[node]
                    return SearchResult(path=path[::-1], visited_pages=visited_pages)

                if depth + 1 < max_depth:
                    queue.append((neighbor, depth + 1))

    return None


def find_path_bidirectional_bfs(
    start: str,
    goal: str,
    provider: LinkProvider,
    *,
    max_depth: int = 5,
    max_pages: int = 500,
) -> Optional[SearchResult]:
    start = normalize_title(start)
    goal = normalize_title(goal)

    if start == goal:
        return SearchResult(path=[start], visited_pages=0)

    reverse_graph = build_reverse_graph(provider.g) if hasattr(provider, "g") else {}

    parent = {start: None}
    children = {goal: None}

    dist_from_front = {start: 0}
    dist_from_back = {goal: 0}

    queue_from_front = deque([(start, 0)])
    visited_from_front = {start}

    queue_from_back = deque([(goal, 0)])
    visited_from_back = {goal}

    visited_pages = 0

    while queue_from_front or queue_from_back:
        if queue_from_front:
            current_from_front, depth_from_front = queue_from_front.popleft()

            if depth_from_front < max_depth and visited_pages < max_pages:
                links = provider.get_links(current_from_front)
                visited_pages += 1

                for neighbor in links:
                    if neighbor not in visited_from_front:
                        visited_from_front.add(neighbor)
                        parent[neighbor] = current_from_front
                        dist_from_front[neighbor] = depth_from_front + 1

                        if neighbor in visited_from_back:
                            if dist_from_front[neighbor] + dist_from_back[neighbor] > max_depth:
                                continue

                            left = []
                            node = neighbor
                            while node is not None:
                                left.append(node)
                                node = parent[node]
                            left.reverse()

                            right = []
                            node = children[neighbor]
                            while node is not None:
                                right.append(node)
                                node = children[node]

                            return SearchResult(
                                path=left + right,
                                visited_pages=visited_pages,
                            )

                        if depth_from_front + 1 < max_depth:
                            queue_from_front.append((neighbor, depth_from_front + 1))

        if queue_from_back:
            current_from_back, depth_from_back = queue_from_back.popleft()

            if depth_from_back < max_depth and visited_pages < max_pages:
                links = get_backlinks(provider, current_from_back, reverse_graph)
                visited_pages += 1

                for neighbor in links:
                    if neighbor not in visited_from_back:
                        visited_from_back.add(neighbor)
                        children[neighbor] = current_from_back

                        dist_from_back[neighbor] = depth_from_back + 1

                        if neighbor in visited_from_front:
                            if dist_from_front[neighbor] + dist_from_back[neighbor] > max_depth:
                                continue

                            left = []
                            node = neighbor
                            while node is not None:
                                left.append(node)
                                node = parent[node]
                            left.reverse()

                            right = []
                            node = children[neighbor]
                            while node is not None:
                                right.append(node)
                                node = children[node]

                            return SearchResult(
                                path=left + right,
                                visited_pages=visited_pages,
                            )

                        if depth_from_back + 1 < max_depth:
                            queue_from_back.append((neighbor, depth_from_back + 1))

        if visited_pages >= max_pages:
            break

    return None