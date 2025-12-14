from .base import IAlgorithm
import networkx as nx

class Dijkstra(IAlgorithm):
    def execute(self, G, start_node, end_node):
        path = nx.dijkstra_path(G, start_node, end_node, weight='weight')
        cost = nx.dijkstra_path_length(G, start_node, end_node, weight='weight')
        return {"path_nodes": path, "cost": int(cost), "type": "path", "msg": "Đường đi ngắn nhất"}

class BellmanFord(IAlgorithm):
    def execute(self, G, start_node, end_node):
        path = nx.bellman_ford_path(G, start_node, end_node, weight='weight')
        cost = nx.bellman_ford_path_length(G, start_node, end_node, weight='weight')
        return {"path_nodes": path, "cost": int(cost), "type": "path", "msg": "Đường đi ngắn nhất"}
    
    