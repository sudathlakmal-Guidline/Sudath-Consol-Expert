import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime

# --- 1. DATABASE SETUP (Refresh කළත් දත්ත නොමැකීමට) ---
def init_db():
    conn = sqlite3.connect('sudath_consol_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs 
                 (email TEXT, action TEXT, timestamp TEXT)''')
    # Admin ගිණුම සෑදීම
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath', 'sudath@123', '2026-02-08')")
    conn.commit()
    conn.close()

init_db()

# --- 2. CONFIG ---
APP_VERSION = "v2.1 (PRO FINAL)"
st.set_page_config(page_title="SMART CONSOL PLANNER - SUDATH PRO", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

def log_activity(email, action):
    conn = sqlite3.connect('sudath_consol_final.db')
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", 
              (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# --- 3. LOGIN & REGISTER ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with tab1:
        u = st.text_input("User ID / Email", key="login_u").strip().lower()
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("LOGIN", use_container_width=True):
            conn = sqlite3.connect('sudath_consol_final.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.auth = True
                st.session_state.user_email = u
                log_activity(u, "Login")
                st.rerun()
            else: st.error("Invalid Credentials")
            conn.close()
            
    with tab2:
        new_u = st.text_input("Email Address", key="reg_u").strip().lower()
        new_p = st.text_input("Create Password", type="password", key="reg_p")
        if st.button("REGISTER NOW", use_container_width=True):
            if new_u and new_p:
                try:
                    conn = sqlite3.connect('sudath_consol_final.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (new_u, new_p, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    log_activity(new_u, "Registration")
                    st.success("Success! Please Login.")
                except: st.error("Email already registered!")
    st.stop()

# --- 4. MAIN APP ---
st.markdown(f'<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.success(f"✅ User: {st.session_state.user_email}")
    if st.session_state.user_email == "sudath":
        st.subheader("👨‍✈️ ADMIN CONTROL")
        if st.button("📊 VIEW USER REPORTS"):
            st.session_state.show_admin = not st.session_state.get('show_admin', False)
    
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

# --- ADMIN PANEL ---
if st.session_state.get('show_admin', False):
    st.divider()
    conn = sqlite3.connect('sudath_consol_final.db')
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("👥 Users")
        st.dataframe(pd.read_sql("SELECT email, reg_date FROM users", conn), use_container_width=True)
    with col_b:
        st.subheader("🕒 Recent Activity")
        st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 15", conn), use_container_width=True)
    conn.close()
    st.divider()

# --- CARGO ENTRY & LOGIC ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500, "Can_Rotate": True}]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        # මූලික ගණනය කිරීම්
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = (clean_df['Weight_kg'] * clean_df['Qty']).sum()
        util_pct = (total_vol / specs['MAX_CBM']) * 100

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{total_vol:.2f} CBM")
        m2.metric("Container Capacity", f"{specs['MAX_CBM']} CBM")
        m3.metric("Utilization", f"{util_pct:.1f}%")
        m4.metric("Total Weight", f"{total_weight:,.0f} kg")

        # --- 3D VISUALIZATION ---
        fig = go.Figure()
        L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
        fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))
        
        # සරල 3D පිරවුම් ලොජික් එක
        cx, cy, cz, layer_h = 0, 0, 0, 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for idx, row in clean_df.iterrows():
            l, w, h = row['L'], row['W'], row['H']
            for _ in range(int(row['Qty'])):
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=colors[idx % 4], opacity=0.7, alphahull=0))
                    cx += l
                    layer_h = max(layer_h, h)
        
        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF GENERATION ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20); pdf.text(50, 25, "SMART CONSOL REPORT")
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 12); pdf.ln(45)
        pdf.cell(0, 10, f"User: {st.session_state.user_email} | Date: {datetime.now()}", 0, 1)
        pdf.cell(0, 10, f"Utilization: {util_pct:.1f}% | Total Weight: {total_weight} kg", 0, 1)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Consol_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD PDF REPORT</a>', unsafe_allow_html=True)
        log_activity(st.session_state.user_email, f"Generated Report ({util_pct:.1f}%)")

st.markdown("---")
st.markdown(f"<center>© 2026 POWERED BY SUDATH PRO | {APP_VERSION}</center>", unsafe_allow_html=True)
