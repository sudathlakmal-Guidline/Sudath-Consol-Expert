import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- 1. SETUP & PAGE CONFIG ---
st.set_page_config(page_title="SMART CONSOL PLANNER", layout="wide")

# Container Specifications
CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0}
}

# --- 2. LOGIN SYSTEM ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def check_login():
    # මෙතනදී අකුරු වල වෙනස (sudath vs Sudath) බලපාන්නේ නැති ලෙස සකසා ඇත
    if st.session_state.u_name.strip().lower() == "sudath" and st.session_state.p_word == "admin123":
        st.session_state.auth = True
    else:
        st.error("Invalid Credentials! Please try again.")

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM LOGIN</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        st.text_input("User ID", key="u_name")
        st.text_input("Password", type="password", key="p_word")
        st.button("LOGIN", on_click=check_login, use_container_width=True)
    st.stop()

# --- 3. MAIN APP CONTENT ---
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.success(f"Logged in as: Sudath")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

specs = CONTAINERS[c_type]

# Cargo Data Entry
st.subheader(f"📊 {c_type} Cargo Entry & Validation")
df = st.data_editor(pd.DataFrame([
    {"Cargo": "Shipment_1", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}
]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE 3D LOADING PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        # Calculations
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = (clean_df['Weight_kg'] * clean_df['Qty']).sum()
        utilization = (total_vol / specs['MAX_CBM']) * 100

        # Metrics display
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Volume", f"{total_vol:.2f} CBM")
        col2.metric("Utilization", f"{utilization:.1f}%")
        col3.metric("Total Weight", f"{total_weight:,.0f} kg")

        if utilization > 100:
            st.error(f"⚠️ OVERLOAD! Total volume ({total_vol:.2f} CBM) exceeds {c_type} capacity.")

        # 3D Visualization
        fig = go.Figure()
        L, W, H = specs['L'], specs['W'], specs['H']
        
        # Container Box
        fig.add_trace(go.Scatter3d(
            x=[0,L,L,0,0,0,L,L,0,0,L,L,CL,CL,0,0], 
            y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], 
            z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], 
            mode='lines', line=dict(color='black', width=4), name="Container"
        ))

        # Packing Algorithm (Basic Visual)
        cx, cy, cz, max_h = 0, 0, 0, 0
        colors = ["blue", "orange", "green", "red", "purple"]
        
        for i, row in clean_df.iterrows():
            c_l, c_w, c_h = row['L'], row['W'], row['H']
            color = colors[i % len(colors)]
            for _ in range(int(row['Qty'])):
                if cx + c_l > L: cx = 0; cy += c_w
                if cy + c_w > W: cy = 0; cz += max_h; max_h = 0
                
                if cz + c_h <= H:
                    fig.add_trace(go.Mesh3d(
                        x=[cx, cx, cx+c_l, cx+c_l, cx, cx, cx+c_l, cx+c_l],
                        y=[cy, cy+c_w, cy+c_w, cy, cy, cy+c_w, cy+c_w, cy],
                        z=[cz, cz, cz, cz, cz+c_h, cz+c_h, cz+c_h, cz+c_h],
                        color=color, opacity=0.6, alphahull=0
                    ))
                    cx += c_l
                    max_h = max(max_h, c_h)

        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig, use_container_width=True)

        # PDF REPORT GENERATION
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=12)
            pdf.cell(95, 10, f"Container Type: {c_type}")
            pdf.cell(95, 10, f"Total Volume: {total_vol:.2f} CBM", 0, 1)
            pdf.cell(95, 10, f"Utilization: {utilization:.1f}%")
            pdf.cell(95, 10, f"Total Weight: {total_weight:,.0f} kg", 0, 1)
            pdf.ln(10)

            # Table Header
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(50, 10, 'Cargo', 1, 0, 'C', True)
            pdf.cell(30, 10, 'Qty', 1, 0, 'C', True)
            pdf.cell(60, 10, 'Dimensions (cm)', 1, 0, 'C', True)
            pdf.cell(50, 10, 'Weight (kg)', 1, 1, 'C', True)

            for _, r in clean_df.iterrows():
                pdf.cell(50, 10, str(r['Cargo']), 1)
                pdf.cell(30, 10, str(int(r['Qty'])), 1, 0, 'C')
                pdf.cell(60, 10, f"{r['L']}x{r['W']}x{r['H']}", 1, 0, 'C')
                pdf.cell(50, 10, f"{r['Weight_kg']:,}", 1, 1, 'C')

            pdf_output = pdf.output(dest='S').encode('latin-1')
            b64_pdf = base64.b64encode(pdf_output).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Loading_Plan_Sudath.pdf" style="display:inline-block; padding:15px 25px; background-color:#28a745; color:white; text-decoration:none; border-radius:8px; font-weight:bold;">📥 DOWNLOAD PDF REPORT</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"PDF Error: {e}")

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
