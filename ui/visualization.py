from pyvis.network import Network
import tempfile
import networkx as nx

class Visualizer:
    @staticmethod
    def render(G: nx.DiGraph, result: dict, is_mst: bool = False) -> str:
        """
        Render the NetworkX graph to an HTML string using Pyvis.
        Highlights the path or nodes based on the algorithm result.
        """
        # Initialize Network
        net = Network(height="550px", width="100%", bgcolor="#FFFFFF", font_color="#000", directed=True)
        
        path = result.get('path_nodes', [])
        mst_edges = result.get('mst_edges', [])

        # Add Nodes
        for n in G.nodes():
            color = "#90CAF9" # Default Blue
            if n in path:
                color = "#FFD54F" # Highlight Yellow
                if n == path[0]: color = "#66BB6A" # Start Green
                if n == path[-1] and len(path) > 1: color = "#EF5350" # End Red
            
            # MST Highlight (Legacy support)
            if mst_edges and G.degree[n] > 0: 
                color = "#FFD54F"
            
            net.add_node(n, label=str(n), color=color, size=25, borderWidth=1)

        # Add Edges
        for u, v, d in G.edges(data=True):
            color, width = "#CFD8DC", 1 # Default Grey
            
            # Highlight Logic
            if path:
                try:
                    # Check if edge u->v is in the path
                    if u in path and v in path:
                        idx = path.index(u)
                        # Ensure v is the NEXT node in the path sequence
                        if idx < len(path)-1 and path[idx+1] == v: 
                            color = "#FF6F00"
                            width = 4
                except ValueError: 
                    pass
            
            net.add_edge(u, v, label=str(d.get('weight', 1)), color=color, width=width)

        # Physics Options
        net.set_options('{"physics": {"forceAtlas2Based": {"gravitationalConstant": -100, "springLength": 120}, "solver": "forceAtlas2Based"}}')
        
        # Save to Temporary File and Read
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f: 
                return f.read()