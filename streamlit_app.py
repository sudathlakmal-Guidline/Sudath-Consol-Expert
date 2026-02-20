import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Sudath", layout="wide")

# AI Setup
try:
    genai.configure(api_key="AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ")
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except: pass

# CSS for Watermark & UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .watermark { position: fixed; bottom: 10px; right: 10px; opacity: 0.3; font-size: 18px; color: gray; z-index: 1000; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def get_db_connection():
    return sqlite3.connect('sudath_consol_v3.db', check_same_thread=False)

def init_db():
    conn = get_db_connection(); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL')")
    conn.commit(); conn.close()

init_db()

def log_act(email, action):
    conn = get_db_connection(); c = conn.cursor()
    c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

# --- 3. AUTHENTICATION ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    u = st.text_input("Email").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN", use_container_width=True):
        conn = get_db_connection(); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
        if c.fetchone():
            st.session_state.auth = True; st.session_state.user = u
            log_act(u, "Login Successful"); st.rerun()
        else: st.error("Invalid Credentials")
    st.stop()

# --- 4. MAIN APP ---
st.markdown(f'<h2 style="background-color:#004a99; color:white; padding:10px; border-radius:10px; text-align:center;">🚢 SMART CONSOL PRO - Powered by Sudath</h2>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 590, "W": 235, "H": 239, "MAX_CBM": 33.0},
    "40GP": {"L": 1203, "W": 235, "H": 239, "MAX_CBM": 67.0},
    "40HC": {"L": 1203, "W": 235, "H": 269, "MAX_CBM": 76.0}
}

with st.sidebar:
    st.write(f"Logged in: **{st.session_state.user}**")
    c_type = st.selectbox("Select Container:", list(CONTAINERS.keys()))
    st.divider()
    if st.session_state.user == "sudath.lakmal@gmail.com":
        if st.button("📊 ADMIN LOGS"):
            conn = get_db_connection()
            st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn))
            conn.close()
    
    st.subheader("🤖 AI Expert")
    prompt = st.text_input("Ask something...")
    if st.button("Ask AI") and prompt:
        try: res = ai_model.generate_content(prompt); st.info(res.text)
        except: st.error("AI Error")
    
    if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

# Cargo Input
st.subheader("📦 Cargo Details Entry")
df = st.data_editor(pd.DataFrame([{"Cargo": "PKG_001", "L": 100, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}]), num_rows="dynamic")

if st.button("GENERATE TIGHT-PACK 3D PLAN", use_container_width=True):
    specs = CONTAINERS[c_type]
    total_cbm = (df['L'] * df['W'] * df['H'] * df['Qty']).sum() / 1000000
    
    if total_cbm > specs['MAX_CBM']:
        st.error(f"⚠️ Volume Exceeded! Total: {total_cbm:.2f} CBM (Max: {specs['MAX_CBM']})")
    else:
        st.success(f"Utilization: {(total_cbm/specs['MAX_CBM'])*100:.1f}% | Total: {total_cbm:.2f} CBM")
        
        # --- TIGHT LOADING LOGIC (THE FIX) ---
        fig = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        curr_x, curr_y, curr_z = 0, 0, 0
        max_h_in_row = 0
        max_w_in_layer = 0
        
        for i, row in df.iterrows():
            l, w, h, qty = row['L'], row['W'], row['H'], int(row['Qty'])
            color = colors[i % len(colors)]
            legend_needed = True # Show each cargo type once in legend
            
            for _ in range(qty):
                # 1. Check if it fits in current Width (Y)
                if curr_y + w > specs['W']:
                    curr_y = 0
                    curr_x += l # Move to next Row in Length
                
                # 2. Check if it fits in current Length (X)
                if curr_x + l > specs['L']:
                    curr_x = 0
                    curr_y = 0
                    curr_z += max_h_in_row # Move to next Layer in Height
                    max_h_in_row = 0

                # Draw the box
                fig.add_trace(go.Mesh3d(
                    x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                    y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                    z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                    color=color, opacity=0.85, alphahull=0, name=row['Cargo'], showlegend=legend_needed
                ))
                legend_needed = False
                
                curr_y += w
                max_h_in_row = max(max_h_in_row, h)

        fig.update_layout(scene=dict(xaxis_title='Length', yaxis_title='Width', zaxis_title='Height'))
        st.plotly_chart(fig, use_container_width=True)

        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 30, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 14); pdf.text(60, 20, "SMART CONSOL LOADING REPORT")
        pdf.set_text_color(0,0,0); pdf.set_font("Arial", '', 10); pdf.ln(35)
        pdf.cell(0, 10, f"Container: {c_type} | Utilization: {(total_cbm/specs['MAX_CBM'])*100:.1f}%", 0, 1)
        pdf.cell(0, 10, f"Total CBM: {total_cbm:.2f} | Generated by: {st.session_state.user}", 0, 1)
        
        pdf_out = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DOWNLOAD PDF REPORT", data=pdf_out, file_name="Loading_Plan.pdf", use_container_width=True)
        log_act(st.session_state.user, f"Generated Plan for {total_cbm:.2f} CBM")

st.markdown("<br><center><p style='color:gray;'>© 2026 SMART CONSOL PRO - Powered by Sudath</p></center>", unsafe_allow_html=True)
