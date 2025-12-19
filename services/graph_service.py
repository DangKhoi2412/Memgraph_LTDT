from db.memgraph import MemgraphClient
import networkx as nx

class GraphService:
    def __init__(self):
        self.client = MemgraphClient()

    def load_from_db(self):
        """
        Đọc dữ liệu từ Memgraph lên App.
        CHUẨN HÓA OUTPUT: 
          - nodes: List[str] -> ['A', 'B']
          - edges: List[dict] -> [{'source': 'A', 'target': 'B', 'weight': 1}, ...]
        """
        if not self.client.is_connected():
            return [], []

        try:
            # 1. Tải Đỉnh
            q_nodes = "MATCH (n:Node) RETURN n.name as name"
            nodes = [r['name'] for r in self.client.execute_query(q_nodes) if r.get('name')]
            
            # 2. Tải Cạnh (Mapping ngay tại câu query DB để trả về key chuẩn)
            q_edges = """
            MATCH (u:Node)-[r:LINK]->(v:Node) 
            RETURN u.name as source, v.name as target, r.weight as weight
            """
            raw_edges = self.client.execute_query(q_edges)
            
            # Xử lý an toàn dữ liệu trả về
            edges = []
            for r in raw_edges:
                if r.get('source') and r.get('target'):
                    edges.append({
                        "source": r['source'], 
                        "target": r['target'], 
                        "weight": int(r.get('weight', 1))
                    })
            
            print(f"📥 [LOAD] Đã tải: {len(nodes)} đỉnh, {len(edges)} cạnh.")
            return nodes, edges

        except Exception as e:
            print(f"❌ [LOAD ERROR] {e}")
            return [], []

    def sync_to_db(self, nodes, edges):
        """
        Ghi đè dữ liệu xuống Memgraph dùng BATCH PROCESSING (UNWIND).
        Tốc độ nhanh, nguyên tử (atomic), ít lỗi.
        """
        if not self.client.is_connected():
            print("⚠️ Memgraph chưa kết nối.")
            return

        print(f"🚀 [SYNC BATCH] Đang xử lý {len(nodes)} đỉnh và {len(edges)} cạnh...")

        try:
            # BƯỚC 1: CHUẨN HÓA DỮ LIỆU ĐẦU VÀO
            clean_nodes = [{"name": str(n).strip()} for n in nodes]
            
            clean_edges = []
            for e in edges:
                # Ưu tiên lấy key chuẩn 'source'/'target', fallback sang key cũ ('src', 'dst') nếu có
                src = str(e.get('source', e.get('src', ''))).strip()
                dst = str(e.get('target', e.get('dst', e.get('target', '')))).strip()
                w = int(e.get('weight', e.get('w', 1)))
                
                if src and dst:
                    clean_edges.append({"source": src, "target": dst, "weight": w})

            # BƯỚC 2: RESET GRAPH (Xóa cũ)
            self.client.execute_query("MATCH (n) DETACH DELETE n")

            # BƯỚC 3: BATCH INSERT NODES (1 Query duy nhất)
            if clean_nodes:
                q_create_nodes = """
                UNWIND $batch_nodes as row
                MERGE (:Node {name: row.name})
                """
                self.client.execute_query(q_create_nodes, {"batch_nodes": clean_nodes})

            # BƯỚC 4: BATCH INSERT EDGES (1 Query duy nhất)
            if clean_edges:
                q_create_edges = """
                UNWIND $batch_edges as row
                MATCH (u:Node {name: row.source}), (v:Node {name: row.target})
                MERGE (u)-[r:LINK]->(v)
                SET r.weight = row.weight
                """
                self.client.execute_query(q_create_edges, {"batch_edges": clean_edges})

            print(f"✅ [SYNC SUCCESS] Hoàn tất đồng bộ!")

        except Exception as e:
            print(f"❌ [SYNC ERROR] {e}")

    def build_networkx_graph(self, nodes, edges, for_mst=False):
        """Tạo đồ thị NetworkX từ danh sách cạnh chuẩn hóa"""
        if for_mst:
            G = nx.Graph()
            G.add_nodes_from(nodes)
            edge_map = {}
            for e in edges:
                u = e.get('source', e.get('src'))
                v = e.get('target', e.get('dst', e.get('target')))
                w = int(e.get('weight', e.get('w', 1)))
                
                if u and v:
                    # Vô hướng: (A,B) là (B,A), lấy min weight
                    key = tuple(sorted((u, v)))
                    edge_map[key] = min(edge_map.get(key, float('inf')), w)
            
            for (u, v), w in edge_map.items():
                G.add_edge(u, v, weight=w)
        else:
            G = nx.DiGraph()
            G.add_nodes_from(nodes)
            for e in edges:
                u = e.get('source', e.get('src'))
                v = e.get('target', e.get('dst', e.get('target')))
                w = int(e.get('weight', e.get('w', 1)))
                
                if u and v:
                    G.add_edge(u, v, weight=w)
        return G