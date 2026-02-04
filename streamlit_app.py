import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

# ==========================================
# 1. CORE SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(page_title="SUDATH LOGISTICS PRO", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .report-header { background: linear-gradient(90deg, #001f3f 0%, #0074D9 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; }
    .metric-card { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .dg-critical { border-left: 5px solid #FF4136; background-color: #FFFAFA; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SECURITY & AUTHENTICATION
# ==========================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

def check_login():
    st.markdown("<div class='report-header'><h1>🔐 FREIGHT INTELLIGENCE GATEWAY</h1></div><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("Login Form"):
            u_email = st.text_input("Authorized Email", placeholder="sudath@expert.com")
            u_pass = st.text_input("Access Key", type="password")
            submitted = st.form_submit_button("UNLOCK SYSTEM", use_container_width=True)
            if submitted:
                if u_email == "sudath@expert.com" and u_pass == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Credentials")

if not st.session_state.auth:
    check_login()
else:
    # ==========================================
    # 3. GLOBAL DATA & SPECS
    # ==========================================
    EQ_SPECS = {
        "20GP": {"L": 589, "W": 235, "H": 239, "Payload": 28200, "CBM": 33.1},
        "40HC": {"L": 1203, "W": 235, "H": 269, "Payload": 28600, "CBM": 76.2}
    }

    # ==========================================
    # 4. SIDEBAR NAVIGATION
    # ==========================================
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3067/3067451.png", width=100)
        st.title("SUDATH NAVIGATOR")
        st.markdown(f"**User:** Admin Sudath\n**Session:** Active")
        if st.button("🔒 LOGOUT"):
            st.session_state.auth = False
            st.rerun()
        st.divider()
        module = st.radio("SELECT MISSION CRITICAL MODULE:", 
                          ["📦 CONSOL PLANNER", "🏗️ OOG ASSESSMENT", "☣️ IMDG COMPLIANCE"])
        st.divider()
        st.caption(f"System Time: {datetime.now().strftime('%H:%M:%S')}")

    # ==========================================
    # 5. MODULE 1: CONSOLIDATION PLANNER
    # ==========================================
    if module == "📦 CONSOL PLANNER":
        st.markdown("<div class='report-header'><h2>📦 ADVANCED CONSOLIDATION ENGINE</h2></div><br>", unsafe_allow_html=True)
        
        # --- DATA INPUT SECTION ---
        st.subheader("1. Manifest Load List")
        input_df = pd.DataFrame([
            {"Item": "Cargo_A", "L": 120, "W": 100, "H": 100, "Qty": 10, "Weight_kg": 500, "Stackable": True},
            {"Item": "Cargo_B", "L": 200, "W": 120, "H": 150, "Qty": 5, "Weight_kg": 1200, "Stackable": False}
        ])
        editor_df = st.data_editor(input_df, num_rows="dynamic", use_container_width=True, key="ed_v31")

        # --- CALCULATION LOGIC ---
        if st.button("🚀 INITIATE LOADING SIMULATION", use_container_width=True):
            clean_df = editor_df.dropna()
            tot_wgt = (clean_df['Weight_kg'] * clean_df['Qty']).sum()
            tot_cbm = ((clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']) / 1000000).sum()
            
            selected_eq = "20GP" if tot_cbm < 28 and tot_wgt < 26000 else "40HC"
            
            # --- ANALYTICS CARDS ---
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Weight", f"{tot_wgt:,.0f} kg")
            with c2: st.metric("Total Volume", f"{tot_cbm:.2f} CBM")
            with c3: st.metric("Best Equipment", selected_eq)
            with c4: 
                util = (tot_cbm / EQ_SPECS[selected_eq]['CBM']) * 100
                st.metric("Utilization", f"{util:.1f}%")

            # --- 3D VISUALIZATION ENGINE ---
            st.subheader("2. Loading Pattern (3D)")
            fig = go.Figure()
            L, W, H = EQ_SPECS[selected_eq]["L"], EQ_SPECS[selected_eq]["W"], EQ_SPECS[selected_eq]["H"]
            
            # Container Frame
            fig.add_trace(go.Scatter3d(x=
