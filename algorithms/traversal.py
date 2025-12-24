from .base import IAlgorithm
import networkx as nx
from collections import deque

class BFS(IAlgorithm):
    def execute(self, G, start_node, end_node=None):
        visited = set()
        queue = deque([start_node])
        path = []  
        
        visited.add(start_node)
        
        while queue:
            u = queue.popleft()
            path.append(u)
            for v in G[u]:
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
                    
        return {
            "path_nodes": path, 
            "type": "traversal", 
            "msg": f"BFS duyệt {len(path)} đỉnh (Thủ công)"
        }

class DFS(IAlgorithm):
    def execute(self, G, start_node, end_node=None):
        visited = set()
        stack = [start_node]
        path = []
        while stack:
            u = stack.pop()
            
            if u not in visited:
                visited.add(u)
                path.append(u)
                neighbors = list(G[u])
                for v in reversed(neighbors):
                    if v not in visited:
                        stack.append(v)
        return {
            "path_nodes": path, 
            "type": "traversal", 
            "msg": f"DFS duyệt {len(path)} đỉnh (Thủ công)"
        }