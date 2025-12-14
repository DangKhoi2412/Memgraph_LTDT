from .base import IAlgorithm
import networkx as nx

class MSTAlgorithm(IAlgorithm):
    def __init__(self, algo_type='prim'):
        self.algo_type = algo_type

    def execute(self, G, start_node=None, end_node=None):
        if G.is_directed(): 
            G = G.to_undirected()
            
        mst = nx.minimum_spanning_tree(G, weight='weight', algorithm=self.algo_type)
        return {
            "mst_edges": list(mst.edges()), 
            "cost": int(mst.size(weight='weight')), 
            "type": "mst", 
            "is_mst_mode": True,
            "msg": f"Cây khung nhỏ nhất ({self.algo_type})"
        }