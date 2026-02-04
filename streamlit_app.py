import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 1. SETUP
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")
DB = "users_db.csv"
if not os.path.exists(DB): pd.DataFrame(columns=["e","p","d"]).to_csv(DB, index=False)

def load(): return pd.read_csv(DB)
def save(e, p):
    df = load()
    if str(e) in df['e'].values.astype(str): return False
    pd.concat([df, pd.DataFrame([[e,p,datetime.now().strftime('%Y-%m-%d')]], columns=["e","p","d"])], ignore_index=True).to_csv(DB, index=False)
    return True

# 2. AUTH
if 'L' not in st.session_state: st.session_state.L = False
if not st.session_state.L:
    st.title("🚢 SMART CONSOL SYSTEM")
    t1, t2 = st.tabs(["LOGIN", "REGISTER"])
    with t1:
        with st.form("a"):
            e, p = st.text_input("Email"), st.text_input("Password", type="password")
            if st.form_submit_button("ENTER"):
                u = load()
                m = u[u['e'] == e]
                if not m.empty and str(m.iloc[0]['p']) == p:
                    st.session_state.L, st.session_state.u = True, e
                    st.rerun()
                else: st.error("Failed")
    with t2:
        with st.form("b"):
            ne, np = st.text_input("New Email"), st.text_input("New Password", type="password")
            if st.form_submit_button("SIGN UP"):
                if save(ne, np): st.success("Done!")
                else: st.error("Error")
else:
    # 3. APP
    st.markdown(f"### 🚢 SMART CONSOL PLANNER - BY SUDATH (User: {st.session_state.u})")
    if st.sidebar.button("LOGOUT"):
        st.session_state.L = False
        st.rerun()
    
    m = st.sidebar.radio("MODE", ["Consolidation", "OOG"])
    if m == "Consolidation":
        df = st.data_editor(pd.DataFrame([{"Cargo":"P1","L":115,"W":115,"H":115,"Qty":10}]), num_rows="dynamic")
        if st.button("RUN 3D"):
            c = df.dropna()
            fig = go.Figure()
            # Container
            L, W, H = 585, 230, 235
            fig.add_trace(go.Scatter3d(x=[0,L,L,0,0,0,L,L,0,0,L,L,L,L,0,0], y=[0,0,W,W,0,0,0,W,W,0,0,0,W,W,W,W], z=[0,0,0,0,0,H,H,H,H,H,H,0,0,H,H,0], mode='lines', line=dict(color='black')))
            
            # Simple Placement
            x, y, z, mh = 0, 0, 0, 0
            for i, r in c.iterrows():
                l, w, h = r['L'], r['W'], r['H']
                for _ in range(int(r['Qty'])):
                    if x + l > L: x=0; y+=w
                    if y + w > W: y=0; z+=mh; mh=0
                    if z + h <= H:
                        fig.add_trace(go.Mesh3d(x=[x,x,x+l,x+l,x,x,x+l,x+l], y=[y,y+w,y+w,y,y,y+w,y+w,y], z=[z,z,z,z,z+h,z+h,z+h,z+h], color="blue", opacity=0.6, alphahull=0))
                        x+=l; mh=max(mh, h)
            st.plotly_chart(fig)
    else:
        st.write("OOG Check Active")

st.markdown("<hr><center>SMART CONSOL PLANNER - BY SUDATH</center>", unsafe_allow_html=True)
