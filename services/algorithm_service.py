from algorithms.traversal import BFS, DFS
from algorithms.pathfinding import Dijkstra, BellmanFord
from algorithms.mst import MSTAlgorithm

class AlgorithmFactory:
    _algos = {
        "BFS": BFS(),
        "DFS": DFS(),
        "Dijkstra": Dijkstra(),
        "Bellman-Ford": BellmanFord(),
        "Prim (MST)": MSTAlgorithm('prim'),
        "Kruskal (MST)": MSTAlgorithm('kruskal')
    }

    @classmethod
    def get_algorithm(cls, name):
        return cls._algos.get(name.split(" ")[0])
    
    @staticmethod
    def is_mst(name):
        return "MST" in name