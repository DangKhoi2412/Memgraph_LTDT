from algorithms.traversal import BFS, DFS
from algorithms.pathfinding import Dijkstra, BellmanFord
# Đã xóa import MST

class AlgorithmFactory:
    _algos = {
        "BFS": BFS(),
        "DFS": DFS(),
        "Dijkstra": Dijkstra(),
        "Bellman-Ford": BellmanFord()
        # Đã xóa Prim và Kruskal
    }

    @classmethod
    def get_algorithm(cls, name):
        # Lấy tên thuật toán an toàn hơn
        key = name.split(" ")[0]
        return cls._algos.get(key)
    
    # Đã xóa staticmethod is_mst vì không còn dùng