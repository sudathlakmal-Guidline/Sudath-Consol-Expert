import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & HIGH SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 

try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    pass

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
def init_db():
    conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL', '2026-02-08')")
    conn.commit()
    conn.close()

init_db()

def log_activity(email, action):
    conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

# --- 3. AUTH LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    with tab1:
        u = st.text_input("User ID / Email", key="l_u").strip().lower()
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("LOGIN", use_container_width=True):
            conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.auth = True; st.session_state.user_email = u
                log_activity(u, "Login Successful"); st.rerun()
            else: st.error("Invalid Credentials")
            conn.close()
    with tab2:
        nu = st.text_input("Email Address", key="r_u").strip().lower()
        np = st.text_input("Create Password", type="password", key="r_p")
        if st.button("REGISTER NOW", use_container_width=True):
            try:
                conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
                c = conn.cursor()
                c.execute("INSERT INTO users VALUES (?, ?, ?)", (nu, np, datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); conn.close(); st.success("Success! Please Login.")
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
    st.code("https://sudath-consol-expert-tgbirizblcv4mfney8vvpz.streamlit.app/")
    
    st.subheader("⭐ Rate our App")
    rating = st.slider("How helpful is this?", 1, 5, 5)
    if st.button("Submit Rating"): st.toast(f"Thank you for rating us {rating} stars!")

    st.divider()
    st.subheader("🤖 Smart Support (AI)")
    ai_msg = st.text_input("Ask about logistics...")
    if st.button("Ask AI"):
        if ai_msg:
            try:
                res = ai_model.generate_content(f"Logistics expert mode: {ai_msg}")
                st.info(res.text); log_activity(st.session_state.user_email, f"AI Query: {ai_msg[:20]}")
            except: st.error("AI Error")

    if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

if st.session_state.get('show_admin', False):
    conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
    st.subheader("👥 User Analytics")
    st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn), use_container_width=True)
    conn.close()

# --- 5. CARGO ENTRY & VALIDATION ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Gross_Weight_kg": 500}]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna()
    total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
    
    # ❌ Validation Check for Dimensions
    too_large = []
    for _, row in clean_df.iterrows():
        if row['L'] > specs['L'] or row['W'] > specs['W'] or row['H'] > specs['H']:
            too_large.append(f"{row['Cargo']} (Size Exceeded)")
    
    if too_large:
        st.error(f"❌ Cannot Load: {', '.join(too_large)}. Items are larger than {c_type} internal size!")
    elif total_vol > specs['MAX_CBM']:
        st.error(f"❌ Capacity Exceeded! Total: {total_vol:.2f} CBM (Max: {specs['MAX_CBM']})")
    else:
        # Tight Loading Logic
        fig = go.Figure()
        colors = ['#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
        curr_x, curr_y, curr_z, max_h_row = 0, 0, 0, 0
        
        for i, row in clean_df.iterrows():
            l, w, h, qty = row['L'], row['W'], row['H'], int(row['Qty'])
            for q in range(qty):
                if curr_y + w > specs['W']: curr_y = 0; curr_x += l
                if curr_x + l > specs['L']: curr_x = 0; curr_y = 0; curr_z += max_h_row; max_h_row = 0
                
                fig.add_trace(go.Mesh3d(
                    x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                    y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                    z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                    color=colors[i % len(colors)], opacity=0.9, alphahull=0, name=row['Cargo'], showlegend=(q==0)
                ))
                curr_y += w
                max_h_row = max(max_h_row, h)

        fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=specs['L']/100, y=specs['W']/100, z=specs['H']/100)))
        st.plotly_chart(fig, use_container_width=True)
        
        # Simple PDF summary
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Loading Report - {c_type}", 0, 1)
        pdf.set_font("Arial", '', 12); pdf.cell(0, 10, f"Total Volume: {total_vol:.2f} CBM", 0, 1)
        st.download_button("📥 DOWNLOAD REPORT", data=pdf.output(dest='S').encode('latin-1'), file_name="Report.pdf")
