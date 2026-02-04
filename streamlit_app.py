import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# Database Initialization
USER_DB = "users_db.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["email", "password", "reg_date"]).to_csv(USER_DB, index=False)

def load_users():
    return pd.read_csv(USER_DB)

def save_user(email, password):
    df = load_users()
    if email in df['email'].values.astype(str): return False
    new_u = pd.DataFrame([[email, password, datetime.now().strftime('%Y-%m-%d')]], columns=["email", "password", "reg_date"])
    pd.concat([df, new_u], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# Visual Styling
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .legend-box { padding: 8px; border-radius: 5px; margin: 2px; color: white; font-weight: bold; text-align: center; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION SYSTEM (30-DAY TRIAL)
# ==========================================
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER (30 DAYS FREE)"])
    
    with t1:
        with st.form("login"):
            u_e = st.text_input("Email")
            u_p = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER SYSTEM", use_container_width=True):
                users = load_users()
                match = users[users['email'] == u_e]
                if not match.empty and str(match.iloc[0]['password']) == u_p:
                    reg = datetime.strptime(str(match.iloc[0]['reg_date']), '%Y-%m-%d')
                    exp = reg + timedelta(days=30)
                    if datetime.now() <= exp:
                        st.session_state.logged_in, st.session_state.user, st.session_state.exp = True, u_e, exp.strftime('%Y-%m-%d')
                        st.rerun()
                    else: st.error(f"Trial Expired on {exp.strftime('%Y-%m-%d')}. Contact Admin Sudath.")
                else: st.error("Access Denied: Invalid Credentials")
    
    with t2:
        with st.form("signup"):
            n_e = st.text_input("Business Email")
            n_p = st.text_input("Create Password", type="password")
            if st.form_submit_button("START 30-DAY FREE TRIAL", use_container_width=True):
                if n_e and len(n_p) > 3:
                    if save_user(n_e, n_p): st.success("Account Created! Please Login.")
                    else: st.error("Email already registered!")
                else: st.warning("Please enter valid details.")

else:
    # ==========================================
    # 3. MAIN INTERFACE (AFTER LOGIN)
    # ==========================================
    st.markdown(f'<div class="main-header"><h1>🚢 SMART CONSOL PLANNER</h1><p>User: {st.session_state.user} | Trial Ends: {st.session_state.exp}</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        mod = st.radio("SELECT MODULE:", ["📦 Consolidation Planner", "🏗️ OOG Check"])

    if mod == "📦 Consolidation Planner":
        st.subheader("1. CARGO MANIFEST DATA")
        init = pd.DataFrame([{"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10, "Wgt": 1000, "Rot": "NO"}])
        df_in = st.data_editor(init, num_rows="dynamic", use_container_width=True)
        
        if st.button("GENERATE 3D LOADING PLAN", type="primary", use_container_width=True):
            clean = df_in.dropna()
            vol = ((clean['L']*clean['W']*clean['H']*clean['Qty'])/1000000).sum()
            wgt = (clean['Wgt']*clean['Qty']).sum()
            eq = "20GP" if vol <= 31 and wgt <= 26000 else "40HC"
            
            # Summary Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Weight", f"{wgt:,.0f} kg")
            c2.metric("Total Volume", f"{vol:.2f} CBM")
            c3.metric("Recommended EQ", eq)

            # 3D Visualization Engine
            fig = go.Figure()
            L_m = 585 if eq == "20GP" else 1200
            W_m, H_m = 230, 235
            
            # Draw Container Frame
            fig.add_trace(go.Scatter3d(
                x=[0,L_m,L_m,0,0,0,L_m,L_m,0,0,L_m,L_m,L_m,L_m,0,0], 
                y=[0,0,W_m,W_m,0,0,0,W_m,W_m,0,0,0,W_m,W_m,W_m,W_m], 
                z=[0,0,0,0,0,
