import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & ORIGINAL STYLE ---
st.set_page_config(page_title="SMART CONSOL PRO - Sudath", layout="wide")

# AI Setup
try:
    genai.configure(api_key="AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ")
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except: pass

# CSS to match your original UI (image_aa6cde.png)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton>button { background-color: #28a745; color: white; border-radius: 5px; }
    .main-header { background-color: #004a99; color: white; text-align: center; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
    </style>
    <div style="position: fixed; bottom: 5px; right: 5px; opacity: 0.3; font-size: 12px;">Powered by Sudath</div>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def get_db():
    conn = sqlite3.connect('sudath_final_v4.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)')
    conn.commit(); conn.close()

init_db()

# --- 3. SESSION STATE ---
if 'auth' not in st.session_state: st.session_state.auth = False

# Login Page (image_b4de43.jpg style)
if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    u = st.text_input("User ID / Email").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN", use_container_width=True):
        if u == "sudath.lakmal@gmail.com" and p == "853602795@@@vSL":
            st.session_state.auth = True; st.session_state.user = u; st.rerun()
        else: st.error("Invalid Credentials")
    st.stop()

# --- 4. SIDEBAR (Exactly like image_aa6cde.png) ---
with st.sidebar:
    st.markdown(f"✅ **User:** \n`{st.session_state.user}`", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 👨‍💼 ADMIN CONTROL")
    if st.button("📊 VIEW USER REPORTS"):
        conn = get_db()
        st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn))
        conn.close()
    
    st.divider()
    c_type = st.selectbox("Select Container Type:", ["20GP", "40GP", "40HC"])
    
    st.divider()
    st.markdown("🔗 **Share with Friends**")
    st.code("https://sudath-consol-expert.streamlit.app")
    
    st.divider()
    st.markdown("⭐ **Rate our App**")
    st.slider("How helpful is this?", 1, 5, 5)
    st.button("Submit Rating")
    
    st.divider()
    st.markdown("🤖 **Smart Support (AI)**")
    aq = st.text_input("Ask about cargo...")
    if st.button("Ask AI") and aq:
        try: res = ai_model.generate_content(aq); st.info(res.text)
        except: st.error("AI Busy")
        
    if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown('<div class="main-header"><h1>🚢 SMART CONSOL PRO - Powered by Sudath</h1></div>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 590, "W": 235, "H": 239, "MAX_CBM": 33.0},
    "40GP": {"L": 1203, "W": 235, "H": 239, "MAX_CBM": 67.0},
    "40HC": {"L": 1203, "W": 235, "H": 269, "MAX_CBM": 76.0}
}
specs = CONTAINERS[c_type]

st.subheader(f"📊 {c_type} Cargo Entry")
df = st.data_editor(pd.DataFrame([{"Cargo": "PKG_001", "L": 100, "W": 100, "H": 100, "Qty": 5, "Weight_kg":
