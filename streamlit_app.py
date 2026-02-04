import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

st.markdown("""
    <style>
    .header-style { background: #004a99; padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; font-family: sans-serif; }
    .stButton>button { background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN (Static for stability)
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.container():
        uid = st.text_input("User ID")
        ups = st.text_input("Password", type="password")
        if st.button("ENTER SYSTEM"):
            if uid == "sudath" and ups == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied!")
else:
    # 3. MAIN DASHBOARD
    st.markdown('<div class="header-style"><h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()
    
    menu = st.sidebar.radio("MENU:", ["📦 3D Consolidation", "🏗️ OOG Check"])

    if menu == "📦 3D Consolidation":
        st.subheader("📊 Manifest Entry")
        # Sample data with different cargo types
        init_data = pd.DataFrame([
            {"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10},
            {"Cargo": "P2", "L": 80, "W": 120, "H": 100, "Qty": 5}
        ])
        df = st.data_editor(init_data, num_rows="dynamic", use_container_width=True)
        
        if st.button("GENERATE COLOR-CODED 3D VIEW"):
            clean = df.dropna()
            fig = go.Figure()
            
            # Container Frame (20GP)
            L, W, H = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L,L,0,0,0,L,L,0,0,L,L,L,L,0,0], y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], mode='lines', line=dict(color='black', width=4), showlegend=False))
            
            # 🌈 Multi-Color Logic
            color_list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            
            cx, cy, cz, mh = 0, 0, 0, 0
            for i, r in clean.iterrows():
                # Assign unique color based on row index
                c_color = color_list[i % len(color_list)]
                l, w, h = r['L'], r['W'], r['H']
                
                # First box of each type to show in legend
                first_box = True
                
                for _ in range(int(r['Qty'])):
                    if cx + l > L: cx=0; cy+=w
                    if cy + w > W: cy=0; cz+=mh; mh=0
                    if cz + h <= H:
                        fig.add_trace(go.Mesh3d(
                            x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], 
                            y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], 
                            z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], 
                            color=c_color, opacity=0.8, alphahull=0,
                            name=r['Cargo'] if first_box else "",
                            showlegend=first_box
                        ))
                        cx+=l; mh=max(mh, h)
                        first_box = False # Only show legend once per cargo type
            
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("OOG Assessment Module Ready.")

st.markdown("<hr><center>SMART CONSOL PLANNER - BY SUDATH | v50.0 PRO</center>", unsafe_allow_html=True)
