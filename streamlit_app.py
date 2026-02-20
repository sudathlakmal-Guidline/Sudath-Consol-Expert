import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & STYLE (Your Original Layout) ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: white; }
    .watermark { position: fixed; bottom: 5px; right: 5px; opacity: 0.2; font-size: 12px; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# AI Setup
try:
    genai.configure(api_key="AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ")
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except: pass

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('sudath_consol_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL')")
    conn.commit(); conn.close()

init_db()

# --- 3. LOGIN (Original Simple Style) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("User ID / Email").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN", use_container_width=True):
            if u == "sudath.lakmal@gmail.com" and p == "853602795@@@vSL":
                st.session_state.auth = True; st.session_state.user = u
                st.rerun()
            else: st.error("Invalid Credentials")
    st.stop()

# --- 4. MAIN INTERFACE (As per image_aa61b4.png) ---
st.markdown('<h2 style="background-color:#004a99; color:white; text-align:center; padding:10px;">🚢 SMART CONSOL PRO - Powered by Sudath</h2>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 590, "W": 235, "H": 239, "MAX_CBM": 33.0},
    "40GP": {"L": 1203, "W": 235, "H": 239, "MAX_CBM": 67.0},
    "40HC": {"L": 1203, "W": 235, "H": 269, "MAX_CBM": 76.0}
}

col_main, col_side = st.columns([4, 1])

with col_side:
    st.info(f"👤 {st.session_state.user}")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

with col_main:
    st.subheader(f"📊 {c_type} Cargo Entry")
    df = st.data_editor(pd.DataFrame([{"Cargo": "PKG_01", "L": 100, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}]), num_rows="dynamic", use_container_width=True)
    
    if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
        specs = CONTAINERS[c_type]
        total_cbm = (df['L'] * df['W'] * df['H'] * df['Qty']).sum() / 1000000
        
        if total_cbm > specs['MAX_CBM']:
            st.error(f"❌ Capacity Exceeded! Total: {total_cbm:.2f} CBM")
        else:
            # 3D TIGHT LOADING LOGIC
            fig = go.Figure()
            colors = ['#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
            
            # Start from corner (0,0,0)
            curr_x, curr_y, curr_z = 0, 0, 0
            max_h_row = 0
            
            for i, row in df.iterrows():
                l, w, h, qty = row['L'], row['W'], row['H'], int(row['Qty'])
                color = colors[i % len(colors)]
                
                for _ in range(qty):
                    if curr_y + w > specs['W']: # Next Row
                        curr_y = 0; curr_x += l
                    if curr_x + l > specs['L']: # Next Layer
                        curr_x = 0; curr_y = 0; curr_z += max_h_row; max_h_row = 0
                    
                    # Drawing the box tightly
                    fig.add_trace(go.Mesh3d(
                        x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                        y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                        z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                        color=color, opacity=0.9, alphahull=0, name=row['Cargo'], showlegend=(_==0)
                    ))
                    curr_y += w
                    max_h_row = max(max_h_row, h)

            # Container Outline (Visualizing the 20GP shape)
            fig.add_trace(go.Box(x=[0, specs['L']], y=[0, specs['W']], z=[0, specs['H']], opacity=0, showlegend=False))
            
            fig.update_layout(
                scene=dict(
                    aspectmode='manual',
                    aspectratio=dict(x=specs['L']/100, y=specs['W']/100, z=specs['H']/100),
                    xaxis=dict(range=[0, specs['L']], title="Length"),
                    yaxis=dict(range=[0, specs['W']], title="Width"),
                    zaxis=dict(range=[0, specs['H']], title="Height")
                ),
                margin=dict(l=0, r=0, b=0, t=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Volume", f"{total_cbm:.2f} CBM")
            m2.metric("Utilization", f"{(total_cbm/specs['MAX_CBM'])*100:.1f}%")
            m3.metric("Total Weight", f"{df['Weight_kg'].sum()} kg")

            # Report Download
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "SMART CONSOL LOADING REPORT", 0, 1, 'C')
            pdf.set_font("Arial", '', 12); pdf.ln(10)
            pdf.cell(0, 10, f"Container: {c_type} | Utilization: {(total_cbm/specs['MAX_CBM'])*100:.1f}%", 0, 1)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 DOWNLOAD FINAL REPORT", data=pdf_bytes, file_name="Consol_Report.pdf", use_container_width=True)

# AI Sidebar
with st.sidebar:
    st.divider()
    st.subheader("🤖 AI Logistics Support")
    aq = st.text_input("Ask AI...")
    if st.button("Ask") and aq:
        try: res = ai_model.generate_content(aq); st.info(res.text)
        except: st.error("AI Offline")
