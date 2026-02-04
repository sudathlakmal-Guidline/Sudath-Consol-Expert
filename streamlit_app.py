import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 1. පද්ධති සැකසුම් (System Config)
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

USER_DB = "users_db.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["email", "password", "reg_date"]).to_csv(USER_DB, index=False)

def load_users(): return pd.read_csv(USER_DB)
def save_user(email, password):
    df = load_users()
    if email in df['email'].values.astype(str): return False
    new_u = pd.DataFrame([[email, password, datetime.now().strftime('%Y-%m-%d')]], columns=["email", "password", "reg_date"])
    pd.concat([df, new_u], ignore_index=True).to_csv(USER_DB, index=False)
    return True

# ලස්සන පෙනුම සඳහා CSS (Professional Styling)
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    .legend-box { padding: 10px; border-radius: 6px; margin: 4px; color: white; font-weight: bold; text-align: center; font-size: 13px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .stMetric { background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; }
    </style>
    """, unsafe_allow_html=True)

# 2. ආරක්ෂිත පිවිසුම් පද්ධතිය (Auth System)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    with t1:
        with st.form("login_form"):
            u_e = st.text_input("Email")
            u_p = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER SYSTEM", use_container_width=True):
                users = load_users()
                match = users[users['email'] == u_e]
                if not match.empty and str(match.iloc[0]['password']) == u_p:
                    st.session_state.logged_in, st.session_state.user = True, u_e
                    st.rerun()
                else: st.error("Invalid Credentials")
    with t2:
        with st.form("signup_form"):
            n_e, n_p = st.text_input("Business Email"), st.text_input("Create Password", type="password")
            if st.form_submit_button("START 30-DAY FREE TRIAL"):
                if n_e and len(n_p) > 3:
                    if save_user(n_e, n_p): st.success("Account Created! Please Login.")
                    else: st.error("Email already exists!")

else:
    # 3. ප්‍රධාන පද්ධතිය (Main App Interface)
    st.markdown(f'<div class="main-header"><h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1><p>Welcome, {st.session_state.user}</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        mod = st.radio("SELECT MODULE:", ["📦 Consolidation Planner", "🏗️ OOG Assessment"])

    if mod == "📦 Consolidation Planner":
        st.subheader("📊 Cargo Manifest Data")
        init_df = pd.DataFrame([{"Cargo": "P1", "L": 115, "W": 115, "H": 115, "Qty": 10, "Wgt": 1000, "Rot": "NO"}])
        df_in = st.data_editor(init_df, num_rows="dynamic", use_container_width=True)
        
        if st.button("GENERATE 3D LOADING PLAN", type="primary", use_container_width=True):
            clean = df_in.dropna()
            total_vol = ((clean['L']*clean['W']*clean['H']*clean['Qty'])/1000000).sum()
            total_wgt = (clean['Wgt']*clean['Qty']).sum()
            eq_type = "20GP" if total_vol <= 31 else "40HC"
            
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Weight", f"{total_wgt:,.0f} kg")
            c2.metric("Total Volume", f"{total_vol:.2f} CBM")
            c3.metric("Recommended EQ", eq_type)

            # 3D Visualization
            fig = go.Figure()
            L_limit = 585 if eq_type == "20GP" else 1200
            W_limit, H_limit = 230, 235
            
            # Container Wireframe
            fig.add_trace(go.Scatter3d(x=[0,L_limit,L_limit,0,0,0,L_limit,L_limit,0,0,L_limit,L_limit,L_limit,L_limit,0,0], y=[0,0,W_limit,W_limit,0,0,0,W_limit,W_limit,0,0,0,W_limit,W_limit,W_limit,W_limit], z=[0,0,0,0,0,H_limit,H_limit,H_limit,H_limit,H_limit,H_limit,0,0,H_limit,H_limit,0], mode='lines', line=dict(color='black', width=4), showlegend=False))

            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
            cx, cy, cz, max_h = 0, 0, 0, 0
            legend_items = []
            
            for idx, r in clean.iterrows():
                clr = colors[idx % len(colors)]
                legend_items.append({"n": r['Cargo'], "c": clr})
                l, w, h = (r['W'],r['L'],r['H']) if r['Rot']=="YES" else (r['L'],r['W'],r['H'])
                
                for _ in range(int(r['Qty'])):
                    if cx + l > L_limit: cx = 0; cy += w
                    if cy + w > W_limit: cy = 0; cz += max_h; max_h = 0
                    if cz + h <= H_limit:
                        fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.85, alphahull=0))
                        cx += l; max_h = max(max_h, h)
            
            fig.update_layout(scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # Color Legend
            st.write("### 🎨 Cargo Color Key")
            leg_cols = st.columns(len(legend_items))
            for i, item in enumerate(legend_items):
                leg_cols[i].markdown(f'<div class="legend-box" style="background-color:{item["c"]}">{item["n"]}</div>', unsafe_allow_html=True)

    elif mod == "🏗️ OOG Assessment":
        st.subheader("🚧 Out of Gauge Check")
        o_w = st.number_input("Cargo Width (cm)", value=250)
        if st.button("ANALYZE"):
            if o_w > 230: st.error("🚨 OOG DETECTED - Requires Special Equipment (Flat Rack/Open Top)")
            else: st.success("✅ STANDARD - Fits in General Purpose Container")

st.markdown("<br><hr><p style='text-align: center; color: gray;'>SMART CONSOL PLANNER - BY SUDATH | v41.0 PRO</p>", unsafe_allow_html=True)
