import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# 1. පද්ධති සැකසුම්
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

USER_DB = "users_db.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["email", "password", "reg_date"]).to_csv(USER_DB, index=False)

def load_u(): return pd.read_csv(USER_DB)
def save_u(e, p):
    df = load_u()
    if str(e) in df['email'].values.astype(str): return False
    new_u = pd.DataFrame([[e, p, datetime.now().strftime('%Y-%m-%d')]], columns=["email", "password", "reg_date"])
    pd.concat([df, new_u], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# Professional Design
st.markdown("""<style>.main-h { background: #004a99; padding: 15px; border-radius: 8px; color: white; text-align: center; }</style>""", unsafe_allow_html=True)

# 2. Login System
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    with t1:
        with st.form("l"):
            u = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER SYSTEM"):
                df = load_u()
                # KeyError එක මෙතනින් නිවැරදි කර ඇත
                match = df[df['email'] == u]
                if not match.empty and str(match.iloc[0]['password']) == p:
                    st.session_state.auth, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Login Failed")
    with t2:
        with st.form("r"):
            ne, np = st.text_input("New Email"), st.text_input("New Password", type="password")
            if st.form_submit_button("REGISTER"):
                if save_u(ne, np): st.success("Success! Now LOGIN.")
                else: st.error("Exists!")
else:
    # 3. Main Dashboard
    st.markdown(f'<div class="main-h"><h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1><p>User: {st.session_state.user}</p></div>', unsafe_allow_html=True)
    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()
    
    m = st.sidebar.radio("CHOOSE:", ["📦 3D Planner", "🏗️ OOG Check"])
    if m == "📦 3D Planner":
        df_in = st.data_editor(pd.DataFrame([{"Cargo":"P1","L":115,"W":115,"H":115,"Qty":10}]), num_rows="dynamic")
        if st.button("RUN 3D"):
            c = df_in.dropna()
            fig = go.Figure()
            L, W, H = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L,L,0,0,0,L,L,0,0,L,L,L,L,0,0], y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], mode='lines', line=dict(color='black')))
            x, y, z, mh = 0, 0, 0, 0
            for i, r in c.iterrows():
                l, w, h = r['L'], r['W'], r['H']
                for _ in range(int(r['Qty'])):
                    if x + l > L: x=0; y+=w
                    if y + w > W: y=0; z+=mh; mh=0
                    if z + h <= H:
                        fig.add_trace(go.Mesh3d(x=[x,x,x+l,x+l,x,x,x+l,x+l], y=[y,y+w,y+w,y,y,y+w,y+w,y], z=[z,z,z,z,z+h,z+h,z+h,z+h], color="blue", opacity=0.7, alphahull=0))
                        x+=l; mh=max(mh, h)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("OOG Assessment Tool Ready.")

st.markdown("<hr><center>SMART CONSOL PLANNER - BY SUDATH</center>", unsafe_allow_html=True)
