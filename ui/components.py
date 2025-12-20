
import streamlit as st

class Components:
    @staticmethod
    def result_card(res, algo_name):
        if not res: return
        
        val_lbl = "ĐỈNH ĐÃ DUYỆT"
        val_num = 0
        path_lbl = "📌 CHI TIẾT LỘ TRÌNH:"
        path_txt = ""

        if res.get('type') == 'path':
            val_lbl = "TỔNG CHI PHÍ"
            val_num = res.get('cost', 0)
            path_txt = " ➝ ".join(res.get('path_nodes', []))
            
        else:
            val_num = len(res.get('path_nodes', []))
            path_txt = " ➝ ".join(res.get('path_nodes', []))

        st.markdown(f"""
        <div class="result-card">
            <div class="res-left">
                <div class="res-label">{val_lbl}</div>
                <div class="res-number">{val_num}</div>
                <div class="res-algo">{algo_name}</div>
            </div>
            <div class="res-right">
                <div class="res-path-title">{path_lbl}</div>
                <div class="res-code-box">{path_txt}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def input_section(session_state, on_change_callback):
        col_L, col_R = st.columns([1, 1.8], gap="large")

        with col_L:
            st.markdown('<div class="input-title">📍 QUẢN LÝ ĐỈNH</div>', unsafe_allow_html=True)
            with st.form("f_node", clear_on_submit=True):
                c1, c2 = st.columns([2.5, 1], vertical_alignment="bottom")
                c1.text_input("Tên", placeholder="Tên...", key="input_node_name")
                
                def add_n():
                    new_name = st.session_state.input_node_name
                    if new_name:
                        clean_name = str(new_name).strip()
                        if clean_name not in session_state.nodes:
                            session_state.nodes.append(clean_name)
                            session_state.dirty = True 
                            on_change_callback()
                
                c2.form_submit_button("Thêm", type="primary", on_click=add_n, use_container_width=True)

            st.write("")
            h1, h2 = st.columns([3, 1], vertical_alignment="center")
            h1.markdown('<div class="grid-header">TÊN ĐỈNH</div>', unsafe_allow_html=True)
            h2.markdown('<div class="grid-header" style="text-align:center">XÓA</div>', unsafe_allow_html=True)
            
            with st.container(height=300):
                if not session_state.nodes: st.caption("Chưa có dữ liệu")
                for i, n in enumerate(session_state.nodes):
                    r1, r2 = st.columns([3, 1], vertical_alignment="center")
                    r1.write(f"**{n}**")
                    
                    def del_n(idx=i, name=n):
                        session_state.nodes.pop(idx)
                        session_state.edges = [
                            e for e in session_state.edges 
                            if e.get('source') != name and e.get('target') != name
                        ]
                        session_state.dirty = True 
                        on_change_callback()
                        
                    r2.button("✕", key=f"dn_{i}", type="secondary", use_container_width=True, on_click=del_n)
                    st.markdown("<hr>", unsafe_allow_html=True)
    
        with col_R:
            st.markdown('<div class="input-title">🔗 QUẢN LÝ CẠNH (CÓ HƯỚNG)</div>', unsafe_allow_html=True)
            with st.form("f_edge", clear_on_submit=False):
                c1, c2, c3, c4 = st.columns([2, 1.5, 2, 1.2], vertical_alignment="bottom")
                
                c1.selectbox("Từ", session_state.nodes, key="input_edge_src")
                c2.number_input("W", value=1, step=1, key="input_edge_w")
                c3.selectbox("Đến", session_state.nodes, key="input_edge_target")
                
                def add_e():
                    s = st.session_state.get("input_edge_src")
                    d = st.session_state.get("input_edge_target")
                    w = st.session_state.get("input_edge_w", 1)
                    
                    if s and d:
                        new_edge = {
                            "source": str(s).strip(),
                            "target": str(d).strip(),
                            "weight": int(w)
                        }
                        if new_edge not in session_state.edges:
                            session_state.edges.append(new_edge)
                            session_state.dirty = True 
                            on_change_callback()
                        
                c4.form_submit_button("Thêm", type="primary", on_click=add_e, use_container_width=True)

            st.write("")
            h_ratio = [3, 1.5, 1]
            h1, h2, h3 = st.columns(h_ratio, vertical_alignment="center")
            h1.markdown('<div class="grid-header">CHI TIẾT</div>', unsafe_allow_html=True)
            h2.markdown('<div class="grid-header">TRỌNG SỐ</div>', unsafe_allow_html=True)
            h3.markdown('<div class="grid-header" style="text-align:center">XÓA</div>', unsafe_allow_html=True)

            with st.container(height=300):
                if not session_state.edges: st.caption("Chưa có dữ liệu")
                for i, e in enumerate(session_state.edges):
                    r1, r2, r3 = st.columns(h_ratio, vertical_alignment="center")
                    
                    src = e.get('source', e.get('src', '?'))
                    dst = e.get('target', e.get('target', '?')) 
                    w   = e.get('weight', e.get('w', 0))

                    r1.write(f"{src} ➝ {dst}")
                    r2.write(f"{int(w)}")
                    
                    def del_e(idx=i):
                        session_state.edges.pop(idx)
                        session_state.dirty = True 
                        on_change_callback()
                        
                    r3.button("✕", key=f"de_{i}", type="secondary", use_container_width=True, on_click=del_e)
                    st.markdown("<hr>", unsafe_allow_html=True)