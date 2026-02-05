import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP & BRANDING
st.set_page_config(page_title="SMART CONSOL PLANNER - POWERED BY SUDATH", layout="wide")

st.markdown("""
    <style>
    .main-header { background: linear-gradient(90deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .color-box { width: 20px; height: 20px; display: inline-block; border-radius: 3px; margin-right: 10px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN SYSTEM (Stability First)
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        with st.form("login"):
            u = st.text_input("User ID")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN"):
                if u == "sudath" and p == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Invalid Login")
else:
    # 3. MAIN APP
    st.markdown('<div class="main-header"><h1>🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()
    
    # Logic Parameters (Standard 20GP)
    C_L, C_W, C_H, MAX_CBM = 585, 230, 235, 31.62
    
    st.subheader("📋 Manifest Entry & Validation")
    init_df = pd.DataFrame([{"Cargo":"P1","L":115,"W":115,"H":115,"Qty":10}])
    df_in = st.data_editor(init_df, num_rows="dynamic", use_container_width=True)
    
    if st.button("GENERATE VALIDATED LOADING PLAN", type="primary"):
        clean = df_in.dropna()
        errors = []
        total_vol = 0
        
        # Validation Logic
        for idx, row in clean.iterrows():
            if row['L'] > C_L or row['W'] > C_W or row['H'] > C_H:
                errors.append(f"❌ {row['Cargo']}: Exceeds Container dimensions!")
            total_vol += (row['L'] * row['W'] * row['H'] * row['Qty']) / 1000000

        if errors:
            for err in errors: st.error(err)
        elif total_vol > MAX_CBM:
            st.error(f"🚨 OVERLOAD: Total volume ({total_vol:.2f} CBM) exceeds 20GP capacity ({MAX_CBM} CBM)!")
        else:
            # Metrics
            util = (total_vol / MAX_CBM) * 100
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">Total Volume<br><b>{total_vol:.2f} CBM</b></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">Capacity<br><b>{MAX_CBM} CBM</b></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">Utilization<br><b>{util:.1f}%</b></div>', unsafe_allow_html=True)
            st.progress(util/100)

            # 3D Plotly Logic
            fig = go.Figure()
            # Container Wireframe
            fig.add_trace(go.Scatter3d(x=[0,C_L,C_L,0,0,0,C_L,C_L,0,0,C_L,C_L,C_L,C_L,0,0], y=[0,0,C_W,C_W,0,0,0,C_W,C_W,0,0,0,C_W,C_W,C_W,C_W], z=[0,0,0,0,0,C_H,C_H,C_H,C_H,C_H,C_H,0,0,C_H,C_H,0], mode='lines', line=dict(color='black', width=3), showlegend=False))

            colors = ["#004a99", "#ee7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            legend_html = "<div style='display: flex; flex-wrap: wrap; margin-top: 20px;'>"
            
            cx, cy, cz, mh = 0, 0, 0, 0
            for i, r in clean.iterrows():
                clr = colors[i % len(colors)]
                legend_html += f'<div style="margin-right:20px;"><span class="color-box" style="background:{clr}"></span>{r["Cargo"]}</div>'
                
                l, w, h = r['L'], r['W'], r['H']
                for _ in range(int(r['Qty'])):
                    if cx + l > C_L: cx = 0; cy += w
                    if cy + w > C_W: cy = 0; cz += mh; mh = 0
                    if cz + h <= C_H:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.8, alphahull=0, showlegend=False))
                        cx += l; mh = max(mh, h)
            
            legend_html += "</div>"
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # Cargo Color Key Display
            st.markdown("### 🎨 Cargo Color Key")
            st.markdown(legend_html, unsafe_allow_html=True)

st.markdown("<hr><center>SMART CONSOL PLANNER - POWERED BY SUDATH | v60.0</center>", unsafe_allow_html=True)
