from algorithms.traversal import BFS, DFS
from algorithms.pathfinding import Dijkstra, BellmanFord

class AlgorithmFactory:
    _algos = {
        "BFS": BFS(),
        "DFS": DFS(),
        "Dijkstra": Dijkstra(),
        "Bellman-Ford": BellmanFord()
    }

    @classmethod
    def get_algorithm(cls, name: str):
        key = name.split(" ")[0]
        return cls._algos.get(key)