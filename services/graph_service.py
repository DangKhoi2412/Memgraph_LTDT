from typing import List, Tuple, Dict, Any, Optional
import networkx as nx
import logging
from repositories.graph_repository import GraphRepository

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.repository = GraphRepository()
        self.last_load_successful: bool = False

    def load_from_db(self) -> Tuple[List[str], List[Dict[str, Any]], Dict[str, Any]]:
        try:
            nodes, edges, config = self.repository.get_all_nodes_and_edges()
            self.last_load_successful = True
            return nodes, edges, config
        except Exception as e:
            self.last_load_successful = False
            raise e

    def sync_to_db(self, nodes: List[str], edges: List[Dict[str, Any]], is_directed: bool = True, is_weighted: bool = True) -> Tuple[bool, str]:
        if not self.last_load_successful:
            msg = "⚠️ Safety Lock: Cannot sync because initial load failed."
            logger.warning(msg)
            return False, msg

        edges_to_sync = list(edges)
        if not is_directed:
            # For undirected graphs, ensure bidirectional storage (A->B and B->A)
            # This allows Cypher queries to traverse in both directions even if they follow standard directed semantics
            augmented_edges = []
            seen = set()
            
            for e in edges_to_sync:
                s, t, w = e.get('source'), e.get('target'), e.get('weight', 1)
                
                # Add original
                sig = (s, t)
                if sig not in seen:
                    augmented_edges.append(e)
                    seen.add(sig)
                
                # Add reverse
                rev_sig = (t, s)
                if rev_sig not in seen and s != t: # Avoid duplicating self-loops if handled elsewhere, but self-loops are fine
                    rev_edge = e.copy()
                    rev_edge['source'] = t
                    rev_edge['target'] = s
                    augmented_edges.append(rev_edge)
                    seen.add(rev_sig)
            
            edges_to_sync = augmented_edges

        # Auto-save config
        self.repository.save_config(is_directed, is_weighted)

        return self.repository.sync_graph(nodes, edges_to_sync)

    def clear_db(self) -> None:
        self.repository.clear_database()
    
    def build_networkx_graph(self, nodes: List[str], edges: List[Dict[str, Any]], is_directed: bool = True, is_weighted: bool = True) -> nx.Graph:
        G = nx.DiGraph() if is_directed else nx.Graph()
        G.add_nodes_from(nodes)
        
        for e in edges:
            u = e.get('source')
            v = e.get('target')
            w = e.get('weight', 1) if is_weighted else 1
            
            if u and v:
                G.add_edge(u, v, weight=w)
                
        return G