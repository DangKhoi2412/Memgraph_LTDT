import streamlit as st
import streamlit.components.v1 as components
import networkx as nx

from ui.styles import load_css
from ui.visualization import Visualizer
from ui.components import Components
from services.graph_service import GraphService
from services.algorithm_service import AlgorithmFactory

# 1. SETUP
st.set_page_config(layout="wide", page_title="Graph Algo OOP", initial_sidebar_state="collapsed")
load_css()

# 2. INIT SERVICES & STATE
if 'graph_service' not in st.session_state:
    st.session_state.graph_service = GraphService()

# Auto load DB
if 'loaded' not in st.session_state:
    db_nodes, db_edges = st.session_state.graph_service.load_from_db()
    st.session_state.nodes = db_nodes if db_nodes else []
    st.session_state.edges = db_edges if db_edges else []
    st.session_state.loaded = True

if 'algo_result' not in st.session_state: st.session_state.algo_result = {}

def sync_data():
    st.session_state.graph_service.sync_to_db(st.session_state.nodes, st.session_state.edges)
    st.session_state.algo_result = {}

# 3. MAIN LAYOUT
st.title("Chương Trình Mô Phỏng Đồ Thị")

# --- SỬA Ở ĐÂY: Tăng tỷ lệ lên [4, 1] để đồ thị chiếm 80% chiều ngang ---
col_viz, col_ctrl = st.columns([4, 1], gap="large")

# --- CỘT PHẢI: MENU ĐIỀU KHIỂN ---
with col_ctrl:
    st.markdown("### 🎮 Bảng Điều Khiển")
    
    algos = ["BFS", "DFS", "Dijkstra", "Bellman-Ford", "Prim (MST)", "Kruskal (MST)"]
    algo_name = st.selectbox("Chọn Thuật toán", algos)
    is_mst = AlgorithmFactory.is_mst(algo_name)

    need_end = not (is_mst or "BFS" in algo_name or "DFS" in algo_name)
    
    if is_mst:
        st.info("⚠️ MST Mode: Tự động chuyển Vô Hướng.")
    
    c1 = st.container()
    start = c1.selectbox("Bắt đầu", st.session_state.nodes) if st.session_state.nodes else None
    
    if st.session_state.nodes and need_end:
        end = c1.selectbox("Kết thúc", st.session_state.nodes) 
    else:
        end = None

    st.write("")
    
    if st.button("🚀 THỰC HIỆN", type="primary", use_container_width=True):
        if not st.session_state.nodes:
            st.error("Đồ thị trống! Vui lòng nhập dữ liệu bên dưới.")
        else:
            try:
                G = st.session_state.graph_service.build_networkx_graph(
                    st.session_state.nodes, st.session_state.edges, for_mst=is_mst
                )
                if is_mst and not nx.is_connected(G): st.warning("Đồ thị không liên thông!")

                algorithm = AlgorithmFactory.get_algorithm(algo_name)
                res = algorithm.execute(G, start, end)
                
                st.session_state.algo_result = res
                st.session_state.algo_result['algo_name'] = algo_name
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.session_state.algo_result = {}

    st.write("")
    b1, b2 = st.columns(2)
    if b1.button("🔄 Reset KQ", type="secondary", use_container_width=True):
        st.session_state.algo_result = {}; st.rerun()
    if b2.button("🗑️ Xóa Đồ thị", type="secondary", use_container_width=True):
        st.session_state.nodes = []; st.session_state.edges = []; 
        sync_data(); st.rerun()

# --- CỘT TRÁI: VISUALIZATION & KẾT QUẢ ---
with col_viz:
    res = st.session_state.algo_result
    viz_mode_mst = res.get('is_mst_mode', False)
    
    if st.session_state.nodes:
        G_viz = st.session_state.graph_service.build_networkx_graph(
            st.session_state.nodes, st.session_state.edges, for_mst=viz_mode_mst
        )
        html = Visualizer.render(G_viz, res, is_mst=viz_mode_mst)
        
        # --- SỬA Ở ĐÂY: Tăng chiều cao khung hiển thị lên 800px ---
        components.html(html, height=800) 
    else:
        st.info("Chưa có dữ liệu. Vui lòng thêm Đỉnh và Cạnh ở bên dưới.")

    Components.result_card(res, res.get('algo_name', ''))

st.markdown("---")
st.subheader("📝 Nhập Liệu Đồ Thị")
Components.input_section(st.session_state, sync_data)