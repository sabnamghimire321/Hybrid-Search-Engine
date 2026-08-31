from search_engine.datastructures.graph import Graph

def test_add_edge_creates_both_nodes():
    g = Graph(directed=True)
    g.add_edge("A", "B")
    assert g.has_node("A")
    assert g.has_node("B")

def test_directed_edge_is_one_way():
    g = Graph(directed=True)
    g.add_edge("A", "B")
    assert g.has_edge("A", "B") is True
    assert g.has_edge("B", "A") is False

def test_undirected_edge_is_two_way():
    g = Graph(directed=False)
    g.add_edge("A", "B")
    assert g.has_edge("A", "B") is True
    assert g.has_edge("B", "A") is True

def test_neighbors_preserve_insertion_order():
    g = Graph()
    g.add_edge("A", "C")
    g.add_edge("A", "B")
    g.add_edge("A", "D")
    assert g.neighbors("A") == ["C", "B", "D"]

def test_neighbors_of_leaf_node_is_empty():
    g = Graph()
    g.add_edge("A", "B")
    assert g.neighbors("B") == []

def test_node_and_edge_counts_directed():
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "C")
    assert g.node_count() == 3
    assert g.edge_count() == 3

def test_node_and_edge_counts_undirected():
    g = Graph(directed=False)
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    assert g.node_count() == 3
    assert g.edge_count() == 2  
def test_len_and_contains():
    g = Graph()
    g.add_edge("A", "B")
    assert len(g) == 2
    assert "A" in g
    assert "Z" not in g