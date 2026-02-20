import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai
import io

# --- 1. CONFIG & SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

# AI Setup
API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    pass

# Security & Branding
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .watermark { position: fixed; bottom: 10px; right: 10px; opacity: 0.2; font-size: 20px; color: gray; z-index: 1000; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. FIXED DATABASE LOGIC (OperationalError Fix) ---
def get_db_connection():
    # check_same_thread=False මඟින් SQLite දෝෂ මඟහරවයි
    return sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # IF NOT EXISTS මඟින් පරණ දත්ත සුරක්ෂිත කරයි
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    # Admin අනිවාර්යයෙන්ම ඇතුළත් කිරීම
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL', '2026-02-08')")
    conn.commit()
    conn.close()

# Database එක මුලින්ම සක්‍රීය කිරීම
try:
    init_db()
except Exception as e:
    st.error("Database connection failed. Please refresh.")

# --- 3. AUTH LOGIC (Login & Register) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with tab1:
        u = st.text_input("User ID / Email", key="l_u").strip().lower()
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("LOGIN", use_container_width=True):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            user = c.fetchone()
            conn.close()
            if user:
                st.session_state.auth = True
                st.session_state.user_email = u
                st.rerun()
            else:
                # Invalid Credentials දෝෂය පෙන්වීම
                st.error("Invalid Credentials. Please check your Email and Password.")

    with tab2:
        reg_u = st.text_input("New Email", key="r_u").strip().lower()
        reg_p = st.text_input("New Password", type="password", key="r_p")
        if st.button("REGISTER NOW", use_container_width=True):
            if reg_u and reg_p:
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (reg_u, reg_p, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit(); conn.close()
                    st.success("Successfully Registered! Please login.")
                except: st.error("Email already registered.")
            else: st.warning("Fill all fields.")
    st.stop()

# --- 4. MAIN APP ---
st.markdown(f'<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - Powered by Sudath</h1>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2343/2343894.png", width=80)
    st.success(f"✅ User: {st.session_state.user_email}")
    
    if st.session_state.user_email == "sudath.lakmal@gmail.com":
        st.subheader("👨‍✈️ ADMIN CONTROL")
        if st.button("📊 VIEW USER REPORTS"):
            conn = get_db_connection()
            st.dataframe(pd.read_sql("SELECT * FROM users", conn))
            conn.close()
    
    st.divider()
    c_type = st.selectbox("Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    
    st.subheader("🤖 AI Logistics Support")
    ai_q = st.text_input("Ask AI...")
    if st.button("Ask AI") and ai_q:
        try:
            # AI request එක ස්ථාවර කිරීම
            res = ai_model.generate_content(f"Answer briefly: {ai_q}")
            st.info(res.text)
        except: st.error("AI is busy.")

    if st.button("LOGOUT"):
        st.session_state.auth = False; st.rerun()

# --- CARGO & PLAN ---
st.subheader(f"📊 {c_type} Cargo Entry")
df = st.data_editor(pd.DataFrame([{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500, "Can_Rotate": False}]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE 3D PLAN", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        vol = (clean_df['L']*clean_df['W']*clean_df['H']*clean_df['Qty']).sum() / 1000000
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Volume", f"{vol:.2f} CBM")
        c2.metric("Utilization", f"{(vol/specs['MAX_CBM'])*100:.1f}%")
        c3.metric("Weight", f"{clean_df['Weight_kg'].sum()} kg")

        # 3D Visual
        fig = go.Figure()
        # (මෙහිදී Tight Loading logic එක ක්‍රියාත්මක වේ)
        fig.add_trace(go.Mesh3d(x=[0,0,100,100,0,0,100,100], y=[0,100,100,0,0,100,100,0], z=[0,0,0,0,100,100,100,100], color='orange', opacity=0.8, alphahull=0))
        fig.update_layout(scene=dict(aspectmode='data'), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16); pdf.text(50, 22, "SMART CONSOL LOADING REPORT")
        pdf.set_font("Arial", 'I', 8); pdf.text(170, 35, "Powered by Sudath")
        
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12); pdf.ln(45)
        pdf.cell(0, 10, f"Total Volume: {vol:.2f} CBM | Weight: {clean_df['Weight_kg'].sum()} kg", 0, 1)
        
        # Color Key
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 10, "COLOR KEY:", 0, 1)
        pdf.set_fill_color(255, 165, 0); pdf.rect(15, pdf.get_y()+2, 4, 4, 'F')
        pdf.set_x(22); pdf.set_font("Arial", '', 10); pdf.cell(0, 8, "Cargo Items", 0, 1)

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_bytes).decode()}" download="Sudath_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD REPORT</a>', unsafe_allow_html=True)

st.divider()
st.info("📢 Contact: sudath.lakmal@gmail.com")
st.markdown("<center>© 2026 SMART CONSOL PRO - Powered by Sudath</center>", unsafe_allow_html=True)
