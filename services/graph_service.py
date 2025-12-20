from typing import List, Tuple, Dict, Any, Optional
import networkx as nx
import logging
from repositories.graph_repository import GraphRepository

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.repository = GraphRepository()
        self.last_load_successful: bool = False

    def load_from_db(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        try:
            nodes, edges = self.repository.get_all_nodes_and_edges()
            self.last_load_successful = True
            return nodes, edges
        except Exception as e:
            self.last_load_successful = False
            raise e

    def sync_to_db(self, nodes: List[str], edges: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if not self.last_load_successful:
            msg = "⚠️ Safety Lock: Cannot sync because initial load failed."
            logger.warning(msg)
            return False, msg

        return self.repository.sync_graph(nodes, edges)

    def clear_db(self) -> None:
        self.repository.clear_database()
    
    def build_networkx_graph(self, nodes: List[str], edges: List[Dict[str, Any]]) -> nx.DiGraph:
        G = nx.DiGraph() 
        G.add_nodes_from(nodes)
        
        for e in edges:
            u = e.get('source')
            v = e.get('target')
            w = e.get('weight', 1)
            
            if u and v:
                G.add_edge(u, v, weight=w)
                
        return G