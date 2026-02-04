import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 1. INITIAL SETUP
st.set_page_config(page_title="SMART CONSOL - BY SUDATH", layout="wide")
USER_DB = "users_db.csv"
if not os.path.exists(USER_DB): pd.DataFrame(columns=["email", "password", "reg_date"]).to_csv(USER_DB, index=False)

def load_u(): return pd.read_csv(USER_DB)
def save_u(e, p):
    df = load_u()
    if e in df['email'].values.astype(str): return False
    pd.concat([df, pd.DataFrame([[e, p, datetime.now().strftime('%Y-%m-%d')]], columns=["email", "password", "reg_date"])], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# 2. LOGIN LOGIC
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    with t1:
        with st.form("l"):
            ue, up = st.text_input("Email"), st.text_input("Password", type="password")
            if st.form_submit_button("ENTER", use_container_width=True):
                users = load_u()
                match = users[users['email'] == ue]
                if not match.empty and str(match.iloc[0]['password']) == up:
                    reg = datetime.strptime(str(match.iloc[0]['reg_date']), '%Y-%m-%d')
                    exp = reg + timedelta(days=30)
                    if datetime.now() <= exp:
                        st.session_state.logged_in, st.session_state.u, st.session_state.x = True, ue, exp.strftime('%Y-%m-%d')
                        st.rerun()
                    else: st.error("Trial Expired!")
                else: st.error("Invalid Credentials!")
    with t2:
        with st.form("s"):
            ne, np = st.text_input("New Email"), st.text_input("New Password", type="password")
            if st.form_submit_button("SIGN UP"):
                if ne and len(np)>3:
                    if save_u(ne, np): st.success("Created! Please Login.")
                    else: st.error("Email Exists!")
else:
    # 3. MAIN DASHBOARD
    st.sidebar.markdown(f"### 👤 {st.session_state.u}\n**Trial Ends:** {st.session_state.x}")
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    
    mod = st.sidebar.radio("MODULE:", ["📦 Consolidation", "🏗️ OOG Check"])
    if mod == "📦 Consolidation":
        st.subheader("1. MANIFEST ENTRY")
        init = pd.DataFrame([{"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10, "Wgt": 1000, "Rot": "NO"}])
        df_in = st.data_editor(init, num_rows="dynamic", use_container_width=True)
        if st.button("RUN 3D SIMULATION", type="primary", use_container_width=True):
            clean = df_in.dropna()
            vol = ((clean['L']*clean['W']*clean['H']*clean['Qty'])/1000000).sum()
            wgt = (clean['Wgt']*clean['Qty']).sum()
            st.info(f"Summary: {vol:.2f} CBM | {wgt} kg")
            
            fig = go.Figure()
            # Container Frame
            L_m, W_m, H_m = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L_m,L_m,0,0,0,L_m,L_m,0,0,L_m,L_m,L_m,L_m,0,0], y=[0,0,W_m,W_m,0,0,0,W_m,W_m,0,0,0,W_m,W_m,W_m,W_m], z=[0,0,0,0,0,H_m,H_m,H_m,H_m,H_m,H_m,0,0,H_m,H_m,0], mode='lines', line=dict(color='black', width=3)))
            
            # Logic for Boxes
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
            cx, cy, cz, mh = 0, 0, 0, 0
            for i, r in clean.iterrows():
                clr = colors[i % 4]
                l, w, h = (r['W'],r['L'],r['H']) if r['Rot']=="YES" else (r['L'],r['W'],r['H'])
                for _ in range(int(r['Qty'])):
                    if cx + l > L_m: cx=0; cy+=w
                    if cy + w >
