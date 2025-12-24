import json
import os
import streamlit as st
import streamlit.components.v1 as components

from ui.styles import load_css
from ui.visualization import Visualizer
from ui.components import Components
from services.graph_service import GraphService
from services.algorithm_service import AlgorithmFactory

# 1. SETUP
st.set_page_config(
    layout="wide", 
    page_title="Lý thuyết đồ thị: Memgraph", 
    initial_sidebar_state="expanded"
)
load_css()

# 2. STATE INITIALIZATION
if 'graph_service' not in st.session_state:
    st.session_state.graph_service = GraphService()

if "dirty" not in st.session_state:
    st.session_state.dirty = False

if 'algo_result' not in st.session_state: 
    st.session_state.algo_result = {}

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'cfg_graph_type' not in st.session_state:
    st.session_state.cfg_graph_type = "Có hướng"

if 'cfg_is_weighted' not in st.session_state:
    st.session_state.cfg_is_weighted = True

# 3. CALLBACKS & HELPERS (Must be defined before UI usage)

def sync_data_callback():
    """Syncs current memory state to DB based on UI flags."""
    if not st.session_state.dirty: return
    
    is_directed_db = st.session_state.get("cfg_graph_type", "Có hướng") == "Có hướng"
    is_weighted_db = st.session_state.get("cfg_is_weighted", True)
    
    # Use force=False for regular updates
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
    """Saves just the configuration changes."""
    is_directed = st.session_state.cfg_graph_type == "Có hướng"
    is_weighted = st.session_state.cfg_is_weighted
    st.session_state.graph_service.repository.save_config(is_directed, is_weighted)
    st.toast("Đã lưu cấu hình!", icon="💾")

def load_graph_from_data(data):
    """Core logic to load graph from JSON and persist it."""
    try:
        valid_nodes, valid_edges, valid_config = st.session_state.graph_service.from_json(data)
        
        # 1. Update Data
        st.session_state.nodes = valid_nodes
        st.session_state.edges = valid_edges
        
        # 2. Derive Config
        new_type = "Có hướng" if valid_config.get('is_directed', True) else "Vô hướng"
        new_weighted = valid_config.get('is_weighted', True)
        
        # 3. Update Session State (Will be reflected in widgets on next run)
        st.session_state.cfg_graph_type = new_type
        st.session_state.cfg_is_weighted = new_weighted
        
        # 4. Sync to DB IMMEDIATELY with FORCE=True (Overwrite DB)
        success, msg = st.session_state.graph_service.sync_to_db(
            valid_nodes,
            valid_edges,
            is_directed=(new_type == "Có hướng"),
            is_weighted=new_weighted,
            force=True 
        )
        
        if success:
            st.session_state.dirty = False
            st.toast("Đã tải và lưu dữ liệu thành công!", icon="✅")
        else:
            st.error(f"Tải thành công nhưng LỖI LƯU DB: {msg}")
            
    except Exception as e:
        st.error(f"Lỗi xử lý dữ liệu: {e}")

def on_import_click():
    """Callback for File Import Button"""
    if st.session_state.get("u_file") is not None:
        try:
            data = json.load(st.session_state.u_file)
            load_graph_from_data(data)
        except Exception as e:
            st.error(f"Lỗi đọc file JSON: {e}")

