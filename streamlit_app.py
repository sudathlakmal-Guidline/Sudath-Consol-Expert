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

# --- 2. LOGIN ---
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

# --- 3. MAIN APP ---
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.success("✅ Logged in: Sudath")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

st.subheader(f"📊 {c_type} Cargo Entry & Smart Validation")

# දත්ත ඇතුළත් කිරීමේ වගුව
df = st.data_editor(pd.DataFrame([
    {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Weight_kg": 500},
    {"Cargo":"Shipment_2", "L":115, "W":115, "H":115, "Qty":10, "Weight_kg": 1500}
]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        # --- නිවැරදි කිරීම 1: බර වැඩි භාණ්ඩ මුලින්ම ඇසිරීමට පෙළගැස්වීම (Sorting) ---
        clean_df = clean_df.sort_values(by='Weight_kg', ascending=False)
        
        # --- නිවැරදි කිරීම 2: මුළු බර සහ පරිමාව ගණනය කිරීම ---
        clean_df['Line_CBM'] = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']) / 1000000
        clean_df['Line_Weight'] = clean_df['Weight_kg'] * clean_df['Qty']
        
        total_vol = clean_df['Line_CBM'].sum()
        total_weight = clean_df['Line_Weight'].sum() # මුළු බර එකතුව මෙතැනින් නිවැරදි වේ
        util_pct = (total_vol / specs['MAX_CBM']) * 100
        
        # සංඛ්‍යා පෙන්වීම
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{total_vol:.2f} CBM")
        m2.metric("Capacity", f"{specs['MAX_CBM']} CBM")
        m3.metric("Utilization", f"{util_pct:.1f}%")
        m4.metric("Total Gross Weight", f"{total_weight:,.0f} kg")
        
        st.progress(min(util_pct/100, 1.0))
        if total_weight > specs['MAX_KG']:
            st.error(f"⚠️ WEIGHT ALERT: {total_weight:,.0f} kg exceeds limit!")

        # --- 3D Visualization ---
        fig = go.Figure()
        L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
        
        # Container Outline
        fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))

        cx, cy, cz, layer_h = 0, 0, 0, 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        st.write("### 📦 Color Key Legend")
        l_cols = st.columns(len(clean_df))
        
        # බර භාණ්ඩ යටට එන ලෙස ඇසිරීම
        for idx, row in clean_df.reset_index().iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors[idx % len(colors)]
            l_cols[idx].markdown(f"<div style='background-color:{clr}; padding:8px; border-radius:5px; color:white; text-align:center; font-weight:bold;'>{row['Cargo']} ({row['Weight_kg']}kg)</div>", unsafe_allow_html=True)
            
            for _ in range(int(row['Qty'])):
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo']))
                    cx += l
                    layer_h = max(layer_h, h)

        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font("Arial", size=11)
        pdf.cell(95, 10, f"Total Gross Weight: {total_weight:,.0f} kg")
        pdf.ln(15)
        
        for _, r in clean_df.iterrows():
            pdf.cell(190, 10, f"{r['Cargo']} - Qty: {int(r['Qty'])} - Line Weight: {r['Weight_kg'] * r['Qty']:,} kg", 1, 1)

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Consol_Report.pdf" style="display:inline-block; padding:15px; background-color:#28a745; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📥 DOWNLOAD REPORT</a>', unsafe_allow_html=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
