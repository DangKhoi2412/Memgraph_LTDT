from pyvis.network import Network
import tempfile

class Visualizer:
    @staticmethod
    def render(G, result, is_mst=False):
        # --- SỬA Ở ĐÂY: height="800px" cho đồng bộ với app.py ---
        net = Network(height="800px", width="100%", bgcolor="#FFFFFF", font_color="#000", directed=not is_mst)
        
        path = result.get('path_nodes', [])
        mst_edges = result.get('mst_edges', [])

        for n in G.nodes():
            color = "#90CAF9"
            if n in path:
                color = "#FFD54F"
                if n == path[0]: color = "#66BB6A"
                if n == path[-1] and len(path)>1: color = "#EF5350"
            if mst_edges and G.degree[n] > 0: color = "#FFD54F"
            net.add_node(n, label=n, color=color, size=25, borderWidth=1)

        for u, v, d in G.edges(data=True):
            color, width = "#CFD8DC", 1
            if mst_edges:
                if (u, v) in mst_edges or (v, u) in mst_edges: color = "#FF6F00"; width = 4
            elif path:
                try:
                    if u in path and v in path:
                        idx = path.index(u)
                        if idx < len(path)-1 and path[idx+1] == v: color = "#FF6F00"; width = 4
                except: pass
            
            net.add_edge(u, v, label=str(d.get('weight', 1)), color=color, width=width)

        # --- SỬA Ở ĐÂY: Tăng springLength lên 200 để hình bung rộng ra ---
        net.set_options('{"physics": {"forceAtlas2Based": {"gravitationalConstant": -100, "springLength": 120}, "solver": "forceAtlas2Based"}}')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f: return f.read()