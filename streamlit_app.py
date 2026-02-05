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
            
            # 3D Plotly Figure
            fig = go.Figure()
            CL, CW, CH = specs['L'], specs['W'], specs['H']
            fig.add_trace(go.Scatter3d(x=[0,CL,CL,0,0,0,CL,CL,0,0,CL,CL,CL,CL,0,0], y=[0,0,CW,CW,0,0,0,CW,CW,0,0,0,CW,CW,CW,CW], z=[0,0,0,0,0,CH,CH,CH,CH,CH,CH,0,0,CH,CH,0], mode='lines', line=dict(color='black', width=3), showlegend=False))
            
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
            cx, cy, cz, mh = 0, 0, 0, 0
            for idx, r in clean_df.iterrows():
                clr = colors[idx % len(colors)]
                for _ in range(int(r['Qty'])):
                    l, w, h = r['L'], r['W'], r['H']
                    if cx + l > CL: cx = 0; cy += w
                    if cy + w > CW: cy = 0; cz += mh; mh = 0
                    if cz + h <= CH:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.7, alphahull=0))
                        cx += l; mh = max(mh, h)

            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

            # --- PDF Report Generation ---
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
                pdf.cell(100, 10, f"Total Volume: {total_vol:.2f} CBM")
                pdf.cell(90, 10, f"Total Weight: {total_weight:,.0f} kg", 0, 1)
                pdf.ln(10)
                
                # Table
                pdf.cell(60, 10, 'Cargo', 1)
                pdf.cell(30, 10, 'Qty', 1)
                pdf.cell(50, 10, 'Dimensions', 1)
                pdf.cell(50, 10, 'Weight (kg)', 1, 1)
                
                for _, r in clean_df.iterrows():
                    pdf.cell(60, 10, str(r['Cargo']), 1)
                    pdf.cell(30, 10, str(int(r['Qty'])), 1)
                    pdf.cell(50, 10, f"{r['L']}x{r['W']}x{r['H']}", 1)
                    pdf.cell(50, 10, f"{r['Gross_Weight_kg']:,}", 1, 1)
                
                pdf_data = pdf.output(dest='S').encode('latin-1')
                b64_pdf = base64.b64encode(pdf_data).decode()
                st.markdown(f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Loading_Plan.pdf" style="display:inline-block; padding:12px 24px; background-color:#28a745; color:white; text-decoration:none; border-radius:8px; font-weight:bold; margin-top:20px;">📥 DOWNLOAD PDF REPORT</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
