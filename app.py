import streamlit as st
import streamlit.components.v1 as components
import networkx as nx

from ui.styles import load_css
from ui.visualization import Visualizer
from ui.components import Components
from services.graph_service import GraphService
from services.algorithm_service import AlgorithmFactory

# 1. SETUP
st.set_page_config(layout="wide", page_title="Lý thuyết đồ thị: Memgraph", initial_sidebar_state="collapsed")
load_css()

# 2. INIT SERVICES
if 'graph_service' not in st.session_state:
    st.session_state.graph_service = GraphService()
    
if "dirty" not in st.session_state:
    st.session_state.dirty = False

# --- QUY TRÌNH TẢI DỮ LIỆU AN TOÀN ---
if 'data_loaded' not in st.session_state:
    try:
        db_nodes, db_edges = st.session_state.graph_service.load_from_db()
        st.session_state.nodes = db_nodes if db_nodes else []
        st.session_state.edges = db_edges if db_edges else []
        st.session_state.dirty = False
        
        if st.session_state.edges:
            st.toast(f"✅ Đã tải: {len(st.session_state.edges)} cạnh từ DB.", icon="🔗")
            
    except Exception as e:
        st.error(f"Lỗi khởi động: {e}")
        st.session_state.nodes = []; st.session_state.edges = []
    
    st.session_state.data_loaded = True

# Init Result
if 'algo_result' not in st.session_state: st.session_state.algo_result = {}

# Hàm đồng bộ
def sync_data():
    if not st.session_state.dirty:
        return

    # 🔥 FIX: Bỏ đoạn kiểm tra if not st.session_state.edges
    # Cho phép sync kể cả khi list rỗng để đảm bảo DB đúng với UI
    
    st.session_state.graph_service.sync_to_db(
        st.session_state.nodes,
        st.session_state.edges
    )
    
    st.session_state.dirty = False

# 3. UI LAYOUT
st.title("Chương Trình Mô Phỏng Đồ Thị")

col_viz, col_ctrl = st.columns([4, 1], gap="large")

# CỘT PHẢI
with col_ctrl:
    st.markdown("### 🎮 Bảng Điều Khiển")
    algos = ["BFS", "DFS", "Dijkstra", "Bellman-Ford", "Prim (MST)", "Kruskal (MST)"]
    algo_name = st.selectbox("Chọn Thuật toán", algos)
    
    is_mst = AlgorithmFactory.is_mst(algo_name)
    need_end = not (is_mst or "BFS" in algo_name or "DFS" in algo_name)
    
    if is_mst: st.info("⚠️ MST Mode: Xử lý Vô Hướng.")
    
    c1 = st.container()
    start = c1.selectbox("Bắt đầu", st.session_state.nodes) if st.session_state.nodes else None
    end = c1.selectbox("Kết thúc", st.session_state.nodes) if st.session_state.nodes and need_end else None

    st.write("")
    if st.button("🚀 THỰC HIỆN", type="primary", use_container_width=True):
        if not st.session_state.nodes:
            st.error("Đồ thị trống!")
        else:
            try:
                G = st.session_state.graph_service.build_networkx_graph(st.session_state.nodes, st.session_state.edges, for_mst=is_mst)
                if is_mst and not nx.is_connected(G): st.warning("Đồ thị không liên thông!")
                algorithm = AlgorithmFactory.get_algorithm(algo_name)
                res = algorithm.execute(G, start, end)
                st.session_state.algo_result = res
                st.session_state.algo_result['algo_name'] = algo_name
            except Exception as e:
                st.error(f"Lỗi: {e}")

    st.write("")
    b1, b2 = st.columns(2)
    if b1.button("🔄 Reset KQ", use_container_width=True):
        st.session_state.algo_result = {}; st.rerun()
        
    if b2.button("🗑️ Xóa UI"):
        st.session_state.nodes = []
        st.session_state.edges = []
        st.session_state.dirty = True
        sync_data() # Gọi sync ngay
        st.rerun()
        
    if st.button("🔥 Xóa DB thật"):
        st.session_state.graph_service.clear_db()
        st.session_state.nodes = []
        st.session_state.edges = []
        st.session_state.dirty = False
        st.rerun()

# CỘT TRÁI
with col_viz:
    res = st.session_state.algo_result
    viz_mode_mst = res.get('is_mst_mode', False)
    
    if st.session_state.nodes:
        G_viz = st.session_state.graph_service.build_networkx_graph(st.session_state.nodes, st.session_state.edges, for_mst=viz_mode_mst)
        html = Visualizer.render(G_viz, res, is_mst=viz_mode_mst)
        components.html(html, height=550)
    else:
        st.info("Chưa có dữ liệu.")
    Components.result_card(res, res.get('algo_name', ''))

st.markdown("---")
Components.input_section(st.session_state, sync_data)