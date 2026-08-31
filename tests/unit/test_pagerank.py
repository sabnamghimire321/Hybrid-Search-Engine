import math

from search_engine.datastructures.graph import Graph
from search_engine.ranking.pagerank import PageRank

def test_empty_graph_returns_empty_dict():
    graph = Graph(directed=True)
    ranks = PageRank(graph).compute()
    assert ranks == {}

def test_single_isolated_node_gets_full_rank():
    graph = Graph(directed=True)
    graph.add_node("A")
    ranks = PageRank(graph).compute()
    assert math.isclose(ranks["A"], 1.0, abs_tol=1e-6)

def test_two_node_mutual_link_splits_evenly():
    """A <-> B, symmetric -- both should converge to equal rank (0.5 each)."""
    graph = Graph(directed=True)
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")

    ranks = PageRank(graph).compute()
    assert math.isclose(ranks["A"], 0.5, abs_tol=1e-4)
    assert math.isclose(ranks["B"], 0.5, abs_tol=1e-4)

def test_hub_page_gets_higher_rank_than_its_linkers():
    graph = Graph(directed=True)
    graph.add_edge("B", "A")
    graph.add_edge("C", "A")
    graph.add_edge("D", "A")

    ranks = PageRank(graph).compute()
    assert ranks["A"] > ranks["B"]
    assert ranks["A"] > ranks["C"]
    assert ranks["A"] > ranks["D"]


def test_ranks_sum_to_approximately_one():
    graph = Graph(directed=True)
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    graph.add_edge("A", "D")

    ranks = PageRank(graph).compute()
    assert math.isclose(sum(ranks.values()), 1.0, abs_tol=1e-4)


def test_dangling_node_does_not_leak_rank():
    graph = Graph(directed=True)
    graph.add_edge("A", "D")
    graph.add_edge("B", "D")
    graph.add_node("D")

    ranks = PageRank(graph).compute()
    assert math.isclose(sum(ranks.values()), 1.0, abs_tol=1e-4)
    assert ranks["D"] > 0


def test_more_iterations_converges_closer_to_fixed_point():
    graph = Graph(directed=True)
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    graph.add_edge("A", "D")
    graph.add_edge("D", "A")

    loose = PageRank(graph, max_iterations=1, tolerance=1e-9).compute()
    tight = PageRank(graph, max_iterations=100, tolerance=1e-9).compute()

    assert not math.isclose(loose["A"], tight["A"], abs_tol=1e-6)