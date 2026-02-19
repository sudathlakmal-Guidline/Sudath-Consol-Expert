import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIG & HIGH SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

# AI CONFIGURATION
API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
genai.configure(api_key=API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# CSS for Security and Branding
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QS1n {display: none !important;}
            [data-testid="stSidebarNav"] {display: none !important;}
            .watermark {
                position: fixed;
                bottom: 10px;
                right: 10px;
                opacity: 0.2;
                font-size: 20px;
                color: gray;
                z-index: 1000;
            }
            </style>
            <div class="watermark">Powered by Sudath</div>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('sudath_consol_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, reg_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs 
                 (email TEXT, action TEXT, timestamp TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES ('sudath.lakmal@gmail.com', '853602795@@@vSL', '2026-02-08')")
    conn.commit()
    conn.close()

init_db()

def log_activity(email, action):
    conn = sqlite3.connect('sudath_consol_pro.db')
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs VALUES (?, ?, ?)", 
              (email, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# --- 3. PERSISTENT AUTH LOGIC ---
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
    share_link = "https://sudath-consol-expert-tgbirizblcv4mfney8vvpz.streamlit.app/"
    st.code(share_link)
    
    st.subheader("⭐ Rate our App")
    rating = st.slider("How helpful is this?", 1, 5, 5)
    if st.button("Submit Rating"):
        st.toast(f"Thank you for rating us {rating} stars!")

    # --- LIVE AI CHATBOT SECTION ---
    st.divider()
    st.subheader("🤖 Smart Support (AI)")
    ai_msg = st.text_input("Ask about logistics...", placeholder="e.g. Max tare weight of 20GP")
    if st.button("Ask AI"):
        if ai_msg:
            with st.spinner("Expert is thinking..."):
                try:
                    response = ai_model.generate_content(f"You are a logistics expert. Answer this query: {ai_msg}")
                    st.info(response.text)
                    log_activity(st.session_state.user_email, f"AI Query: {ai_msg[:30]}")
                except Exception as e:
                    st.error(f"AI Connection Error: {e}")
        else:
            st.warning("Please enter a question.")

    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

# --- ADMIN PANEL ---
if st.session_state.get('show_admin', False):
    conn = sqlite3.connect('sudath_consol_pro.db')
    st.subheader("👥 User Analytics (Admin Only)")
    col1, col2 = st.columns(2)
    with col1: st.dataframe(pd.read_sql("SELECT email, reg_date FROM users", conn), use_container_width=True)
    with col2: st.dataframe(pd.read_sql("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn), use_container_width=True)
    conn.close()

# --- CARGO ENTRY ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Gross_Weight_kg": 500}]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        # Fixed Weight & CBM Calculation
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = clean_df['Gross_Weight_kg'].sum()
        
        invalid_cargo = []
        for idx, row in clean_df.iterrows():
            if row['L'] > specs['L'] or row['W'] > specs['W'] or row['H'] > specs['H']:
                invalid_cargo.append(f"{row['Cargo']} (Size Exceeded)")
        
        # STOP processing if capacity is exceeded
        if total_vol > specs['MAX_CBM']:
            invalid_cargo.append(f"Total CBM Limit ({total_vol:.2f} / {specs['MAX_CBM']})")

        if invalid_cargo:
            st.error(f"❌ Loading Rejected! {', '.join(invalid_cargo)}")
            log_activity(st.session_state.user_email, f"Rejected: {c_type} (Limit Exceeded)")
        else:
            util_pct = (total_vol / specs['MAX_CBM']) * 100
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Volume", f"{total_vol:.2f} CBM")
            m2.metric("Capacity", f"{specs['MAX_CBM']} CBM")
            m3.metric("Utilization", f"{util_pct:.1f}%")
            m4.metric("Total Weight", f"{total_weight:,.0f} kg")

            # 3D Visualization
            fig = go.Figure()
            colors_hex = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
            fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))
            
            cx, cy, cz, layer_h = 0, 0, 0, 0
            for idx, row in clean_df.reset_index().iterrows():
                l, w, h = row['L'], row['W'], row['H']
                clr = colors_hex[idx % len(colors_hex)]
                for _ in range(int(row['Qty'])):
                    if cx + l > L_max: cx = 0; cy += w
                    if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                    if cz + h <= H_max:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.7, alphahull=0, name=row['Cargo']))
                        cx += l
                        layer_h = max(layer_h, h)
            
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

            # PDF Generation
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20); pdf.text(45, 25, "SMART CONSOL LOADING REPORT")
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'I', 10); pdf.text(160, 35, "Powered by Sudath")
            pdf.set_font("Arial", 'B', 12); pdf.ln(45)
            pdf.cell(0, 10, f"Summary: {total_vol:.2f} CBM | Total Gross Weight: {total_weight} kg", 0, 1)
            
            pdf_output = pdf.output(dest='S').encode('latin-1')
            b64 = base64.b64encode(pdf_output).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Sudath_Consol_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD REPORT</a>', unsafe_allow_html=True)
            log_activity(st.session_state.user_email, f"Success: {c_type} Load Generated")

# --- ADVERTISING & CONTACT SECTION ---
st.divider()
col_ad, col_con = st.columns([2,1])
with col_ad:
    st.info("📢 **Advertise Your Business Here!** \n\n Promote your freight forwarding or shipping services to thousands of users worldwide. Contact us for ad placements.")
with col_con:
    st.markdown("### 📧 Contact Developer")
    st.write("For Advertisements & Custom Tools:")
    st.write("**sudath.lakmal@gmail.com**")

st.markdown("---")
st.markdown(f"<center>© 2026 SMART CONSOL PRO - Powered by Sudath | v2.6 FINAL SECURITY</center>", unsafe_allow_html=True)
