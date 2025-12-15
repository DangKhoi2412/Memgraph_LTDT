import streamlit as st

def load_css():
    st.markdown("""
    <style>
        /* CSS TỐI ƯU GIAO DIỆN (Code Mẫu) */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 16px; 
            color: #333;
        }
        
        /* --- Padding chuẩn --- */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }

        /* Button Styles */
        div.stButton > button {
            min-height: 48px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }
        div.stButton > button[kind="primary"] {
            background-color: #2E7D32 !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        div.stButton > button[kind="secondary"] {
            background-color: white !important;
            border: 1px solid #CFD8DC !important;
            color: #546E7A !important;
        }
        
        /* Result Card - Style Cũ */
        .result-card {
            background-color: #F1F8E9;
            border: 1px solid #C5E1A5;
            border-radius: 8px;
            padding: 10px 15px;
            margin-top: 8px;
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .res-left {
            flex: 1; border-right: 2px solid #AED581;
            padding-right: 15px; margin-right: 15px; text-align: center; min-width: 120px;
        }
        .res-label { font-size: 0.8rem; color: #558B2F; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
        .res-number { font-size: 1.8rem; font-weight: 800; color: #2E7D32; line-height: 1; }
        .res-right { flex: 2; }
        .res-code-box {
            font-family: 'Consolas', monospace;
            background: #fff; padding: 6px 10px;
            border-radius: 4px; border: 1px solid #DCEDC8;
            font-size: 0.9rem; color: #33691E; font-weight: 600;
        }

        /* Input & Grid */
        .grid-header { font-size: 0.9rem; font-weight: 700; color: #455A64; text-transform: uppercase; margin-bottom: 5px; }
        .input-title { font-size: 1.1rem; font-weight: 700; color: #2E7D32; margin-bottom: 10px; border-bottom: 2px solid #E8F5E9; padding-bottom: 5px; }
        hr { margin: 0.5rem 0 !important; border-color: #EEEEEE; }
    </style>
    """, unsafe_allow_html=True)