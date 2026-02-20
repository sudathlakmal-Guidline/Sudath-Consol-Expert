import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai
import io

# --- 1. CONFIG & HIGH SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

# AI Configuration
API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    pass

# CSS Branding & Security (ඔබේ මුල් CSS එකමයි)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .watermark { position: fixed; bottom: 10px; right: 10px; opacity: 0.2; font-size: 20px; color: gray; z-index: 1000; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    <div class="watermark">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. DATABASE SETUP (Multi-user Fix) ---
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
        c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", 
                  (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except: pass

# --- 3. AUTH LOGIC (Login & Register) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with tab1:
        u = st.text_input("User ID / Email", key="login_u").strip().lower()
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("LOGIN", use_container_width=True):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            user = c.fetchone()
            conn.close()
            if user:
                st.session_state.auth = True
                st.session_state.user_email = u
                log_activity(u, "Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials. Please check your details.")

    with tab2:
        new_u = st.text_input("Email Address", key="reg_u").strip().lower()
        new_p = st.text_input("Create Password", type="password", key="reg_p")
        if st.button("REGISTER NOW", use_container_width=True):
            if new_u and new_p:
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (new_u, new_p, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit(); conn.close()
                    st.success("Success! Please Login.")
                except: st.error("Email already exists.")
            else: st.warning("Please fill all fields.")
    st.stop()

# --- 4. MAIN INTERFACE ---
st.markdown(f'<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - Powered by Sudath</h1>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

# Sidebar Elements (Ads, Share, AI)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2343/2343894.png", width=100)
    st.success(f"✅ User: {st.session_state.user_email}")
    
    if st.session_state.user_email == "sudath.lakmal@gmail.com":
        st.subheader("👨‍✈️ ADMIN CONTROL")
        if st.button("📊 VIEW USER REPORTS"):
            st.session_state.show_admin = not st.session_state.get('show_admin', False)
    
    st.divider()
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    
    st.subheader("🔗 Share with Friends")
    st.code("https://sudath-consol-expert.streamlit.app/")
    
    st.info("📢 **Advertise Your Business!** \n\n Shipping & Logistics ads appear here.")
    
    st.subheader("🤖 Smart Support (AI)")
    ai_msg = st.text_input("Ask about logistics...")
    if st.button("Ask AI") and ai_msg:
        try:
            res = ai_model.generate_content(f"You are a logistics expert. Answer this: {ai_msg}")
            st.info(res.text)
            log_activity(st.session_state.user_email, f"AI Query: {ai_msg[:20]}")
        except: st.error("AI is busy.")

    if st.button("LOGOUT"):
        st.session_state.auth = False; st.rerun()

# Admin Display
if st.session_state.get('show_admin', False):
    conn = get_db_connection()
    st.subheader("👥 User Analytics")
    col1, col2 = st.columns(2)
    with col1: st.dataframe(pd.read_sql("SELECT email, reg_date FROM users", conn), use_container_width=True)
    with col2: st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn), use_container_width=True)
    conn.close()

# --- 5. CARGO ENTRY & 3D PLAN ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = clean_df['Weight_kg'].sum()
        
        # Validation Logic (ඔබේ මුල් අදහස)
        invalid_cargo = [row['Cargo'] for _, row in clean_df.iterrows() if row['L'] > specs['L'] or row['W'] > specs['W'] or row['H'] > specs['H']]
        
        if invalid_cargo:
            st.error(f"❌ Size Exceeded: {', '.join(invalid_cargo)}")
        elif total_vol > specs['MAX_CBM']:
            st.error(f"❌ Volume Exceeded: {total_vol:.2f} CBM (Limit: {specs['MAX_CBM']} CBM)")
        else:
            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Volume", f"{total_vol:.2f} CBM")
            m2.metric("Capacity", f"{specs['MAX_CBM']} CBM")
            m3.metric("Utilization", f"{(total_vol/specs['MAX_CBM'])*100:.1f}%")
            m4.metric("Total Weight", f"{total_weight} kg")

            # 3D Visual with Legend
            fig = go.Figure()
            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA']
            x, y, z = 0, 0, 0
            max_h, max_w = 0, 0
            for idx, row in clean_df.iterrows():
                l, w, h = row['L'], row['W'], row['H']
                clr = colors[idx % len(colors)]
                for _ in range(int(row['Qty'])):
                    if x + l > specs['L']: x = 0; y += max_w; max_w = 0
                    if y + w > specs['W']: y = 0; z += max_h; max_h = 0
                    if z + h <= specs['H']:
                        fig.add_trace(go.Mesh3d(x=[x,x,x+l,x+l,x,x,x+l,x+l], y=[y,y+w,y+w,y,y,y+w,y+w,y], z=[z,z,z,z,z+h,z+h,z+h,z+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo'], showlegend=True))
                        x += l; max_h = max(max_h, h); max_w = max(max_w, w)
            
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

            # PDF Report
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16); pdf.text(50, 22, "SMART CONSOL LOADING REPORT")
            pdf.set_font("Arial", 'I', 8); pdf.text(170, 35, "Powered by Sudath")
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12); pdf.ln(45)
            pdf.cell(0, 10, f"Total Volume: {total_vol:.2f} CBM | Weight: {total_weight} kg", 0, 1)
            
            pdf_out = pdf.output(dest='S').encode('latin-1')
            b64 = base64.b64encode(pdf_out).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Sudath_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD FINAL REPORT</a>', unsafe_allow_html=True)
            log_activity(st.session_state.user_email, "Report Generated")

# Footer
st.divider()
c1, c2 = st.columns([2,1])
with c1: st.info("📢 **Advertise Your Business!** Contact: sudath.lakmal@gmail.com")
with c2: st.markdown("### 📧 Support"); st.write("sudath.lakmal@gmail.com")
st.markdown("<center>© 2026 SMART CONSOL PRO - Powered by Sudath</center>", unsafe_allow_html=True)
