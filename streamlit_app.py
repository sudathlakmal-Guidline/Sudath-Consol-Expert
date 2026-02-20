import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai
import io

# --- 1. CONFIG & HIGH SECURITY (ඔබේ මුල්ම කේතය එලෙසමයි) ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Configuration Error: {e}")

# CSS for Security and Branding (මුල් කේතයම වේ)
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE SETUP (මුල් කේතයම වේ) ---
def init_db():
    conn = sqlite3.connect('sudath_consol_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, timestamp TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL', '2026-02-08')")
    conn.commit()
    conn.close()

init_db()

def log_activity(email, action):
    conn = sqlite3.connect('sudath_consol_pro.db')
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# --- 3. PERSISTENT AUTH LOGIC (ඔබේ මුල්ම Login එක) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    with tab1:
        u = st.text_input("User ID / Email", key="login_u").strip().lower()
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("LOGIN", use_container_width=True):
            conn = sqlite3.connect('sudath_consol_pro.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.auth = True
                st.session_state.user_email = u
                log_activity(u, "Login Successful")
                st.rerun()
            else: st.error("Invalid Credentials")
            conn.close()
    with tab2:
        new_u = st.text_input("Email Address", key="reg_u").strip().lower()
        new_p = st.text_input("Create Password", type="password", key="reg_p")
        if st.button("REGISTER NOW", use_container_width=True):
            if new_u and new_p:
                try:
                    conn = sqlite3.connect('sudath_consol_pro.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (new_u, new_p, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
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
    st.success(f"✅ User: {st.session_state.user_email}")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

# --- CARGO ENTRY WITH ROTATION OPTION ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [
    {"Cargo": "Heavy_Box", "L": 200, "W": 200, "H": 100, "Qty": 1, "Weight_kg": 5000, "Can_Rotate": False},
    {"Cargo": "Cartons", "L": 60, "W": 40, "H": 30, "Qty": 100, "Weight_kg": 3000, "Can_Rotate": True},
    {"Cargo": "Pallets", "L": 115, "W": 115, "H": 115, "Qty": 2, "Weight_kg": 2000, "Can_Rotate": False}
]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = clean_df['Weight_kg'].sum()
        
        # 3D Visualization Logic
        fig = go.Figure()
        colors_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
        
        # Container Outline
        fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))
        
        cx, cy, cz, layer_h = 0, 0, 0, 0
        shipment_colors = {} 

        for idx, row in clean_df.iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors_list[idx % len(colors_list)]
            shipment_colors[row['Cargo']] = clr
            
            for _ in range(int(row['Qty'])):
                if row['Can_Rotate'] and (cx + l > L_max): l, w = w, l 
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo'], showlegend=False))
                    cx += l
                    layer_h = max(layer_h, h)
        
        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF GENERATION WITH 3D IMAGE ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20); pdf.text(45, 25, "SMART CONSOL LOADING REPORT")
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 11); pdf.ln(45)
        pdf.cell(0, 10, f"Summary: {total_vol:.2f} CBM | Total Weight: {total_weight} kg", 0, 1)

        # COLOR KEY - සරල වගුව
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, "SHIPMENT COLOR KEY:", 0, 1)
        for name, color in shipment_colors.items():
            r, g, b = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            pdf.set_fill_color(r, g, b); pdf.rect(10, pdf.get_y()+1, 4, 4, 'F')
            pdf.set_x(16); pdf.set_font("Arial", '', 9); pdf.cell(0, 6, f"{name}", 0, 1)

        # 3D PHOTO CAPTURE SOLUTION
        try:
            img_bytes = fig.to_image(format="png", engine="kaleido")
            pdf.image(io.BytesIO(img_bytes), x=10, y=pdf.get_y()+5, w=180)
        except:
            pdf.set_text_color(255, 0, 0); pdf.ln(5); pdf.cell(0, 10, "Note: 3D Image processing failed. Please use app screenshot.", 0, 1)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Sudath_Consol_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD FINAL 3D REPORT</a>', unsafe_allow_html=True)

st.markdown(f"<br><center>© 2026 SMART CONSOL PRO - Powered by Sudath</center>", unsafe_allow_html=True)
