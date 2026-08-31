from search_engine.algorithms.traversal import bfs, bfs_shortest_path, dfs
from search_engine.datastructures.graph import Graph

def _diamond_graph() -> Graph:
    """
        A
       / \\
      B   C
       \\ /
        D
        |
        E
    """
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")
    g.add_edge("D", "E")
    return g

def test_bfs_visits_level_by_level():
    g = _diamond_graph()
    assert bfs(g, "A") == ["A", "B", "C", "D", "E"]

def test_bfs_from_nonexistent_node_returns_empty():
    g = _diamond_graph()
    assert bfs(g, "Z") == []

def test_bfs_does_not_visit_disconnected_nodes():
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_node("Z")  
    result = bfs(g, "A")
    assert "Z" not in result

def test_dfs_goes_deep_before_wide():
    g = _diamond_graph()
    assert dfs(g, "A") == ["A", "B", "D", "E", "C"]

def test_dfs_from_nonexistent_node_returns_empty():
    g = _diamond_graph()
    assert dfs(g, "Z") == []

def test_bfs_shortest_path_picks_the_shorter_route():
    g = _diamond_graph()
    g.add_edge("A", "E")  
    path = bfs_shortest_path(g, "A", "E")
    assert path == ["A", "E"]

def test_bfs_shortest_path_without_shortcut():
    g = _diamond_graph()
    path = bfs_shortest_path(g, "A", "E")
    assert path == ["A", "B", "D", "E"]

def test_bfs_shortest_path_same_start_and_target():
    g = _diamond_graph()
    assert bfs_shortest_path(g, "A", "A") == ["A"]

def test_bfs_shortest_path_unreachable_returns_none():
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_node("Z")  
    assert bfs_shortest_path(g, "A", "Z") is None