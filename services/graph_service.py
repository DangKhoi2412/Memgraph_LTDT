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
            
            # 2. Tải Cạnh (Kèm Trọng số) - Luôn có hướng
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
        """Đồng bộ dữ liệu xuống DB (Tách 3 bước để an toàn tuyệt đối)"""
        if not self.client.is_connected():
            return

        try:
            # --- BƯỚC 1: LƯU ĐỈNH (Nodes) ---
            # Dùng UNWIND để tạo hàng loạt cực nhanh
            if nodes:
                q_nodes = """
                UNWIND $batch as name
                MERGE (:Node {name: name})
                """
                # Clean dữ liệu node trước khi gửi
                node_data = [str(n).strip() for n in nodes]
                self.client.execute_query(q_nodes, {"batch": node_data})

            # --- BƯỚC 2: XÓA SẠCH CẠNH CŨ ---
            # Chạy query riêng biệt, dù có xóa được hay không cũng không ảnh hưởng bước sau
            self.client.execute_query("MATCH ()-[r:LINK]->() DELETE r")

            # --- BƯỚC 3: TẠO CẠNH MỚI (Edges) ---
            if edges:
                q_edges = """
                UNWIND $batch as e
                MATCH (u:Node {name: e.source})
                MATCH (v:Node {name: e.target})
                MERGE (u)-[r:LINK]->(v)
                SET r.weight = e.weight
                """
                
                # Chuẩn bị dữ liệu edge sạch
                edge_data = []
                for e in edges:
                    src = e.get('source') or e.get('src')
                    dst = e.get('target') or e.get('dst')
                    w = e.get('weight') or e.get('w', 1)
                    
                    if src and dst:
                        edge_data.append({
                            "source": str(src).strip(),
                            "target": str(dst).strip(),
                            "weight": int(w)
                        })
                
                # Chỉ gửi query nếu có dữ liệu cạnh hợp lệ
                if edge_data:
                    self.client.execute_query(q_edges, {"batch": edge_data})

            print(f"✅ [SYNC SUCCESS] Saved {len(nodes)} nodes, {len(edges)} edges.")

        except Exception as e:
            print(f"❌ [SYNC ERROR] {e}")
            
    def clear_db(self):
        if not self.client.is_connected(): return
        self.client.execute_query("MATCH (n) DETACH DELETE n")
    
    def build_networkx_graph(self, nodes, edges):
        """
        Luôn build nx.DiGraph (Có hướng).
        Bỏ tham số for_mst.
        """
        G = nx.DiGraph() 
        G.add_nodes_from(nodes)
        for e in edges:
            u, v, w = e['source'], e['target'], e['weight']
            # Trong DiGraph, u->v và v->u là 2 cạnh khác nhau, không cần check trùng kiểu vô hướng
            G.add_edge(u, v, weight=w)
        return G