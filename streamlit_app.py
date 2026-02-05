import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# 1. SETUP & BRANDING
st.set_page_config(page_title="SMART CONSOL PLANNER - POWERED BY SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0}
}

st.markdown("""
    <style>
    .header { background: #004a99; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); text-align: center; }
    .stButton>button { background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; width: 100%; height: 3.5em; }
    .color-box { display: inline-block; width: 18px; height: 18px; border-radius: 3px; margin-right: 8px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN SYSTEM
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u.strip().lower() == "sudath" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
else:
    st.markdown('<div class="header"><h1>🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1></div>', unsafe_allow_html=True)
    with st.sidebar:
        c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    specs = CONTAINERS[c_type]
    st.subheader(f"📊 {c_type} Entry & Smart Validation")
    
    df = st.data_editor(pd.DataFrame([
        {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Gross_Weight_kg": 500, "Allow_Rotate": True}
    ]), num_rows="dynamic", use_container_width=True)

    if st.button("GENERATE VALIDATED 3D PLAN"):
        clean_df = df.dropna().copy()
        if not clean_df.empty:
            clean_df['Vol_Unit'] = (clean_df['L'] * clean_df['W'] * clean_df['H']) / 1000000
            total_vol = (clean_df['Vol_Unit'] * clean_df['Qty']).sum()
            total_weight = clean_df['Gross_Weight_kg'].sum()

            util = (total_vol / specs['MAX_CBM']) * 100
            
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f'<div class="metric-card">Total Cargo<br><h3>{total_vol:.2f} CBM</h3></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card">Capacity<br><h3>{specs["MAX_CBM"]} CBM</h3></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card">Utilization<br><h3>{util:.1f}%</h3></div>', unsafe_allow_html=True)
            with m4: st.markdown(f'<div class="metric-card">Total Weight<br><h3>{total_weight:,.0f} kg</h3></div>', unsafe_allow_html=True)
            
            st.progress(min(util/100, 1.0))
            
            clean_df = clean_df.sort_values(by=['Gross_Weight_kg', 'Vol_Unit'], ascending=False)
            fig = go.Figure()
            CL, CW, CH = specs['L'], specs['W'], specs['H']
            fig.add_trace(go.Scatter3d(x=[0,CL,CL,0,0,0,CL,CL,0,0,CL,CL,CL,CL,0,0], y=[0,0,CW,CW,0,0,0,CW,CW,0,0,0,CW,CW,CW,CW], z=[0,0,0,0,0,CH,CH,CH,CH,CH,CH,0,0,CH,CH,0], mode='lines', line=dict(color='black', width=3), showlegend=False))
            
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
            cx, cy, cz, mh = 0, 0, 0, 0
            for idx, r in clean_df.iterrows():
                clr = colors[idx % len(colors)]
                l, w, h = r['L'], r['W'], r['H']
                for _ in range(int(r['Qty'])):
                    u_l, u_w = l, w
                    if r['Allow_Rotate'] and (cx + l > CL) and (cx + w <= CL and l <= CW): u_l, u_w = w, l
                    if cx + u_l > CL: cx = 0; cy += u_w
                    if cy + u_w > CW: cy = 0; cz += mh; mh = 0
                    if cz + h <= CH:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+u_l,cx+u_l,cx,cx,cx+u_l,cx+u_l], y=[cy,cy+u_w,cy+u_w,cy,cy,cy+u_w,cy+u_w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.7, alphahull=0))
                        cx += u_l; mh = max(mh, h)

            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

            # --- PDF GENERATION ---
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(100, 10, f"Container Type: {c_type}")
            pdf.cell(90, 10, f"Date: 2026-02-05", 0, 1)
            pdf.cell(100, 10, f"Total Volume: {total_vol:.2f} CBM")
            pdf.cell(90, 10, f"Utilization: {util:.1f}%", 0, 1)
            pdf.cell(100, 10, f"Total Weight: {total_weight:,.0f} kg", 0, 1)
            pdf.ln(5)
            
            # Table Header
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(60, 10, 'Cargo', 1, 0, 'C', True)
            pdf.cell(30, 10, 'Qty', 1, 0, 'C', True)
            pdf.cell(40, 10, 'Dimensions', 1, 0, 'C', True)
            pdf.cell(60, 10, 'Total Weight (kg)', 1, 1, 'C', True)
            
            for _, r in clean_df.iterrows():
                pdf.cell(60, 10, str(r['Cargo']), 1)
                pdf.cell(30, 10, str(int(r['Qty'])), 1, 0, 'C')
                pdf.cell(40, 10, f"{r['L']}x{r['W']}x{r['H']}", 1, 0, 'C')
                pdf.cell(60, 10, f"{r['Gross_Weight_kg']:,}", 1, 1, 'C')
            
            pdf_output = pdf.output(dest="S").encode("latin-1")
            b64_pdf = base64.b64encode(pdf_output).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Loading_Plan.pdf" style="display: inline-block; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 DOWNLOAD PDF REPORT</a>', unsafe_allow_html=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
