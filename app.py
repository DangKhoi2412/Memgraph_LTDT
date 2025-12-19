import streamlit as st
import streamlit.components.v1 as components

# Local Imports
from ui.styles import load_css
from ui.visualization import Visualizer
from ui.components import Components
from services.graph_service import GraphService
from services.algorithm_service import AlgorithmFactory

# --- 1. CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="Lý thuyết đồ thị: Memgraph", 
    initial_sidebar_state="collapsed"
)
load_css()

# --- 2. STATE INITIALIZATION ---
if 'graph_service' not in st.session_state:
    st.session_state.graph_service = GraphService()
    
if "dirty" not in st.session_state:
    st.session_state.dirty = False

if 'algo_result' not in st.session_state: 
    st.session_state.algo_result = {}

# --- 3. DATA LOADING (SAFEGUARDED) ---
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if not st.session_state.data_loaded:
    try:
        db_nodes, db_edges = st.session_state.graph_service.load_from_db()
        st.session_state.nodes = db_nodes if db_nodes else []
        st.session_state.edges = db_edges if db_edges else []
        st.session_state.dirty = False
        st.session_state.data_loaded = True
        
        if st.session_state.edges:
            st.toast(f"✅ Đã tải: {len(st.session_state.edges)} cạnh từ DB.", icon="🔗")
            
    except Exception as e:
        st.error(f"❌ LỖI VẬN HÀNH: Không thể tải dữ liệu từ Memgraph/Database.")
        st.error(f"Chi tiết: {e}")
        st.warning("⚠️ Ứng dụng đã dừng để ngăn chặn mất dữ liệu. Vui lòng kiểm tra Docker/Memgraph và thử lại.")
        if st.button("🔄 Thử Lại Kết Nối"): st.rerun()
        st.stop() 

# --- 4. CORE LOGIC ---
def sync_data_callback():
    """Callback triggers sync to DB when data changes."""
    if not st.session_state.dirty: return
    
    success, msg = st.session_state.graph_service.sync_to_db(
        st.session_state.nodes,
        st.session_state.edges
    )
    
    if success:
        st.toast(msg, icon="✅")
        st.session_state.dirty = False
    else:
        st.error(f"Lỗi Lưu Data: {msg}")

# --- 5. UI LAYOUT ---
st.title("Chương Trình Mô Phỏng Đồ Thị (Có Hướng)")

col_viz, col_ctrl = st.columns([4, 1], gap="large")

# === PANEL: CONTROL ===
with col_ctrl:
    st.markdown("### Bảng Điều Khiển")
    
    # Algorithm Selection
    algos = ["BFS", "DFS", "Dijkstra", "Bellman-Ford"]
    algo_name = st.selectbox("Chọn Thuật toán", algos)
    
    # Dynamic Inputs based on Algo
    need_end = algo_name not in ["BFS", "DFS"]
    
    c1 = st.container()
    start = c1.selectbox("Bắt đầu", st.session_state.nodes) if st.session_state.nodes else None
    
    end = None
    if st.session_state.nodes and need_end:
        end = c1.selectbox("Kết thúc", st.session_state.nodes)

    st.write("")
    
    # EXECUTE BUTTON
    if st.button("THỰC HIỆN", type="primary", use_container_width=True):
        if not st.session_state.nodes:
            st.error("Đồ thị trống!")
        else:
            try:
                G = st.session_state.graph_service.build_networkx_graph(
                    st.session_state.nodes, 
                    st.session_state.edges
                )
                algorithm = AlgorithmFactory.get_algorithm(algo_name)
                res = algorithm.execute(G, start, end)
                
                st.session_state.algo_result = res
                st.session_state.algo_result['algo_name'] = algo_name
            except Exception as e:
                st.error(f"Lỗi: {e}")

    st.write("")
    
    # ACTIONS
    b1, b2 = st.columns(2)
    if b1.button("Reset KẾT QUẢ", use_container_width=True):
        st.session_state.algo_result = {}
        st.rerun()
        
    if b2.button("XÓA ĐỒ THỊ"):
        st.session_state.nodes = []
        st.session_state.edges = []
        st.session_state.dirty = True
        sync_data_callback() 
        st.session_state.algo_result = {}
        st.rerun()
        
    if st.button("RESET DATABASE"):
        st.session_state.graph_service.clear_db()
        st.session_state.nodes = []
        st.session_state.edges = []
        st.session_state.dirty = False
        st.rerun()

# === PANEL: VISUALIZATION ===
with col_viz:
    res = st.session_state.algo_result
    
    if st.session_state.nodes:
        G_viz = st.session_state.graph_service.build_networkx_graph(
            st.session_state.nodes, 
            st.session_state.edges
        )
        # Verify Visualizer signature for is_mst support if needed, assuming default False
        html = Visualizer.render(G_viz, res) 
        components.html(html, height=550)
    else:
        st.info("Chưa có dữ liệu. Hãy thêm đỉnh và cạnh.")
        
    Components.result_card(res, res.get('algo_name', ''))

st.markdown("---")
# Input Section handling dynamic updates
Components.input_section(st.session_state, sync_data_callback)