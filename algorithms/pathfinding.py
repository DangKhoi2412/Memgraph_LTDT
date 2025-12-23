from .base import IAlgorithm
import heapq
import math

class Dijkstra(IAlgorithm):
    def execute(self, G, start_node, end_node):
        dist = {node: float('inf') for node in G.nodes()}
        dist[start_node] = 0
        parent = {node: None for node in G.nodes()}
        pq = [(0, start_node)]
        while pq:
            current_dist, u = heapq.heappop(pq)
            if u == end_node:
                break
            if current_dist > dist[u]:
                continue
            for v, attr in G[u].items():
                weight = attr.get('weight', 1)
                new_dist = current_dist + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    parent[v] = u
                    heapq.heappush(pq, (new_dist, v))
        path = []
        curr = end_node
        if dist[end_node] != float('inf'):
            while curr is not None:
                path.insert(0, curr)
                curr = parent[curr]
        
        return {
            "path_nodes": path, 
            "cost": dist[end_node] if dist[end_node] != float('inf') else 0,
            "type": "path", 
            "msg": "Dijkstra (Thủ công)"
        }

class BellmanFord(IAlgorithm):
    def execute(self, G, start_node, end_node):
        dist = {node: float('inf') for node in G.nodes()}
        dist[start_node] = 0
        parent = {node: None for node in G.nodes()}
        nodes = list(G.nodes())
        edges = []
        
        for u, v, attr in G.edges(data=True):
            edges.append((u, v, attr.get('weight', 1)))
        for _ in range(len(nodes) - 1):
            changed = False
            for u, v, w in edges:
                if dist[u] != float('inf') and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u
                    changed = True
            if not changed:
                break
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                 return {
                    "path_nodes": [], 
                    "cost": 0, 
                    "type": "path", 
                    "msg": "Lỗi: Đồ thị có chu trình âm!"
                }
        path = []
        curr = end_node
        if dist[end_node] != float('inf'):
            while curr is not None:
                path.insert(0, curr)
                curr = parent[curr]
        return {
            "path_nodes": path, 
            "cost": dist[end_node] if dist[end_node] != float('inf') else 0,
            "type": "path", 
            "msg": "Bellman-Ford (Thủ công)"
        }