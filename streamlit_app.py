import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# 1. SETUP & BRANDING
st.set_page_config(page_title="SMART CONSOL PLANNER - SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 28000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 28000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 28000}
}

# 2. LOGIN SYSTEM
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM LOGIN</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            # නිවැරදි User ID සහ Password මෙතන පරීක්ෂා කරයි
            if u.lower() == "sudath" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials! Please use ID: sudath and PWD: admin123")
else:
    # --- APP CONTENT STARTS HERE ---
    st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    specs = CONTAINERS[c_type]
    
    # Cargo Input Table
    st.subheader(f"📊 {c_type} Entry & Validation")
    df = st.data_editor(pd.DataFrame([
        {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Weight_kg": 500}
    ]), num_rows="dynamic", use_container_width=True)

    if st.button("GENERATE PLAN & PDF"):
        clean_df = df.dropna().copy()
        if not clean_df.empty:
            total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
            total_weight = (clean_df['Weight_kg'] * clean_df['Qty']).sum()
            util = (total_vol / specs['MAX_CBM']) * 100
            
            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Cargo", f"{total_vol:.2f} CBM")
            m2.metric("Utilization", f"{util:.1f}%")
            m3.metric("Total Weight", f"{total_weight:,.0f} kg")
            
            if total_vol > specs['MAX_CBM']:
                st.error(f"⚠️ VOLUME OVERLOAD! Max is {specs['MAX_CBM']} CBM")
            
            # 3D Plot
            fig = go.Figure()
            CL, CW, CH = specs['L'], specs['W'], specs['H']
            fig.add_trace(go.Scatter3d(x=[0,CL,CL,0,0,0,CL,CL,0,0,CL,CL,CL,CL,0,0], y=[0,0,CW,CW,0,0,0,CW,CW,0,0,0,CW,CW,CW,CW], z=[0,0,0,0,0,CH,CH,CH,CH,CH,CH,0,0,CH,CH,0], mode='lines', line=dict(color='black', width=3), showlegend=False))
            
            # Simple Packing Visualization
            cx, cy, cz, mh = 0, 0, 0, 0
            for idx, r in clean_df.iterrows():
                l, w, h = r['L'], r['W'], r['H']
                for _ in range(int(r['Qty'])):
                    if cx + l > CL: cx = 0; cy += w
                    if cy + w > CW: cy = 0; cz += mh; mh = 0
                    if cz + h <= CH:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color="orange", opacity=0.7, alphahull=0))
                        cx += l; mh = max(mh, h)
            
            fig.update_layout(scene=dict(aspectmode='data'))
            st.plotly_chart(fig, use_container_width=True)

            # PDF GENERATION
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(100, 10, f"Container: {c_type}")
            pdf.cell(90, 10, f"Total Vol: {total_vol:.2f} CBM", 0, 1)
            pdf.ln(5)
            
            # Table in PDF
            pdf.cell(50, 10, 'Cargo', 1); pdf.cell(30, 10, 'Qty', 1); pdf.cell(60, 10, 'L x W x H', 1); pdf.cell(50, 10, 'Weight (kg)', 1, 1)
            for _, r in clean_df.iterrows():
                pdf.cell(50, 10, str(r['Cargo']), 1)
                pdf.cell(30, 10, str(int(r['Qty'])), 1)
                pdf.cell(60, 10, f"{r['L']}x{r['W']}x{r['H']}", 1)
                pdf.cell(50, 10, f"{r['Weight_kg']:,}", 1, 1)
                
            pdf_data = pdf.output(dest='S').encode('latin-1')
            b64_pdf = base64.b64encode(pdf_data).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Report.pdf" style="padding:10px; background-color:green; color:white; border-radius:5px; text-decoration:none;">📥 DOWNLOAD PDF REPORT</a>', unsafe_allow_html=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
