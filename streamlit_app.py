import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. සැකසුම් (Configuration)
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# ලස්සන මෝස්තරය (Styling)
st.markdown("""
    <style>
    .header-box { background: #004a99; padding: 20px; border-radius: 10px; color: white; text-align: center; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #004a99; color: white; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# 2. සරල පිවිසුම් පද්ධතිය (Simple Login - No DB needed)
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.container():
        st.info("Please enter your Admin credentials to access the planner.")
        user_input = st.text_input("User ID")
        pass_input = st.text_input("Password", type="password")
        if st.button("ENTER SYSTEM"):
            # මෙතනින් ඔයාට ඕනෑම User ID එකක් සහ Password එකක් දීලා ලොග් වෙන්න පුළුවන්
            if user_input == "sudath" and pass_input == "admin123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials! Try: sudath / admin123")
else:
    # 3. ප්‍රධාන පද්ධතිය (Main Dashboard)
    st.markdown('<div class="header-box"><h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()
    
    mode = st.sidebar.radio("MENU:", ["📦 3D Consolidation", "🏗️ OOG Check"])

    if mode == "📦 3D Consolidation":
        st.subheader("📊 Manifest Entry")
        # මූලික දත්ත වගුව
        df = st.data_editor(pd.DataFrame([{"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10}]), num_rows="dynamic")
        
        if st.button("GENERATE 3D VIEW"):
            clean_df = df.dropna()
            fig = go.Figure()
            # Container Wireframe (20GP: 585 x 230 x 235)
            L, W, H = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L,L,0,0,0,L,L,0,0,L,L,L,L,0,0], y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], mode='lines', line=dict(color='black', width=4)))
            
            # Simple Packing Logic
            cx, cy, cz, max_h = 0, 0, 0, 0
            for i, row in clean_df.iterrows():
                l, w, h = row['L'], row['W'], row['H']
                for _ in range(int(row['Qty'])):
                    if cx + l > L: cx = 0; cy += w
                    if cy + w > W: cy = 0; cz += max_h; max_h = 0
                    if cz + h <= H:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color="blue", opacity=0.7, alphahull=0))
                        cx += l; max_h = max(max_h, h)
            
            fig.update_layout(scene=dict(aspectmode='data'))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("🏗️ OOG ASSESSMENT")
        width = st.number_input("Cargo Width (cm)", value=250)
        if st.button("ANALYZE"):
            if width > 230: st.error("🚨 OOG DETECTED! Needs Special Equipment.")
            else: st.success("✅ STANDARD SIZE - Fits in GP Container.")

st.markdown("<hr><center>SMART CONSOL PLANNER - BY SUDATH | v45.0 FINAL</center>", unsafe_allow_html=True)
