from search_engine.datastructures.graph import Graph

class PageRank:
    def __init__(
        self,
        graph: Graph,
        damping: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> None:
        self._graph = graph
        self._damping = damping
        self._max_iterations = max_iterations
        self._tolerance = tolerance

    def compute(self) -> dict:
        nodes = self._graph.nodes()
        n = len(nodes)
        if n == 0:
            return {}

        rank = {node: 1.0 / n for node in nodes}
        random_jump_share = (1 - self._damping) / n

        for _ in range(self._max_iterations):
            new_rank = {node: random_jump_share for node in nodes}
            dangling_mass = 0.0

            for node in nodes:
                out_links = self._graph.neighbors(node)
                if not out_links:
                    dangling_mass += rank[node]
                    continue

                contribution = rank[node] / len(out_links)
                for neighbor in out_links:
                    new_rank[neighbor] += self._damping * contribution

            if dangling_mass > 0:
                redistribute = self._damping * dangling_mass / n
                for node in nodes:
                    new_rank[node] += redistribute

            diff = sum(abs(new_rank[node] - rank[node]) for node in nodes)
            rank = new_rank

            if diff < self._tolerance:
                break

        return rank