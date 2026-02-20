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

API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    pass

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .watermark { position: fixed; bottom: 10px; right: 10px; opacity: 0.2; font-size: 20px; color: gray; z-index: 1000; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. DATABASE LOGIC ---
def get_db_connection():
    return sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL', '2026-02-08')")
    conn.commit()
    conn.close()

init_db()

# --- 3. AUTH LOGIC (Register included) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with tab1:
        u = st.text_input("User ID / Email", key="login_email").strip().lower()
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("LOGIN", use_container_width=True):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.auth = True
                st.session_state.user_email = u
                st.rerun()
            else: st.error("Invalid Credentials.")
            conn.close()

    with tab2:
        reg_u = st.text_input("Enter Email", key="reg_email").strip().lower()
        reg_p = st.text_input("Set Password", type="password", key="reg_pass")
        if st.button("REGISTER NOW", use_container_width=True):
            if reg_u and reg_p:
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (reg_u, reg_p, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit(); conn.close()
                    st.success("Success! Please Login.")
                except: st.error("Email already exists.")
    st.stop()

# --- 4. MAIN INTERFACE ---
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
        if st.button("📊 VIEW USER REPORTS"):
            conn = get_db_connection()
            st.dataframe(pd.read_sql("SELECT * FROM users", conn))
            conn.close()
    
    st.divider()
    c_type = st.selectbox("Select Container:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    
    st.slider("Rate our App", 1, 5, 5)
    
    st.subheader("🤖 Smart Support")
    ai_msg = st.text_input("Ask AI...")
    if st.button("Ask AI") and ai_msg:
        try:
            # Fixing the AI logic for stability
            res = ai_model.generate_content(f"Logistics Expert: {ai_msg}")
            st.info(res.text)
        except: st.error("AI Busy.")

    if st.button("LOGOUT"):
        st.session_state.auth = False; st.rerun()

# --- CARGO ENTRY ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500, "Can_Rotate": False}]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{total_vol:.2f} CBM")
        m2.metric("Capacity", f"{specs['MAX_CBM']} CBM")
        m3.metric("Utilization", f"{(total_vol/specs['MAX_CBM'])*100:.1f}%")
        m4.metric("Total Weight", f"{clean_df['Weight_kg'].sum()} kg")

        # 3D Plot
        fig = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        shipment_colors = {}
        x, y, z = 0, 0, 0
        max_h, max_w = 0, 0

        for idx, row in clean_df.iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors[idx % len(colors)]
            shipment_colors[row['Cargo']] = clr
            for _ in range(int(row['Qty'])):
                if row['Can_Rotate'] and (x + l > specs['L']): l, w = w, l 
                if x + l > specs['L']: x = 0; y += max_w; max_w = 0
                if y + w > specs['W']: y = 0; z += max_h; max_h = 0
                if z + h <= specs['H']:
                    fig.add_trace(go.Mesh3d(x=[x,x,x+l,x+l,x,x,x+l,x+l], y=[y,y+w,y+w,y,y,y+w,y+w,y], z=[z,z,z,z,z+h,z+h,z+h,z+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo']))
                    x += l; max_h = max(max_h, h); max_w = max(max_w, w)

        fig.update_layout(scene=dict(aspectmode='data'), showlegend=True) # Added Legend
        st.plotly_chart(fig, use_container_width=True)

        # PDF Fix
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16); pdf.text(45, 22, "SMART CONSOL LOADING REPORT")
        pdf.set_font("Arial", 'I', 8); pdf.text(170, 35, "Powered by Sudath") # Added Branding
        
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 11); pdf.ln(45)
        pdf.cell(0, 10, f"Summary: {total_vol:.2f} CBM | Weight: {clean_df['Weight_kg'].sum()} kg", 0, 1)

        try:
            img_bytes = fig.to_image(format="png", width=800, height=450)
            pdf.image(io.BytesIO(img_bytes), x=10, y=pdf.get_y()+5, w=190)
        except: pass

        pdf_out = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_out).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Sudath_Consol_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD FINAL REPORT</a>', unsafe_allow_html=True)

st.divider()
st.info("📢 **Advertise Here!** Contact: sudath.lakmal@gmail.com")
st.markdown("<center>© 2026 SMART CONSOL PRO - Powered by Sudath</center>", unsafe_allow_html=True)
