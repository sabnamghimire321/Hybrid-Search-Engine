from typing import Any

class Graph:
    def __init__(self, directed: bool = True) -> None:
        self._adjacency: dict[Any, dict[Any, None]] = {}
        self._directed = directed

    def add_node(self, node: Any) -> None:
        self._adjacency.setdefault(node, {})

    def add_edge(self, from_node: Any, to_node: Any) -> None:
        self.add_node(from_node)
        self.add_node(to_node)
        self._adjacency[from_node][to_node] = None
        if not self._directed:
            self._adjacency[to_node][from_node] = None

    def neighbors(self, node: Any) -> list[Any]:
        return list(self._adjacency.get(node, {}).keys())

    def nodes(self) -> list[Any]:
        return list(self._adjacency.keys())

    def has_node(self, node: Any) -> bool:
        return node in self._adjacency

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        return to_node in self._adjacency.get(from_node, {})

    def node_count(self) -> int:
        return len(self._adjacency)

    def edge_count(self) -> int:
        total = sum(len(neighbors) for neighbors in self._adjacency.values())
        return total if self._directed else total // 2

    def __len__(self) -> int:
        return self.node_count()

    def __contains__(self, node: Any) -> bool:
        return self.has_node(node)