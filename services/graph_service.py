import networkx as nx
from db.memgraph import MemgraphClient

class GraphService:
    def __init__(self):
        self.db = MemgraphClient()

    def sync_to_db(self, nodes, edges):
        """Ghi đè dữ liệu từ App vào Memgraph"""
        if not self.db.is_connected(): return
        
        self.db.execute_query("MATCH (n) DETACH DELETE n")
        
        for n in nodes:
            self.db.execute_query("CREATE (:Node {id: $id})", {"id": n})
            
        for e in edges:
            query = """
            MATCH (u:Node {id: $src}), (v:Node {id: $dst})
            MERGE (u)-[:LINK {weight: $w}]->(v)
            """
            self.db.execute_query(query, {"src": e['src'], "dst": e['target'], "w": e['w']})

    def load_from_db(self):
        """Đọc từ Memgraph ra danh sách nodes/edges"""
        if not self.db.is_connected(): return None, None
        
        res_nodes = self.db.execute_query("MATCH (n:Node) RETURN n.id as id")
        nodes = [r['id'] for r in res_nodes]
        
        res_edges = self.db.execute_query("MATCH (u)-[r:LINK]->(v) RETURN u.id as src, v.id as dst, r.weight as w")
        edges = [{"src": r['src'], "target": r['dst'], "w": int(r['w'])} for r in res_edges]
        
        return nodes, edges

    def build_networkx_graph(self, nodes, edges, for_mst=False):
        if for_mst:
            G = nx.Graph()
            for n in nodes: G.add_node(n)
            edge_map = {}
            for e in edges:
                key = tuple(sorted((e['src'], e['target'])))
                edge_map[key] = min(edge_map.get(key, float('inf')), e['w'])
            for (u,v), w in edge_map.items(): G.add_edge(u, v, weight=w)
        else:
            G = nx.DiGraph()
            for n in nodes: G.add_node(n)
            for e in edges: G.add_edge(e['src'], e['target'], weight=e['w'])
        return G