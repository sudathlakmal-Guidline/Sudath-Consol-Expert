import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except: pass

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .watermark { position: fixed; bottom: 10px; right: 10px; opacity: 0.2; font-size: 20px; color: gray; z-index: 1000; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. DATABASE SETUP ---
def get_db_connection():
    return sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL', '2026-02-08')")
    conn.commit()
    conn.close()

init_db()

def log_activity(email, action):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()
    except: pass

# --- 3. AUTH LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    with tab1:
        u = st.text_input("User ID / Email", key="l_u").strip().lower()
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("LOGIN", use_container_width=True):
            conn = get_db_connection(); c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.auth = True; st.session_state.user_email = u
                log_activity(u, "Login Successful"); st.rerun()
            else: st.error("Invalid Credentials")
            conn.close()
    with tab2:
        nu = st.text_input("Email", key="r_u").strip().lower()
        np = st.text_input("New Password", type="password", key="r_p")
        if st.button("REGISTER", use_container_width=True):
            try:
                conn = get_db_connection(); c = conn.cursor()
                c.execute("INSERT INTO users VALUES (?, ?, ?)", (nu, np, datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); conn.close(); st.success("Registered! Please Login.")
            except: st.error("Email already exists.")
    st.stop()

# --- 4. MAIN INTERFACE ---
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - Powered by Sudath</h1>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2343/2343894.png", width=80)
    st.success(f"User: {st.session_state.user_email}")
    if st.session_state.user_email == "sudath.lakmal@gmail.com":
        if st.button("📊 VIEW ADMIN REPORTS"): st.session_state.admin = not st.session_state.get('admin', False)
    
    st.divider()
    c_type = st.selectbox("Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    
    st.subheader("🤖 AI Support")
    q = st.text_input("Ask logistics...")
    if st.button("Ask AI") and q:
        try:
            res = ai_model.generate_content(q)
            st.info(res.text)
        except: st.error("AI Error")

    if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

if st.session_state.get('admin'):
    conn = get_db_connection()
    st.subheader("Admin Reports")
    st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn), use_container_width=True)
    conn.close()

# --- 5. CARGO ENTRY ---
st.subheader(f"📊 {c_type} Entry")
init_df = pd.DataFrame([{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}])
df = st.data_editor(init_df, num_rows="dynamic", use_container_width=True)

if st.button("GENERATE TIGHT-LOAD 3D PLAN & REPORT", use_container_width=True):
    clean = df.dropna()
    if not clean.empty:
        total_vol = (clean['L'] * clean['W'] * clean['H'] * clean['Qty']).sum() / 1000000
        total_w = clean['Weight_kg'].sum()
        
        if total_vol > specs['MAX_CBM']:
            st.error(f"Capacity Exceeded! ({total_vol:.2f} CBM)")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Volume", f"{total_vol:.2f} CBM")
            col2.metric("Utilization", f"{(total_vol/specs['MAX_CBM'])*100:.1f}%")
            col3.metric("Total Weight", f"{total_w} kg")

            # --- TIGHT LOADING LOGIC ---
            fig = go.Figure()
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            curr_x, curr_y, curr_z = 0, 0, 0
            layer_max_h = 0
            row_max_w = 0

            for i, row in clean.iterrows():
                l, w, h, qty = row['L'], row['W'], row['H'], int(row['Qty'])
                color = colors[i % len(colors)]
                
                # Add to legend only once per shipment type
                legend_added = False

                for _ in range(qty):
                    # Check if fits in current row (X)
                    if curr_x + l > specs['L']:
                        curr_x = 0
                        curr_y += row_max_w
                        row_max_w = 0
                    
                    # Check if fits in current layer (Y)
                    if curr_y + w > specs['W']:
                        curr_y = 0
                        curr_z += layer_max_h
                        layer_max_h = 0
                        
                    # 3D Box Generation
                    fig.add_trace(go.Mesh3d(
                        x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                        y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                        z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                        color=color, opacity=0.9, alphahull=0,
                        name=row['Cargo'],
                        showlegend=not legend_added
                    ))
                    legend_added = True
                    
                    curr_x += l
                    layer_max_h = max(layer_max_h, h)
                    row_max_w = max(row_max_w, w)

            fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Length', yaxis_title='Width', zaxis_title='Height'))
            st.plotly_chart(fig, use_container_width=True)

            # --- PDF REPORT ---
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16)
            pdf.text(55, 25, "SMART CONSOL LOADING REPORT")
            pdf.set_font("Arial", 'I', 8); pdf.text(175, 35, "Powered by Sudath")
            
            pdf.set_text_color(0,0,0); pdf.set_font("Arial", '', 12); pdf.ln(45)
            pdf.cell(0, 10, f"Summary: {total_vol:.2f} CBM | Total Weight: {total_w} kg", 0, 1)
            pdf.ln(5); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, "COLOR IDENTIFICATION:", 0, 1)
            
            for i, row in clean.iterrows():
                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 8, f"- {row['Cargo']} (Color Index {i+1})", 0, 1)

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 DOWNLOAD FINAL REPORT", data=pdf_bytes, file_name="Sudath_Consol_Report.pdf", use_container_width=True)
            log_activity(st.session_state.user_email, "Generated Report")

st.divider()
st.markdown("<center>© 2026 SMART CONSOL PRO - Powered by Sudath | sudath.lakmal@gmail.com</center>", unsafe_allow_html=True)
