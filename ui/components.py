import streamlit as st

class Components:
    @staticmethod
    def result_card(res, algo_name):
        if not res: return
        
        # Xác định nội dung hiển thị
        val_lbl = "SỐ ĐỈNH DUYỆT"
        val_num = 0
        path_lbl = "Chi tiết lộ trình / cạnh:"
        path_txt = ""

        if res.get('type') == 'mst':
            val_lbl = "TỔNG TRỌNG SỐ"
            val_num = res['cost']
            path_txt = ",  ".join([f"({u}-{v})" for u, v in res['mst_edges']])
        
        elif res.get('type') == 'path':
            val_lbl = "TỔNG CHI PHÍ"
            val_num = res['cost']
            path_txt = " ➝ ".join(res['path_nodes'])
            
        else: # BFS/DFS
            val_num = len(res.get('path_nodes', []))
            path_txt = " ➝ ".join(res.get('path_nodes', []))

        # Render HTML
        st.markdown(f"""
        <div class="result-card">
            <div class="res-left">
                <div class="res-label">{val_lbl}</div>
                <div class="res-number">{val_num}</div>
                <div class="res-algo">Thuật toán: {algo_name}</div>
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

        # --- NODES ---
        with col_L:
            st.markdown('<div class="input-title">📍 QUẢN LÝ ĐỈNH</div>', unsafe_allow_html=True)
            with st.form("f_n", clear_on_submit=True):
                c1, c2 = st.columns([2.5, 1], vertical_alignment="bottom")
                nn = c1.text_input("Tên", placeholder="Tên...")
                def add_n():
                    if nn and nn not in session_state.nodes:
                        session_state.nodes.append(nn)
                        on_change_callback()
                c2.form_submit_button("Thêm", type="primary", on_click=add_n, use_container_width=True)

            st.write("")
            h1, h2 = st.columns([3, 1], vertical_alignment="center")
            h1.markdown('<div class="grid-header">TÊN ĐỈNH</div>', unsafe_allow_html=True)
            h2.markdown('<div class="grid-header" style="text-align:center">XÓA</div>', unsafe_allow_html=True)
            
            with st.container(height=300):
                if not session_state.nodes: st.caption("Trống")
                for i, n in enumerate(session_state.nodes):
                    r1, r2 = st.columns([3, 1], vertical_alignment="center")
                    r1.write(f"**{n}**")
                    def del_n(idx=i, name=n):
                        session_state.nodes.pop(idx)
                        session_state.edges = [e for e in session_state.edges if e['src']!=name and e['target']!=name]
                        on_change_callback()
                    r2.button("✕", key=f"dn_{i}", type="secondary", use_container_width=True, on_click=del_n)
                    st.markdown("<hr>", unsafe_allow_html=True)

        # --- EDGES ---
        with col_R:
            st.markdown('<div class="input-title">🔗 QUẢN LÝ CẠNH</div>', unsafe_allow_html=True)
            with st.form("f_e", clear_on_submit=False):
                c1, c2, c3, c4 = st.columns([2, 1.5, 2, 1.2], vertical_alignment="bottom")
                s = c1.selectbox("Từ", session_state.nodes, key="s")
                w = c2.number_input("W", value=1, step=1)
                d = c3.selectbox("Đến", session_state.nodes, key="d")
                def add_e():
                    if s and d:
                        session_state.edges.append({"src":s, "target":d, "w":int(w)})
                        on_change_callback()
                c4.form_submit_button("Thêm", type="primary", on_click=add_e, use_container_width=True)

            st.write("")
            h_ratio = [3, 1.5, 1]
            h1, h2, h3 = st.columns(h_ratio, vertical_alignment="center")
            h1.markdown('<div class="grid-header">CHI TIẾT</div>', unsafe_allow_html=True)
            h2.markdown('<div class="grid-header">TRỌNG SỐ</div>', unsafe_allow_html=True)
            h3.markdown('<div class="grid-header" style="text-align:center">XÓA</div>', unsafe_allow_html=True)

            with st.container(height=300):
                if not session_state.edges: st.caption("Trống")
                for i, e in enumerate(session_state.edges):
                    r1, r2, r3 = st.columns(h_ratio, vertical_alignment="center")
                    r1.write(f"{e['src']} ➝ {e['target']}")
                    r2.write(f"{int(e['w'])}")
                    def del_e(idx=i):
                        session_state.edges.pop(idx)
                        on_change_callback()
                    r3.button("✕", key=f"de_{i}", type="secondary", use_container_width=True, on_click=del_e)
                    st.markdown("<hr>", unsafe_allow_html=True)