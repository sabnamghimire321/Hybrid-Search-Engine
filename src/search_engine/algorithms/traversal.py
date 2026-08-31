from collections import deque
from typing import Any
from search_engine.datastructures.graph import Graph

def bfs(graph: Graph, start: Any) -> list[Any]:
    if not graph.has_node(start):
        return []

    visited = {start}
    order = []
    queue = deque([start])

    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def bfs_shortest_path(graph: Graph, start: Any, target: Any) -> list[Any] | None:
    """Shortest path (fewest edges) from start to target, via BFS with
    parent tracking. Returns None if target is unreachable from start."""
    if not graph.has_node(start) or not graph.has_node(target):
        return None
    if start == target:
        return [start]

    visited = {start}
    parent: dict[Any, Any] = {}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                if neighbor == target:
                    return _reconstruct_path(parent, start, target)
                queue.append(neighbor)

    return None

def _reconstruct_path(parent: dict[Any, Any], start: Any, target: Any) -> list[Any]:
    path = [target]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def dfs(graph: Graph, start: Any) -> list[Any]:
    if not graph.has_node(start):
        return []

    visited: set[Any] = set()
    order = []
    stack = [start]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        order.append(current)

        for neighbor in reversed(graph.neighbors(current)):
            if neighbor not in visited:
                stack.append(neighbor)

    return order