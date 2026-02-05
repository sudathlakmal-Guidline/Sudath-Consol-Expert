import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="SMART CONSOL PRO - SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 28000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 28000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 28000}
}

# --- 2. LOGIN SYSTEM ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN", use_container_width=True):
            if u.strip().lower() == "sudath" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Invalid Credentials")
    st.stop()

# --- 3. MAIN APP UI ---
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.success("✅ Logged in: Sudath")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

st.subheader(f"📊 {c_type} Cargo Entry & Smart Validation")

# Data Entry Table
df = st.data_editor(pd.DataFrame([
    {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Weight_kg": 500, "Allow_Rotate": True},
    {"Cargo":"Shipment_2", "L":115, "W":115, "H":115, "Qty":10, "Weight_kg": 1500, "Allow_Rotate": False}
]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        # --- FIX 1: Heavy cargo at the bottom ---
        clean_df = clean_df.sort_values(by='Weight_kg', ascending=False)
        
        # --- FIX 2: Correct Total Gross Weight calculation ---
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = (clean_df['Weight_kg'] * clean_df['Qty']).sum()
        util_pct = (total_vol / specs['MAX_CBM']) * 100
        
        # Display Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Cargo", f"{total_vol:.2f} CBM")
        m2.metric("Capacity", f"{specs['MAX_CBM']} CBM")
        m3.metric("Utilization", f"{util_pct:.1f}%")
        m4.metric("Total Gross Weight", f"{total_weight:,.0f} kg")
        
        # Progress Bar for Utilization
        st.progress(min(util_pct/100, 1.0))
        if total_weight > specs['MAX_KG']:
            st.warning(f"⚠️ WEIGHT ALERT: Total load ({total_weight:,.0f} kg) exceeds container capacity!")

        # --- 3D Visualization ---
        fig = go.Figure()
        L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
        
        # Container Outline
        fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))

        cx, cy, cz, layer_h = 0, 0, 0, 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        # --- FIX 3: Color Key Legend ---
        st.write("### 📦 Color Key Legend")
        legend_cols = st.columns(len(clean_df))
        
        for idx, row in clean_df.reset_index().iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors[idx % len(colors)]
            legend_cols[idx].markdown(f"<div style='background-color:{clr}; padding:8px; border-radius:5px; color:white; text-align:center; font-weight:bold;'>{row['Cargo']}</div>", unsafe_allow_html=True)
            
            # Cargo Placement Logic
            for _ in range(int(row['Qty'])):
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo']))
                    cx += l
                    layer_h = max(layer_h, h)

        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF REPORT GENERATION ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font("Arial", size=11)
        pdf.cell(95, 10, f"Container: {c_type}")
        pdf.cell(95, 10, f"Total Gross Weight: {total_weight:,.0f} kg", 0, 1)
        pdf.cell(95, 10, f"Utilization: {util_pct:.1f}%")
        pdf.ln(15)
        
        # Report Table Header
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(40, 10, 'Cargo', 1, 0, 'C', True)
        pdf.cell(20, 10, 'Qty', 1, 0, 'C', True)
        pdf.cell(50, 10, 'Dim (L x W x H)', 1, 0, 'C', True)
        pdf.cell(40, 10, 'Unit Wt (kg)', 1, 0, 'C', True)
        pdf.cell(40, 10, 'Rotate', 1, 1, 'C', True)
        
        # Report Table Data
        for _, r in clean_df.iterrows():
            pdf.cell(40, 10, str(r['Cargo']), 1)
            pdf.cell(20, 10, str(int(r['Qty'])), 1, 0, 'C')
            pdf.cell(50, 10, f"{r['L']}x{r['W']}x{r['H']}", 1, 0, 'C')
            pdf.cell(40, 10, f"{r['Weight_kg']:,}", 1, 0, 'C')
            pdf.cell(40, 10, "Yes" if r['Allow_Rotate'] else "No", 1, 1, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Consol_Plan.pdf" style="display:inline-block; padding:15px; background-color:#28a745; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📥 DOWNLOAD PDF REPORT</a>', unsafe_allow_html=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
