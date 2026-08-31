from search_engine.datastructures.priority_queue import PriorityQueue

def test_min_first_pops_lowest_priority_first():
    pq = PriorityQueue(min_first=True)
    pq.push("low_cost", priority=1)
    pq.push("high_cost", priority=10)
    pq.push("mid_cost", priority=5)

    assert pq.pop() == "low_cost"
    assert pq.pop() == "mid_cost"
    assert pq.pop() == "high_cost"


def test_max_first_pops_highest_priority_first():
    pq = PriorityQueue(min_first=False)
    pq.push("mediocre_doc", priority=0.3)
    pq.push("best_doc", priority=0.95)
    pq.push("okay_doc", priority=0.6)

    assert pq.pop() == "best_doc"
    assert pq.pop() == "okay_doc"
    assert pq.pop() == "mediocre_doc"


def test_pop_with_priority_returns_both():
    pq = PriorityQueue(min_first=False)
    pq.push("doc1", priority=0.8)
    item, priority = pq.pop_with_priority()
    assert item == "doc1"
    assert priority == 0.8


def test_ties_broken_by_insertion_order_not_by_comparing_items():
    pq = PriorityQueue(min_first=False)

    doc_a = {"id": 1, "title": "First"}
    doc_b = {"id": 2, "title": "Second"}
    doc_c = {"id": 3, "title": "Third"}

    pq.push(doc_a, priority=5.0)
    pq.push(doc_b, priority=5.0)
    pq.push(doc_c, priority=5.0)

    assert pq.pop() == doc_a
    assert pq.pop() == doc_b
    assert pq.pop() == doc_c


def test_is_empty_and_len():
    pq = PriorityQueue()
    assert pq.is_empty() is True
    assert len(pq) == 0

    pq.push("x", priority=1)
    assert pq.is_empty() is False
    assert len(pq) == 1