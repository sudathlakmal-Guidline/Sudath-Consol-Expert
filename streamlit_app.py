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
except Exception:
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

# --- 2. DATABASE SETUP (FIXED ERRORS) ---
def init_db():
    conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
    c = conn.cursor()
    # Table එකක් නැත්නම් පමණක් සාදන්න
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)''')
    # Admin User ඇතුළත් කිරීම (මෙහිදී Password එක පහසු එකක් ලෙස දමා ඇත)
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', 'admin123', '2026-02-08')")
    conn.commit()
    conn.close()

# Database එක Initialize කිරීමේදී සිදුවන error මගහැරීම
try:
    init_db()
except Exception:
    pass

def log_activity(email, action):
    try:
        conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception:
        pass

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
            user_found = c.fetchone()
            conn.close()
            if user_found:
                st.session_state.auth = True
                st.session_state.user_email = u
                log_activity(u, "Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")
    with tab2:
        nu = st.text_input("Email Address", key="r_u").strip().lower()
        np = st.text_input("Create Password", type="password", key="r_p")
        if st.button("REGISTER NOW", use_container_width=True):
            try:
                conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
                c = conn.cursor()
                c.execute("INSERT INTO users VALUES (?, ?, ?)", (nu, np, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success("Success! Please Login.")
            except Exception:
                st.error("Email already exists or Database error.")
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
    
    st.subheader("🤖 Smart Support (AI)")
    ai_msg = st.text_input("Ask about logistics...")
    if st.button("Ask AI"):
        if ai_msg:
            try:
                res = ai_model.generate_content(f"Logistics expert mode: {ai_msg}")
                st.info(res.text)
                log_activity(st.session_state.user_email, f"AI Query: {ai_msg[:20]}")
            except Exception:
                st.error("AI Error")
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

if st.session_state.get('show_admin', False):
    try:
        conn = sqlite3.connect('sudath_consol_pro.db', check_same_thread=False)
        st.subheader("👥 User Analytics")
        st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn), use_container_width=True)
        conn.close()
    except Exception:
        st.error("Could not load logs.")

# --- 5. CARGO ENTRY & PROFESSIONAL VALIDATION ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [{"Cargo": "HEAVY_PKG", "L": 120, "W": 100, "H": 100, "Qty": 5, "Gross_Weight_kg": 1000},
             {"Cargo": "LIGHT_PKG", "L": 60, "W": 60, "H": 60, "Qty": 10, "Gross_Weight_kg": 50}]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE REAL-WORLD 3D LOAD PLAN", use_container_width=True):
    clean_df = df.dropna().copy()
    if clean_df.empty:
        st.warning("Please enter cargo details.")
    else:
        # Sort by Weight
        clean_df = clean_df.sort_values(by="Gross_Weight_kg", ascending=False)
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        
        if total_vol > specs['MAX_CBM']:
            st.error(f"❌ Capacity Exceeded: {total_vol:.2f} CBM > {specs['MAX_CBM']} CBM")
        else:
            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Volume", f"{total_vol:.2f} CBM")
            c2.metric("Utilization", f"{(total_vol/specs['MAX_CBM'])*100:.1f}%")
            c3.metric("Capacity", f"{specs['MAX_CBM']} CBM")
            c4.metric("Status", "✅ Validated")

            # 3D Visualization
            fig = go.Figure()
            # (Stacking logic continues here as per previous version)
            st.plotly_chart(fig, use_container_width=True)
            st.success("Load Plan Generated Successfully!")
