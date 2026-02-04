import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 1. SYSTEM CONFIGURATION
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

USER_DB = "users_db.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["email", "password", "reg_date"]).to_csv(USER_DB, index=False)

def load_u(): return pd.read_csv(USER_DB)
def save_u(e, p):
    df = load_u()
    if e in df['email'].values.astype(str): return False
    new_u = pd.DataFrame([[e, p, datetime.now().strftime('%Y-%m-%d')]], columns=["email", "password", "reg_date"])
    pd.concat([df, new_u], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# Styling
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    .legend-box { padding: 8px; border-radius: 5px; margin: 2px; color: white; font-weight: bold; text-align: center; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN & TRIAL SYSTEM
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    with t1:
        with st.form("login_form"):
            u_e = st.text_input("Email")
            u_p = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER SYSTEM", use_container_width=True):
                users = load_u()
                match = users[users['email'] == u_e]
                if not match.empty and str(match.iloc[0]['password']) == u_p:
                    reg = datetime.strptime(str(match.iloc[0]['reg_date']), '%Y-%m-%d')
                    exp = reg + timedelta(days=30)
                    if datetime.now() <= exp:
                        st.session_state.logged_in, st.session_state.user, st.session_state.exp = True, u_e, exp.strftime('%Y-%m-%d')
                        st.rerun()
                    else: st.error("Trial Expired! Contact Sudath.")
                else: st.error("Invalid Credentials")
    with t2:
        with st.form("signup_form"):
            n_e, n_p = st.text_input("Business Email"), st.text_input("Password", type="password")
            if st.form_submit_button("START 30-DAY FREE TRIAL"):
                if n_e and len(n_p) > 3:
                    if save_u(n_e, n_p): st.success("Account Created! Please Login.")
                    else: st.error("Email already exists!")

else:
    # 3. MAIN INTERFACE
    st.markdown(f'<div class="main-header"><h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1><p>User: {st.session_state.user} | Trial Ends: {st.session_state.exp}</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        mod = st.radio("SELECT:", ["📦 Consolidation", "🏗️ OOG Check"])

    if mod == "📦 Consolidation":
        init_df = pd.DataFrame([{"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10, "Wgt": 1000, "Rot": "NO"}])
        df_in = st.
