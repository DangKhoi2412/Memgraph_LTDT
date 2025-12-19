from typing import List, Tuple, Dict, Any, Optional
import networkx as nx
import logging
from repositories.graph_repository import GraphRepository

logger = logging.getLogger(__name__)

class GraphService:
    """
    Service layer handling graph business logic.
    mediates between the controller (app.py) and the data access layer (GraphRepository).
    """
    def __init__(self):
        self.repository = GraphRepository()
        self.last_load_successful: bool = False

    def load_from_db(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Load nodes and edges from repository.
        Raises exception if load fails to prevent invalid state sync.
        """
        try:
            nodes, edges = self.repository.get_all_nodes_and_edges()
            self.last_load_successful = True
            return nodes, edges
        except Exception as e:
            self.last_load_successful = False
            # Log is handled in repository, but we need to propagate error to UI
            raise e

    def sync_to_db(self, nodes: List[str], edges: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Sync current application state to database.
        Includes safety check: blocks sync if initial load failed.
        """
        if not self.last_load_successful:
            msg = "⚠️ Safety Lock: Cannot sync because initial load failed."
            logger.warning(msg)
            return False, msg

        return self.repository.sync_graph(nodes, edges)

    def clear_db(self) -> None:
        """Clear all data from the database."""
        self.repository.clear_database()
    
    def build_networkx_graph(self, nodes: List[str], edges: List[Dict[str, Any]]) -> nx.DiGraph:
        """
        Convert raw node/edge data into a NetworkX DiGraph.
        """
        G = nx.DiGraph() 
        G.add_nodes_from(nodes)
        
        for e in edges:
            u = e.get('source')
            v = e.get('target')
            w = e.get('weight', 1)
            
            if u and v:
                G.add_edge(u, v, weight=w)
                
        return G