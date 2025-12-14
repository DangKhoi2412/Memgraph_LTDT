from .base import IAlgorithm
import networkx as nx

class BFS(IAlgorithm):
    def execute(self, G, start_node, end_node=None):
        edges = list(nx.bfs_edges(G, start_node))
        path = [start_node] + [v for u, v in edges]
        return {"path_nodes": path, "type": "traversal", "msg": f"BFS duyệt {len(path)} đỉnh"}

class DFS(IAlgorithm):
    def execute(self, G, start_node, end_node=None):
        path = list(nx.dfs_preorder_nodes(G, start_node))
        return {"path_nodes": path, "type": "traversal", "msg": f"DFS duyệt {len(path)} đỉnh"}