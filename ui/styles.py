import streamlit as st

def load_css():
    st.markdown("""
    <style>
        html, body, [class*="css"] { font-family: 'Segoe UI', Roboto, sans-serif; color: #333; }
        .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

        /* BUTTONS */
        div.stButton > button[kind="primary"] {
            background-color: #2E7D32 !important; /* Xanh lá đậm */
            border: none !important;
            color: white !important;
            font-size: 16px !important; font-weight: 700 !important;
            height: 50px !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        div.stButton > button[kind="secondary"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CFD8DC !important;
            color: #546E7A !important;
            height: 45px !important;
        }

        /* --- RESULT CARD (Horizontal Layout) --- */
        .result-card {
            background-color: #F1F8E9; /* Nền xanh nhạt */
            border: 1px solid #AED581; /* Viền xanh */
            border-radius: 8px;
            padding: 15px 20px;
            margin-top: 10px;
            display: flex; /* Xếp ngang */
            align-items: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }

        /* Cột số liệu (Bên trái) */
        .res-left {
            flex: 0 0 200px; /* Cố định chiều rộng */
            border-right: 2px solid #C5E1A5;
            padding-right: 20px; margin-right: 20px;
            text-align: center;
        }
        .res-label { font-size: 0.85rem; color: #558B2F; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
        .res-number { font-size: 3rem; font-weight: 800; color: #2E7D32; line-height: 1; margin-bottom: 5px; }
        .res-algo { font-size: 0.8rem; color: #777; }

        /* Cột chi tiết (Bên phải) */
        .res-right { flex: 1; }
        .res-path-title { font-size: 0.95rem; color: #333; margin-bottom: 8px; font-weight: 600; }
        .res-code-box {
            background-color: #FFFFFF;
            border: 1px solid #DCEDC8;
            border-radius: 6px;
            padding: 10px 15px;
            font-family: 'Consolas', monospace;
            font-size: 1rem; color: #1B5E20; font-weight: 600;
        }

        /* Input & Grid */
        .input-title { font-size: 1.1rem; font-weight: 700; color: #2E7D32; border-bottom: 2px solid #E8F5E9; margin-bottom: 10px; padding-bottom: 5px; }
        .grid-header { font-size: 0.9rem; font-weight: 700; color: #555; text-transform: uppercase; }
        hr { margin: 0.5rem 0 !important; border-color: #EEE; }
    </style>
    """, unsafe_allow_html=True)