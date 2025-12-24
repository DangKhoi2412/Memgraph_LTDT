from .base import IAlgorithm
import heapq

class Prim(IAlgorithm):
    def execute(self, G, start_node, end_node=None):
        mst_edges = []
        total_cost = 0
        visited = set()
        
        if not start_node and len(G.nodes()) > 0:
            start_node = list(G.nodes())[0]

        if start_node:
            visited.add(start_node)
            edges = []
            for v, attr in G[start_node].items():
                w = attr.get('weight', 1)
                heapq.heappush(edges, (w, start_node, v))
            
            while edges:
                weight, u, v = heapq.heappop(edges)
                if v not in visited:
                    visited.add(v)
                    mst_edges.append((u, v))
                    total_cost += weight
                    for neighbor, attr in G[v].items():
                        if neighbor not in visited:
                            w = attr.get('weight', 1)
                            heapq.heappush(edges, (w, v, neighbor))
                            
        return {
            "mst_edges": mst_edges,
            "cost": total_cost,
            "type": "mst",
            "msg": "Thuật toán Prim"
        }

class Kruskal(IAlgorithm):
    def execute(self, G, start_node=None, end_node=None):
        mst_edges = []
        total_cost = 0
        edges = []
        
        for u, v, attr in G.edges(data=True):
            edges.append((attr.get('weight', 1), u, v))
        
        edges.sort()
        
        parent = {node: node for node in G.nodes()}
        
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False
            
        for weight, u, v in edges:
            if union(u, v):
                mst_edges.append((u, v))
                total_cost += weight
                
        return {
            "mst_edges": mst_edges,
            "cost": total_cost,
            "type": "mst",
            "msg": "Thuật toán Kruskal"
        }
