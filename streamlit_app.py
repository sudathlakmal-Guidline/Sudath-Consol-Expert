import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- 1. පද්ධති සැකසුම් ---
st.set_page_config(page_title="SMART CONSOL - SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0}
}

# --- 2. ලොගින් පද්ධතිය (LOGIN SYSTEM) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        u = st.text_input("User ID (sudath)")
        p = st.text_input("Password (admin123)", type="password")
        if st.button("LOGIN", use_container_width=True):
            if u.strip().lower() == "sudath" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# --- 3. ප්‍රධාන පද්ධතිය (MAIN APP) ---
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.write(f"✅ Logged in as: Sudath")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

specs = CONTAINERS[c_type]
L_max, W_max, H_max = specs['L'], specs['W'], specs['H']

st.subheader(f"📊 {c_type} Entry & Validation")
df = st.data_editor(pd.DataFrame([
    {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Weight_kg": 500}
]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE 3D LOADING PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        # ගණනය කිරීම්
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = (clean_df['Weight_kg'] * clean_df['Qty']).sum()
        util = (total_vol / specs['MAX_CBM']) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Volume", f"{total_vol:.2f} CBM")
        col2.metric("Utilization", f"{util:.1f}%")
        col3.metric("Total Weight", f"{total_weight:,.0f} kg")

        # --- 3D Visualization ---
        fig = go.Figure()
        
        # කන්ටේනරයේ රාමුව ඇඳීම (Container Outline)
        fig.add_trace(go.Scatter3d(
            x=[0, L_max, L_max, 0, 0, 0, L_max, L_max, 0, 0, L_max, L_max, L_max, L_max, 0, 0],
            y=[0, 0, W_max, W_max, 0, 0, 0, W_max, W_max, 0, 0, 0, W_max, W_max, W_max, W_max],
            z=[0, 0, 0, 0, 0, H_max, H_max, H_max, H_max, H_max, H_max, 0, 0, H_max, H_max, 0],
            mode='lines', line=dict(color='black', width=4), name="Container"
        ))

        # කාගෝ පෙට්ටි ඇඳීම
        cx, cy, cz, layer_h = 0, 0, 0, 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for idx, row in clean_df.iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors[idx % len(colors)]
            for _ in range(int(row['Qty'])):
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(
                        x=[cx, cx, cx+l, cx+l, cx, cx, cx+l, cx+l],
                        y=[cy, cy+w, cy+w, cy, cy, cy+w, cy+w, cy],
                        z=[cz, cz, cz, cz, cz+h, cz+h, cz+h, cz+h],
                        color=clr, opacity=0.7, alphahull=0
                    ))
                    cx += l
                    layer_h = max(layer_h, h)

        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF Report ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(100, 10, f"Container: {c_type}")
        pdf.cell(90, 10, f"Total Vol: {total_vol:.2f} CBM", 0, 1)
        pdf.ln(5)
        
        pdf.cell(50, 10, 'Cargo', 1); pdf.cell(30, 10, 'Qty', 1); pdf.cell(60, 10, 'Dimensions', 1); pdf.cell(50, 10, 'Weight', 1, 1)
        for _, r in clean_df.iterrows():
            pdf.cell(50, 10, str(r['Cargo']), 1)
            pdf.cell(30, 10, str(int(r['Qty'])), 1)
            pdf.cell(60, 10, f"{r['L']}x{r['W']}x{r['H']}", 1)
            pdf.cell(50, 10, f"{r['Weight_kg']:,} kg", 1, 1)

        pdf_data = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_data).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Report.pdf" style="display:inline-block; padding:15px; background-color:green; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📥 DOWNLOAD PDF REPORT</a>', unsafe_allow_html=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
