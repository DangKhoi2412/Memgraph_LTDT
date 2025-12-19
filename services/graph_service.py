from db.memgraph import MemgraphClient
import networkx as nx

class GraphService:
    def __init__(self):
        self.client = MemgraphClient()

    def load_from_db(self):
        """Tải dữ liệu từ DB lên App"""
        if not self.client.is_connected():
            return [], []

        try:
            # 1. Tải Đỉnh
            q_nodes = "MATCH (n:Node) RETURN n.name as name"
            nodes = [str(r['name']) for r in self.client.execute_query(q_nodes) if r.get('name')]
            
            # 2. Tải Cạnh (Kèm Trọng số)
            q_edges = """
            MATCH (u:Node)-[r:LINK]->(v:Node) 
            RETURN u.name as source, v.name as target, r.weight as weight
            """
            raw_edges = self.client.execute_query(q_edges)
            
            edges = []
            for r in raw_edges:
                src = r.get('source')
                tgt = r.get('target')
                w = 1
                if r.get('weight') is not None:
                    try: w = int(r['weight'])
                    except: w = 1

                if src and tgt:
                    edges.append({
                        "source": str(src), 
                        "target": str(tgt), 
                        "weight": w 
                    })
            
            print(f"📥 [LOAD] Đã tải: {len(nodes)} đỉnh, {len(edges)} cạnh.")
            return nodes, edges

        except Exception as e:
            print(f"❌ [LOAD ERROR] {e}")
            return [], []

    def sync_to_db(self, nodes, edges):
        """Đồng bộ dữ liệu xuống DB (Ghi đè an toàn)"""
        if not self.client.is_connected():
            return

        try:
            # 1. Đảm bảo Nodes tồn tại (Tạo Node trước)
            for node in nodes:
                self.client.execute_query(
                    "MERGE (:Node {name: $name})",
                    {"name": str(node).strip()}
                )

            # 2. XÓA SẠCH CẠNH CŨ (Reset kết nối)
            self.client.execute_query("MATCH ()-[r:LINK]->() DELETE r")

            # 3. TẠO CẠNH MỚI (Dùng MERGE Node để CHỐNG LỖI mất cạnh)
            # LƯU Ý: Tuyệt đối không dùng MATCH ở đây
            for e in edges:
                src = e.get('source') or e.get('src')
                dst = e.get('target') or e.get('dst')
                w = e.get('weight') or e.get('w', 1)

                if src and dst:
                    q_edge = """
                    MERGE (u:Node {name: $src})
                    MERGE (v:Node {name: $dst})
                    MERGE (u)-[r:LINK]->(v)
                    SET r.weight = $w
                    """
                    self.client.execute_query(q_edge, {
                        "src": str(src).strip(),
                        "dst": str(dst).strip(),
                        "w": int(w)
                    })

            print(f"✅ [SYNC SUCCESS] Saved {len(nodes)} nodes, {len(edges)} edges.")

        except Exception as e:
            print(f"❌ [SYNC ERROR] {e}")

    def clear_db(self):
        if not self.client.is_connected(): return
        self.client.execute_query("MATCH (n) DETACH DELETE n")
    
    def build_networkx_graph(self, nodes, edges, for_mst=False):
        G = nx.Graph() if for_mst else nx.DiGraph()
        G.add_nodes_from(nodes)
        for e in edges:
            u, v, w = e['source'], e['target'], e['weight']
            if for_mst and G.has_edge(u, v):
                if w < G[u][v]['weight']: G.add_edge(u, v, weight=w)
            else:
                G.add_edge(u, v, weight=w)
        return G