def on_sample_click():
    """Callback for Sample Load Button"""
    selected = st.session_state.get("sel_sample")
    sample_map = {
        "Mẫu 1: Đồ thị có hướng có trọng số": "sample_directed.json",
        "Mẫu 2: Đồ thị vô hướng có trọng số": "sample_undirected.json"
    }
    
    if selected in sample_map:
        fname = sample_map[selected]
        fpath = os.path.join("samples", fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            load_graph_from_data(data)
        except Exception as e:
            st.error(f"Không thể đọc mẫu {fname}: {e}")

# 4. DATA LOADING (Startup)
if not st.session_state.data_loaded:
    try:
        db_nodes, db_edges, db_config = st.session_state.graph_service.load_from_db()
        st.session_state.nodes = db_nodes if db_nodes else []
        st.session_state.edges = db_edges if db_edges else []
        
        # Apply DB Config to Session State if config exists
        # This overrides defaults, ensuring persistence works
        if db_config:
            st.session_state.cfg_graph_type = "Có hướng" if db_config.get('is_directed', True) else "Vô hướng"
            st.session_state.cfg_is_weighted = db_config.get('is_weighted', True)
            
        st.session_state.dirty = False
        st.session_state.data_loaded = True
        
        if st.session_state.edges:
            st.toast(f"✅ Đã tải {len(st.session_state.edges)} cạnh.", icon="🔗")
            
    except Exception as e:
        st.error(f"LỖI VẬN HÀNH: Không thể kết nối Memgraph.")
        st.warning(f"Chi tiết: {e}")
        if st.button("Thử Lại Kết Nối"): st.rerun()
        st.stop() 

# 5. UI LAYOUT
st.title("Chương Trình Mô Phỏng Đồ Thị Dựa Trên Memgraph")

# --- SIDEBAR CONTROL PANEL ---
# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("## 🎛️ Bảng Điều Khiển")

    # 1. CONFIGURATION
    with st.expander("⚙️ Cấu Hình Đồ Thị", expanded=True):
        c_type, c_weight = st.columns(2)
        # Widgets map to session_state keys automatically
        graph_type = c_type.radio(
            "Loại", 
            ["Có hướng", "Vô hướng"], 
            horizontal=True, 
            label_visibility="collapsed", 
            key="cfg_graph_type", 
            on_change=save_config_callback
        )
        is_weighted = c_weight.checkbox(
            "Trọng số", 
            value=True, 
            key="cfg_is_weighted", 
            on_change=save_config_callback
        )
        is_directed = (graph_type == "Có hướng")

    st.write("")

    # 2. ALGORITHMS
    with st.expander("🧮 Chọn Thuật Toán", expanded=True):
        algos = ["BFS", "DFS", "Dijkstra", "Bellman-Ford"]
        algo_name = st.selectbox("Thuật toán", algos, label_visibility="collapsed")
        
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
    
    # 3. ACTIONS
    with st.expander("🛠️ Tác Vụ", expanded=True):
        b1, b2 = st.columns(2)
        if b1.button("RESET KQ", use_container_width=True):
            st.session_state.algo_result = {}
            st.rerun()
            
        if b2.button("XÓA ĐỒ THỊ", use_container_width=True):
            st.session_state.nodes = []
            st.session_state.edges = []
            st.session_state.dirty = True
            sync_data_callback() 
            st.session_state.algo_result = {}
            st.rerun()
            
        if st.button("RESET DATABASE", use_container_width=True):
            st.session_state.graph_service.clear_db()
            st.session_state.nodes = []
            st.session_state.edges = []
            st.session_state.dirty = False
            st.rerun()

    st.write("")
    
    # 4. DATA MANAGEMENT
    with st.expander("📂 Quản Lý Dữ Liệu", expanded=False):
        # EXPORT
        st.markdown("**1. Xuất Dữ Liệu**")
        if st.session_state.nodes:
            export_config = {
                "is_directed": is_directed,
                "is_weighted": is_weighted
            }
            json_data = st.session_state.graph_service.to_json(
                st.session_state.nodes, 
                st.session_state.edges, 
                export_config
            )
            st.download_button(
                label="💾 Tải xuống JSON",
                data=json.dumps(json_data, indent=2, ensure_ascii=False),
                file_name="graph_data.json",
                mime="application/json"
            )
        else:
            st.caption("Đồ thị trống.")

        st.markdown("---")
        
        # IMPORT
        st.markdown("**2. Nhập Dữ Liệu**")
        st.file_uploader("Chọn file JSON", type=["json"], key="u_file")
        st.button("Lên tải & Áp dụng", on_click=on_import_click)

        st.markdown("---")
        
        # SAMPLES
        st.markdown("**3. Dữ Liệu Mẫu**")
        sample_keys = [
            "Mẫu 1: Đồ thị có hướng có trọng số",
            "Mẫu 2: Đồ thị vô hướng có trọng số"
        ]
        st.selectbox("Chọn mẫu", sample_keys, key="sel_sample")
        st.button("Tải Mẫu", on_click=on_sample_click, type="secondary")

# --- MAIN VISUALIZATION ---
res = st.session_state.algo_result
    
if st.session_state.nodes:
    # Use visualization settings from Result (if available) or Current State
    viz_directed = res.get('is_directed', is_directed)
    viz_weighted = res.get('is_weighted', is_weighted)
    
    G_viz = st.session_state.graph_service.build_networkx_graph(
        st.session_state.nodes, 
        st.session_state.edges,
        is_directed=viz_directed, 
        is_weighted=viz_weighted
    )
    
    html = Visualizer.render(G_viz, res, is_directed=viz_directed, is_weighted=viz_weighted) 
    components.html(html, height=550)
else:
    st.info("Chưa có dữ liệu. Hãy thêm đỉnh và cạnh hoặc tải dữ liệu mẫu từ Sidebar.")
    
Components.result_card(res, res.get('algo_name', ''))

st.markdown("---")
Components.input_section(st.session_state, sync_data_callback, is_directed=is_directed, is_weighted=is_weighted)