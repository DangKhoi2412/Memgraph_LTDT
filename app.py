import streamlit as st
import streamlit.components.v1 as components

from ui.styles import load_css
from ui.visualization import Visualizer
from ui.components import Components
from services.graph_service import GraphService
from services.algorithm_service import AlgorithmFactory

st.set_page_config(
    layout="wide", 
    page_title="Lý thuyết đồ thị: Memgraph", 
    initial_sidebar_state="collapsed"
)
load_css()

if 'graph_service' not in st.session_state:
    st.session_state.graph_service = GraphService()
    
if "dirty" not in st.session_state:
    st.session_state.dirty = False

if 'algo_result' not in st.session_state: 
    st.session_state.algo_result = {}

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if not st.session_state.data_loaded:
    try:
        db_nodes, db_edges, db_config = st.session_state.graph_service.load_from_db()
        st.session_state.nodes = db_nodes if db_nodes else []
        st.session_state.edges = db_edges if db_edges else []
        
        # Initialize Config from DB
        if 'cfg_graph_type' not in st.session_state:
            st.session_state.cfg_graph_type = "Có hướng" if db_config.get('is_directed', True) else "Vô hướng"
        
        if 'cfg_is_weighted' not in st.session_state:
            st.session_state.cfg_is_weighted = db_config.get('is_weighted', True)
            
        st.session_state.dirty = False
        st.session_state.data_loaded = True
        
        if st.session_state.edges:
            st.toast(f"✅ Đã tải: {len(st.session_state.edges)} cạnh từ DB.", icon="🔗")
            
            
    except Exception as e:
        st.error(f"LỖI VẬN HÀNH: Không thể tải dữ liệu từ Memgraph/Database.")
        st.error(f"Chi tiết: {e}")
        st.warning("Ứng dụng đã dừng để ngăn chặn mất dữ liệu. Vui lòng kiểm tra Docker/Memgraph và thử lại.")
        if st.button("Thử Lại Kết Nối"): st.rerun()
        st.stop() 

def sync_data_callback():
    if not st.session_state.dirty: return
    
    is_directed_db = st.session_state.get("cfg_graph_type", "Có hướng") == "Có hướng"
    is_weighted_db = st.session_state.get("cfg_is_weighted", True)
    
    success, msg = st.session_state.graph_service.sync_to_db(
        st.session_state.nodes,
        st.session_state.edges,
        is_directed=is_directed_db,
        is_weighted=is_weighted_db
    )
    
    if success:
        st.toast(msg, icon="✅")
        st.session_state.dirty = False
    else:
        st.error(f"Lỗi Lưu Data: {msg}")

def save_config_callback():
    # Save config immediately when changed
    is_directed = st.session_state.cfg_graph_type == "Có hướng"
    is_weighted = st.session_state.cfg_is_weighted
    st.session_state.graph_service.repository.save_config(is_directed, is_weighted)
    st.toast("Đã lưu cấu hình!", icon="💾")

st.title("Chương Trình Mô Phỏng Đồ Thị Dựa trên Memgraph database")

col_viz, col_ctrl = st.columns([4, 1], gap="large")
with col_ctrl:
    st.markdown("### Bảng Điều Khiển")

    st.markdown("##### Cấu Hình Đồ Thị")
    c_type, c_weight = st.columns(2)
    # Using keys to persist state across reruns
    graph_type = c_type.radio("Loại", ["Có hướng", "Vô hướng"], horizontal=True, label_visibility="collapsed", key="cfg_graph_type", on_change=save_config_callback)
    is_weighted = c_weight.checkbox("Trọng số", value=True, key="cfg_is_weighted", on_change=save_config_callback)
    
    is_directed = graph_type == "Có hướng"
    
    st.markdown("---")
    
    algos = ["BFS", "DFS", "Dijkstra", "Bellman-Ford"]
    algo_name = st.selectbox("Chọn Thuật toán", algos)
    
    need_end = algo_name not in ["BFS", "DFS"]
    
    c1 = st.container()
    start = c1.selectbox("Bắt đầu", st.session_state.nodes) if st.session_state.nodes else None
    
    end = None
    if st.session_state.nodes and need_end:
        end = c1.selectbox("Kết thúc", st.session_state.nodes)

    st.write("")
    
    if st.button("THỰC HIỆN", type="primary", use_container_width=True):
        if not st.session_state.nodes:
            st.error("Đồ thị trống!")
        else:
            try:
                G = st.session_state.graph_service.build_networkx_graph(
                    st.session_state.nodes, 
                    st.session_state.edges,
                    is_directed=is_directed,
                    is_weighted=is_weighted
                )
                algorithm = AlgorithmFactory.get_algorithm(algo_name)
                res = algorithm.execute(G, start, end)
                
                st.session_state.algo_result = res
                st.session_state.algo_result['algo_name'] = algo_name
                st.session_state.algo_result['is_directed'] = is_directed
                st.session_state.algo_result['is_weighted'] = is_weighted
            except Exception as e:
                st.error(f"Lỗi: {e}")

    st.write("")
    
    b1, b2 = st.columns(2)
    if b1.button("RESET KẾT QUẢ", use_container_width=True):
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

with col_viz:
    res = st.session_state.algo_result
    
    if st.session_state.nodes:
        G_viz = st.session_state.graph_service.build_networkx_graph(
            st.session_state.nodes, 
            st.session_state.edges,
            is_directed=res.get('is_directed', is_directed), 
            is_weighted=res.get('is_weighted', is_weighted)
        )
        # Use result settings if available (snapshot), else current UI settings
        viz_directed = res.get('is_directed', is_directed)
        viz_weighted = res.get('is_weighted', is_weighted)
        
        html = Visualizer.render(G_viz, res, is_directed=viz_directed, is_weighted=viz_weighted) 
        components.html(html, height=550)
    else:
        st.info("Chưa có dữ liệu. Hãy thêm đỉnh và cạnh.")
        
    Components.result_card(res, res.get('algo_name', ''))

st.markdown("---")
Components.input_section(st.session_state, sync_data_callback, is_directed=is_directed, is_weighted=is_weighted)