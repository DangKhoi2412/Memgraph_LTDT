from db.memgraph import MemgraphClient
import networkx as nx

class GraphService:
    def __init__(self):
        self.client = MemgraphClient()

    def load_from_db(self):
        """
        Tải dữ liệu an toàn từ Memgraph.
        Đã thêm cơ chế chống Crash khi dữ liệu bị lỗi (NoneType).
        """
        if not self.client.is_connected():
            return [], []

        try:
            # 1. Tải Đỉnh
            q_nodes = "MATCH (n:Node) RETURN n.name as name"
            # Ép kiểu str() để tránh lỗi nếu DB trả về null
            nodes = [str(r['name']) for r in self.client.execute_query(q_nodes) if r.get('name')]
            
            # 2. Tải Cạnh
            # Lấy source, target và weight
            q_edges = """
            MATCH (u:Node)-[r:LINK]->(v:Node) 
            RETURN u.name as source, v.name as target, r.weight as weight
            """
            raw_edges = self.client.execute_query(q_edges)
            
            edges = []
            for r in raw_edges:
                src = r.get('source')
                tgt = r.get('target')
                w_raw = r.get('weight')

                # SAFETY CHECK: Xử lý trọng số an toàn
                # Nếu DB lưu bậy bạ (null, string rác), mặc định về 1 để App không bị sập
                weight = 1
                try:
                    if w_raw is not None:
                        weight = int(w_raw)
                except:
                    weight = 1
                
                # Chỉ lấy cạnh khi có đủ 2 đầu mút
                if src and tgt:
                    edges.append({
                        "source": str(src), 
                        "target": str(tgt), 
                        "weight": weight
                    })
            
            print(f"📥 [LOAD] Đã tải: {len(nodes)} đỉnh, {len(edges)} cạnh.")
            return nodes, edges

        except Exception as e:
            print(f"❌ [LOAD ERROR] {e}")
            return [], []

    def sync_to_db(self, nodes, edges):
        """
        Lưu dữ liệu xuống Memgraph.
        SỬ DỤNG CHIẾN THUẬT 'MERGE-ALL' ĐỂ KHÔNG BAO GIỜ MẤT CẠNH.
        """
        if not self.client.is_connected():
            return

        try:
            # 1. Chuẩn hóa dữ liệu đầu vào
            clean_nodes = [{"name": str(n).strip()} for n in nodes if n]
            
            clean_edges = []
            for e in edges:
                # Hỗ trợ cả 2 loại key (cũ và mới) để tương thích với UI
                src = e.get('source') or e.get('src')
                dst = e.get('target') or e.get('dst')
                w = e.get('weight') or e.get('w', 1)
                
                if src and dst:
                    clean_edges.append({
                        "source": str(src).strip(), 
                        "target": str(dst).strip(), 
                        "weight": int(w)
                    })

            # 2. Reset Graph (Xóa sạch cũ)
            self.client.execute_query("MATCH (n) DETACH DELETE n")

            # 3. Tạo Đỉnh (Batch Nodes)
            if clean_nodes:
                q_nodes = "UNWIND $batch as row MERGE (:Node {name: row.name})"
                self.client.execute_query(q_nodes, {"batch": clean_nodes})

            # 4. Tạo Cạnh (Batch Edges) - PHẦN SỬA QUAN TRỌNG NHẤT
            # Thay vì MATCH (tìm), ta dùng MERGE cho cả Node đầu và cuối.
            # Điều này ép buộc Database phải đảm bảo Node tồn tại rồi mới nối cạnh.
            if clean_edges:
                q_edges = """
                UNWIND $batch as row
                MERGE (u:Node {name: row.source})
                MERGE (v:Node {name: row.target})
                MERGE (u)-[r:LINK]->(v)
                SET r.weight = row.weight
                """
                self.client.execute_query(q_edges, {"batch": clean_edges})

            print(f"✅ [SYNC] Đã lưu {len(clean_nodes)} đỉnh, {len(clean_edges)} cạnh.")

        except Exception as e:
            print(f"❌ [SYNC ERROR] {e}")

    def build_networkx_graph(self, nodes, edges, for_mst=False):
        """Helper để tạo đồ thị NetworkX dùng cho thuật toán"""
        G = nx.Graph() if for_mst else nx.DiGraph()
        G.add_nodes_from(nodes)
        
        for e in edges:
            u = e.get('source') or e.get('src')
            v = e.get('target') or e.get('dst')
            w = e.get('weight') or e.get('w', 1)
            
            if u and v:
                if for_mst and G.has_edge(u, v):
                    if w < G[u][v]['weight']:
                        G.add_edge(u, v, weight=w)
                else:
                    G.add_edge(u, v, weight=w)
        return G