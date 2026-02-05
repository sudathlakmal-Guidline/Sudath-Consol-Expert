import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP & BRANDING
st.set_page_config(page_title="SMART CONSOL PLANNER - POWERED BY SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 33.0},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 67.0},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 76.0}
}

st.markdown("""
    <style>
    .header { background: #004a99; padding: 20px; border-radius: 10px; color: white; text-align: center; }
    .stButton>button { background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; width: 100%; height: 3.5em; }
    .nav-bar { background: #e1e4e8; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center; font-weight: bold; color: #004a99; }
    .color-key { display: inline-block; width: 20px; height: 20px; border-radius: 3px; margin-right: 5px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.columns([1,1.5,1])[1]:
        st.markdown("<h2 style='text-align: center;'>🚢 LOGIN</h2>", unsafe_allow_html=True)
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "sudath" and p == "admin123": st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied")
else:
    # 3. INTERFACE
    st.markdown('<div class="header"><h1>🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-bar">MENU: [📦 3D PLANNER] | [🏗️ OOG CHECK] | [🔄 AUTO-ROTATE]</div>', unsafe_allow_html=True)

    with st.sidebar:
        c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
        if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

    specs = CONTAINERS[c_type]
    st.subheader(f"📊 {c_type} Manifest & Smart Validation")
    
    df = st.data_editor(pd.DataFrame([
        {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":10, "Allow_Rotate": True}
    ]), num_rows="dynamic", use_container_width=True)

    if st.button("RUN SMART 3D PLAN"):
        clean_df = df.dropna()
        errors = []
        shipments_data = []
        total_vol = 0
        
        # Validation & CBM Calculation
        for i, r in clean_df.iterrows():
            vol = (r['L'] * r['W'] * r['H'] * r['Qty']) / 1000000
            total_vol += vol
            shipments_data.append({"name": r['Cargo'], "vol": vol, "dims": (r['L'], r['W'], r['H']), "rotate": r['Allow_Rotate']})

        # Check Overload
        if total_vol > specs['MAX_CBM']:
            st.error(f"🚨 OVERLOAD: Total {total_vol:.2f} CBM exceeds {c_type} limit ({specs['MAX_CBM']} CBM)!")
            # 💡 ADVICE LOGIC
            sorted_shipments = sorted(shipments_data, key=lambda x: x['vol'], reverse=True)
            st.info(f"💡 **Sudath's Advice:** To proceed, try holding Shipment **'{sorted_shipments[0]['name']}'** ({sorted_shipments[0]['vol']:.2f} CBM) to clear space.")
        else:
            # 3D Plotly Logic
            fig = go.Figure()
            CL, CW, CH = specs['L'], specs['W'], specs['H']
            fig.add_trace(go.Scatter3d(x=[0,CL,CL,0,0,0,CL,CL,0,0,CL,CL,CL,CL,0,0], y=[0,0,CW,CW,0,0,0,CW,CW,0,0,0,CW,CW,CW,CW], z=[0,0,0,0,0,CH,CH,CH,CH,CH,CH,0,0,CH,CH,0], mode='lines', line=dict(color='black', width=3), showlegend=False))

            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
            cx, cy, cz, mh = 0, 0, 0, 0
            legend_html = "<div style='margin-top:20px;'><b>🎨 Cargo Color Key:</b><br>"

            for i, r in clean_df.iterrows():
                l, w, h = r['L'], r['W'], r['H']
                clr = colors[i % len(colors)]
                legend_html += f'<span class="color-key" style="background:{clr}"></span> {r["Cargo"]} &nbsp;&nbsp;'
                
                for _ in range(int(r['Qty'])):
                    u_l, u_w = l, w
                    # Rotation Check
                    if r['Allow_Rotate']
