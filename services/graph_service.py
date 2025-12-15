from db.memgraph import MemgraphClient
import networkx as nx

class GraphService:
    def __init__(self):
        self.client = MemgraphClient()

    def load_from_db(self):
        """Đọc dữ liệu từ Memgraph lên App (Dùng thuộc tính 'name')"""
        if not self.client.is_connected(): return None, None
        try:
            # 1. Tải Đỉnh: Dùng thuộc tính 'name'
            q_nodes = "MATCH (n:Node) RETURN n.name as name"
            # Lọc bỏ giá trị None nếu có
            nodes = [r['name'] for r in self.client.execute_query(q_nodes) if r.get('name')]
            
            # 2. Tải Cạnh: Tìm theo 'name' của 2 đầu
            q_edges = """
            MATCH (u:Node)-[r:LINK]->(v:Node) 
            RETURN u.name as src, v.name as dst, r.weight as w
            """
            edges = [{"src": r['src'], "target": r['dst'], "w": int(r['w'])} 
                     for r in self.client.execute_query(q_edges)]
            
            print(f"📥 [LOAD] Đã tải: {len(nodes)} đỉnh, {len(edges)} cạnh.")
            return nodes, edges
        except Exception as e:
            print(f"❌ [LOAD ERROR] {e}")
            return [], []

    def sync_to_db(self, nodes, edges):
        """Ghi đè dữ liệu xuống Memgraph (Dùng 'name' + Xử lý khoảng trắng)"""
        if not self.client.is_connected():
            print("⚠️ Memgraph chưa kết nối.")
            return

        print(f"🚀 [SYNC] Bắt đầu lưu {len(nodes)} đỉnh và {len(edges)} cạnh...")

        try:
            # BƯỚC 1: Xóa sạch dữ liệu cũ
            self.client.execute_query("MATCH (n) DETACH DELETE n")
            
            # BƯỚC 2: TẠO ĐỈNH (Dùng 'name')
            for n in nodes:
                # .strip() cực quan trọng để xóa khoảng trắng thừa (ví dụ "A " -> "A")
                clean_name = str(n).strip()
                self.client.execute_query(
                    "MERGE (:Node {name: $name})", 
                    {"name": clean_name}
                )
            
            # BƯỚC 3: TẠO CẠNH (Tìm theo 'name' để nối)
            count = 0
            for e in edges:
                src = str(e['src']).strip()
                dst = str(e['target']).strip()
                w = int(e['w'])
                
                # Query tìm 2 đỉnh bằng 'name' rồi nối
                query = """
                MATCH (u:Node {name: $src}), (v:Node {name: $dst})
                MERGE (u)-[r:LINK]->(v)
                SET r.weight = $w
                RETURN u.name
                """
                
                res = self.client.execute_query(query, {"src": src, "dst": dst, "w": w})
                
                if res: 
                    count += 1
                else: 
                    # Nếu log hiện dòng này -> Tên đỉnh bị lệch
                    print(f"⚠️ CẢNH BÁO: Không nối được {src} -> {dst} (Kiểm tra xem đỉnh đã tạo chưa?)")

            print(f"✅ [SYNC] Hoàn tất! Đã lưu thành công {count}/{len(edges)} cạnh.")

        except Exception as e:
            print(f"❌ [SYNC ERROR] {e}")

    def build_networkx_graph(self, nodes, edges, for_mst=False):
        """Helper tạo đồ thị NetworkX cho thuật toán"""
        if for_mst:
            G = nx.Graph()
            for n in nodes: G.add_node(n)
            edge_map = {}
            for e in edges:
                key = tuple(sorted((e['src'], e['target'])))
                edge_map[key] = min(edge_map.get(key, float('inf')), int(e['w']))
            for (u,v), w in edge_map.items(): G.add_edge(u, v, weight=w)
        else:
            G = nx.DiGraph()
            for n in nodes: G.add_node(n)
            for e in edges: G.add_edge(e['src'], e['target'], weight=int(e['w']))
        return G