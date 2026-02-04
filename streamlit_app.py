import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 1. පද්ධති සැකසුම්
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# Database එක අලුත් නම් වලින් හදනවා (KeyError එක නැති කරන්න)
USER_DB = "users_db.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["email", "password", "reg_date"]).to_csv(USER_DB, index=False)

def load_u(): return pd.read_csv(USER_DB)
def save_u(e, p):
    df = load_u()
    if str(e) in df['email'].values.astype(str): return False
    new_data = pd.DataFrame([[e, p, datetime.now().strftime('%Y-%m-%d')]], columns=["email", "password", "reg_date"])
    pd.concat([df, new_data], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# Professional Design
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. ආරක්ෂිත පිවිසුම
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with tab1:
        with st.form("l_form"):
            u_email = st.text_input("Email")
            u_pass = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER SYSTEM"):
                users = load_u()
                # මෙතන තමයි KeyError එක මම නිවැරදි කළේ
                match = users[users['email'] == u_email]
                if not match.empty and str(match.iloc[0]['password']) == u_pass:
                    st.session_state.auth, st.session_state.user = True, u_email
                    st.rerun()
                else: st.error("Login Failed! Please check email/password.")
    
    with tab2:
        with st.form("r_form"):
            n_email = st.text_input("New Business Email")
            n_pass = st.text_input("Create Password", type="password")
            if st.form_submit_button("REGISTER NOW"):
                if n_email and len(n_pass) > 3:
                    if save_u(n_email, n_pass): st.success("Account Created! Now go to LOGIN tab.")
                    else: st.error("User already exists!")

else:
    # 3. ප්‍රධාන පද්ධතිය
    st.markdown(f'<div class="main-header"><h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1><p>Active User: {st.session_state.user}</p></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()
    
    mod = st.sidebar.radio("CHOOSE:", ["📦 Consolidation Planner", "🏗️ OOG Check"])

    if mod == "📦 Consolidation Planner":
        data = st.data_editor(pd.DataFrame([{"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10}]), num_rows="dynamic")
        if st.button("GENERATE 3D PLAN"):
            c = data.dropna()
            fig = go.Figure()
            # Container Frame (20GP Standard)
            L, W, H = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L,L,0,0,0,L,L,0,0,L,L,L,L,0,0], y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], mode='lines', line=dict(color='black', width=4)))
            
            # Cargo Placing
            cx, cy, cz, mh = 0, 0, 0, 0
            for i, r in c.iterrows():
                l, w, h = r['L'], r['W'], r['H']
                for _ in range(int(r['Qty'])):
                    if cx + l > L: cx=0; cy+=w
                    if cy + w > W: cy=0; cz+=mh; mh=0
                    if cz + h <= H:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color="blue", opacity=0.7, alphahull=0))
                        cx+=l; mh=max(mh, h)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.subheader("🏗️ OOG ASSESSMENT")
        w_val = st.number_input("Width (cm)", 250)
        if st.button("CHECK"):
            if w_val > 230: st.error("OOG - Special Equipment Needed!")
            else: st.success("Standard Cargo Size")

st.markdown("<hr><center>SMART CONSOL PLANNER - BY SUDATH | v42.0</center>", unsafe_allow_html=True)
