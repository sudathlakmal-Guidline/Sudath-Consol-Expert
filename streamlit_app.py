import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධති සැකසුම් (System Settings)
st.set_page_config(page_title="SMART CONSOL PLANNER - POWERED BY SUDATH", layout="wide", page_icon="🚢")

# UI එක ලස්සන කරන CSS
st.markdown("""
    <style>
    .main-title { background: linear-gradient(90deg, #002b5e 0%, #004a99 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 8px; height: 3.5em; width: 100%; font-weight: bold; }
    .stDataEditor { border: 1px solid #ddd; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. ආරක්ෂිත පිවිසුම (Secure Access)
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div style='text-align: center; padding-top: 50px;'><h1>🚢 SMART CONSOL SYSTEM</h1><p>Powered by Sudath</p></div>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN"):
                if u == "sudath" and p == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("වැරදි දත්ත! නැවත උත්සාහ කරන්න.")
else:
    # 3. ප්‍රධාන පද්ධතිය (Main Dashboard)
    st.markdown('<div class="main-title"><h1>🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.write(f"👤 User: **Sudath Admin**")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()
        st.divider()
        mod = st.radio("පද්ධති මෙවලම්:", ["📦 3D Consolidation", "🏗️ OOG Assessment"])

    if mod == "📦 3D Consolidation":
        st.subheader("📊 Cargo Manifest Entry")
        # මූලික දත්ත වගුව
        df = st.data_editor(pd.DataFrame([
            {"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10},
            {"Cargo": "P2", "L": 80, "W": 120, "H": 100, "Qty": 5}
        ]), num_rows="dynamic", use_container_width=True)
        
        if st.button("GENERATE 3D LOADING PLAN"):
            clean = df.dropna()
            fig = go.Figure()
            
            # Container Frame (20GP Standard)
            L, W, H = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L,L,0,0,0,L,L,0,0,L,L,L,L,0,0], y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], mode='lines', line=dict(color='black', width=4), showlegend=False))
            
            # 🎨 විවිධ Cargo වර්ග සඳහා වෙනස් වර්ණ (Color Palette)
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            
            cx, cy, cz, mh = 0, 0, 0, 0
            for i, r in clean.iterrows():
                c_clr = colors[i % len(colors)]
                l_val, w_val, h_val = r['L'], r['W'], r['H']
                first = True
                
                for _ in range(int(r['Qty'])):
                    if cx + l_val > L: cx = 0; cy += w_val
                    if cy + w_val > W: cy = 0; cz += mh; mh = 0
                    if cz + h_val <= H:
                        fig.add_trace(go.Mesh3d(
                            x=[cx,cx,cx+l_val,cx+l_val,cx,cx,cx+l_val,cx+l_val], 
                            y=[cy,cy+w_val,cy+w_val,cy,cy,cy+w_val,cy+w_val,cy], 
                            z=[cz,cz,cz,cz,cz+h_val,cz+h_val,cz+h_val,cz+h_val], 
                            color=c_clr, opacity=0.8, alphahull=0,
                            name=r['Cargo'] if first else "", showlegend=first
                        ))
                        cx += l_val; mh = max(mh, h_val); first = False
            
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
            st.success("✅ 3D Loading සැලසුම සාර්ථකව සකස් කරන ලදී.")

    else:
        st.subheader("🏗️ OOG Dimension Assessment")
        w_check = st.number_input("Cargo Width (cm)", value=250)
        if st.button("ANALYSIS"):
            if w_check > 230: st.error("🚨 OOG DETECTED: Special Equipment Required!")
            else: st.success("✅ STANDARD: Cargo fits in GP container.")

st.markdown("<hr><center>© 2024 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
