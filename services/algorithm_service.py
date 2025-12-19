from algorithms.traversal import BFS, DFS
from algorithms.pathfinding import Dijkstra, BellmanFord

class AlgorithmFactory:
    """Factory to retrieve algorithm instances by name."""
    
    _algos = {
        "BFS": BFS(),
        "DFS": DFS(),
        "Dijkstra": Dijkstra(),
        "Bellman-Ford": BellmanFord()
    }

    @classmethod
    def get_algorithm(cls, name: str):
        """Get algorithm instance based on name (e.g. 'BFS' or 'Dijkstra (Shortest Path)')."""
        # Robust name handling
        key = name.split(" ")[0]
        return cls._algos.get(key)