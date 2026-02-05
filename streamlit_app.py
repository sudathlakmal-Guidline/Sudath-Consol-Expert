import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

# --- 1. CONFIG & LOGIN ---
st.set_page_config(page_title="SMART CONSOL", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

def check_login():
    if st.session_state.u_input.lower() == "sudath" and st.session_state.p_input == "admin123":
        st.session_state.auth = True
    else:
        st.error("Invalid Login! Try again.")

if not st.session_state.auth:
    st.title("🚢 SMART CONSOL SYSTEM")
    st.text_input("User ID", key="u_input")
    st.text_input("Password", type="password", key="p_input")
    st.button("LOGIN", on_click=check_login)
    st.stop()

# --- 2. APP CONTENT (If Authenticated) ---
st.success("Successfully Logged In!")
st.title("🚢 SMART CONSOL PLANNER - POWERED BY SUDATH")

if st.sidebar.button("LOGOUT"):
    st.session_state.auth = False
    st.rerun()

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0}
}

c_type = st.sidebar.selectbox("Container Type", list(CONTAINERS.keys()))
specs = CONTAINERS[c_type]

st.subheader(f"📊 {c_type} Cargo Entry")
df = st.data_editor(pd.DataFrame([
    {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Weight_kg": 500}
]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE 3D PLAN"):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        st.metric("Total Volume", f"{vol:.2f} CBM")
        
        # Simple 3D Visualization
        fig = go.Figure()
        CL, CW, CH = specs['L'], specs['W'], specs['H']
        fig.add_trace(go.Scatter3d(x=[0,CL,CL,0,0,0,CL,CL,0,0,CL,CL,CL,CL,0,0], 
                                   y=[0,0,CW,CW,0,0,0,CW,CW,0,0,0,CW,CW,CW,CW], 
                                   z=[0,0,0,0,0,CH,CH,CH,CH,CH,CH,0,0,CH,CH,0], 
                                   mode='lines', line=dict(color='black', width=3)))
        
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER</center>", unsafe_allow_html=True)
