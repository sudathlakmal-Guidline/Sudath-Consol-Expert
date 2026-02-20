import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & ORIGINAL DESIGN STYLE ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

# AI Setup
try:
    genai.configure(api_key="AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ")
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except:
    pass

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .main-header { background-color: #004a99; color: white; text-align: center; padding: 10px; border-radius: 5px; }
    .stButton>button { background-color: #28a745; color: white; border-radius: 5px; width: 100%; }
    .watermark { position: fixed; bottom: 5px; right: 5px; opacity: 0.2; font-size: 12px; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. DATABASE (Stable Version) ---
def get_db_connection():
    return sqlite3.connect('sudath_final_fixed.db', check_same_thread=False)

def init_db():
    conn = get_db_connection(); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)')
    conn.commit(); conn.close()

init_db()

# --- 3. LOGIN & AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    u = st.text_input("User ID / Email").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u == "sudath.lakmal@gmail.com" and p == "853602795@@@vSL":
            st.session_state.auth = True; st.session_state.user = u
            st.rerun()
        else: st.error("Invalid Credentials")
    st.stop()

# --- 4. SIDEBAR (As per image_aa6cde.png) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2343/2343894.png", width=60)
    st.markdown(f"✅ **User:** `{st.session_state.user}`")
    
    st.divider()
    st.markdown("### 👨‍💼 ADMIN CONTROL")
    if st.button("📊 VIEW USER REPORTS"):
        conn = get_db_connection()
        st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn))
        conn.close()
    
    st.divider()
    c_type = st.selectbox("Select Container Type:", ["20GP", "40GP", "40HC"])
    
    st.divider()
    st.markdown("🔗 **Share with Friends**")
    st.code("https://sudath-consol-expert.streamlit.app")
    
    st.divider()
    st.markdown("🤖 **Smart Support (AI)**")
    aq = st.text_input("Ask logistics...")
    if st.button("Ask AI") and aq:
        try:
            res = ai_model.generate_content(aq); st.info(res.text)
        except: st.error("AI Offline")
        
    if st.button("LOGOUT"):
        st.session_state.auth = False; st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown('<div class="main-header"><h1>🚢 SMART CONSOL PRO - Powered by Sudath</h1></div>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 590, "W": 235, "H": 239, "MAX_CBM": 33.0},
    "40GP": {"L": 1203, "W": 235, "H": 239, "MAX_CBM": 67.0},
    "40HC": {"L": 1203, "W": 235, "H": 269, "MAX_CBM": 76.0}
}
specs = CONTAINERS[c_type]

st.subheader(f"📊 {c_type} Cargo Entry")
# Fixed Dictionary Syntax (image_b5cda4 error fix)
df = st.data_editor(pd.DataFrame([{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE TIGHT-LOAD 3D PLAN & REPORT"):
    total_vol = (df['L'] * df['W'] * df['H'] * df['Qty']).sum() / 1000000
    
    if total_vol > specs['MAX_CBM']:
        st.error(f"❌ Capacity Exceeded! ({total_vol:.2f} CBM)")
    else:
        # Original Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{total_vol:.2f} CBM")
        m2.metric("Capacity", f"{specs['MAX_CBM']} CBM")
        m3.metric("Utilization", f"{(total_vol/specs['MAX_CBM'])*100:.1f}%")
        m4.metric("Total Weight", f"{df['Weight_kg'].sum()} kg")

        # --- 3D TIGHT PACKING LOGIC ---
        fig = go.Figure()
        colors = ['#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
        
        curr_x, curr_y, curr_z = 0, 0, 0
        max_h_row = 0
        
        for i, row in df.iterrows():
            l, w, h, qty = row['L'], row['W'], row['H'], int(row['Qty'])
            for q_idx in range(qty):
                if curr_y + w > specs['W']:
                    curr_y = 0; curr_x += l
                if curr_x + l > specs['L']:
                    curr_x = 0; curr_y = 0; curr_z += max_h_row; max_h_row = 0
                
                # 3D Box Construction
                fig.add_trace(go.Mesh3d(
                    x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                    y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                    z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                    color=colors[i % len(colors)], opacity=0.9, alphahull=0, name=row['Cargo'],
                    showlegend=(q_idx == 0) # Legend per cargo type
                ))
                curr_y += w
                max_h_row = max(max_h_row, h)

        # Correcting the 20GP/40GP Shape (image_b5ca3f fix)
        fig.update_layout(
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(x=specs['L']/100, y=specs['W']/100, z=specs['H']/100),
                xaxis=dict(title='Length (cm)', range=[0, specs['L']]),
                yaxis=dict(title='Width (cm)', range=[0, specs['W']]),
                zaxis=dict(title='Height (cm)', range=[0, specs['H']])
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # PDF Download (image_aa0b24 style)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16)
        pdf.text(50, 25, "SMART CONSOL LOADING REPORT")
        pdf.set_text_color(0,0,0); pdf.set_font("Arial", '', 12); pdf.ln(45)
        pdf.cell(0, 10, f"Summary: {total_vol:.2f} CBM | Weight: {df['Weight_kg'].sum()} kg", 0, 1)
        pdf.ln(10); pdf.cell(0, 10, "COLOR KEY / SHIPMENT IDENTIFICATION:", 0, 1)
        for i, row in df.iterrows():
            pdf.cell(0, 8, f"- {row['Cargo']}", 0, 1)

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DOWNLOAD FINAL REPORT (PDF)", data=pdf_bytes, file_name="Sudath_Consol_Report.pdf")
