import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    .util-frame { border: 2px solid #004a99; padding: 20px; border-radius: 15px; background-color: #f8fbff; margin-bottom: 20px; }
    .metric-val { font-size: 24px; font-weight: bold; color: #004a99; }
    .legend-box { padding: 10px; border-radius: 8px; margin: 5px; display: inline-block; color: white; font-weight: bold; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIN SYSTEM
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 Restricted Access</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="sudath@expert.com")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN TO SYSTEM", use_container_width=True):
                if email == "sudath@expert.com" and pwd == "admin123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Login Details!")
else:
    # ==========================================
    # 3. MAIN INTERFACE
    # ==========================================
    st.markdown("""
        <div class="main-header">
            <h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1>
            <p>Strategic Freight Intelligence System | v38.0 Final Master</p>
        </div>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👤 Admin: Sudath")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        module = st.radio("SELECT MISSION MODULE:", ["📦 Consolidation Planner", "🏗️ OOG Assessment", "☣️ IMDG Segregation"])
        st.divider()
        st.info(f"System Date: {datetime.now().strftime('%Y-%m-%d')}")

    SPECS = {
        "20GP": {"L": 585, "W": 230, "H": 230, "MaxKg": 26000},
        "40HC": {"L": 1200, "W": 230, "H": 265, "MaxKg": 28500}
    }

    if module == "📦 Consolidation Planner":
        st.subheader("1. MANIFEST DATA ENTRY")
        init_df = pd.DataFrame([
            {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 1000, "Rotation": "NO"},
            {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 500, "Rotation": "NO"}
        ])
        input_df = st.data_editor(init_df, num_rows="dynamic", use_container_width=True, key="consol_final")

        if st.button("GENERATE ADVANCED LOADING PLAN", type="primary", use_container_width=True):
            clean_df = input_df.dropna()
            total_cbm = ((clean_df['Length_cm'] * clean_df['Width_cm'] * clean_df['Height_cm'] * clean_df['Quantity']) / 1000000).sum()
            total_wgt = (clean_df['Weight_kg'] * clean_df['Quantity']).sum()
            best_eq = "20GP" if total_cbm <= 31.5 and total_wgt <= 26000 else "40HC"
            
            st.markdown("### 2. CONSOLIDATION ANALYTICS")
            st.markdown(f"""
                <div class="util-frame">
                    <div style="display: flex; justify-content: space-around; text-align: center;">
                        <div><p>Total Weight</p><p class="metric-val">{total_wgt:,.0f} kg</p></div>
                        <div><p>Total Volume</p><p class="metric-val">{total_cbm:.3f} CBM</p></div>
                        <div><p>Recommended Equipment</p><p class="metric-val">{best_eq}</p></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- 3D ENGINE ---
            st.subheader("3. 3D LOADING VISUALIZATION")
            fig = go.Figure()
            Lm, Wm, Hm = SPECS[best_eq]["L"], SPECS[best_eq]["W"], SPECS[best_eq]["H"]
            
            fig.add_trace(go.Scatter3d(
                x=[0, Lm, Lm, 0, 0, 0, Lm, Lm, 0, 0, Lm, Lm, Lm, Lm, 0, 0],
                y=[0, 0, Wm, Wm, 0, 0, 0, Wm, Wm, 0, 0, 0, Wm, Wm, Wm, Wm],
                z=[0, 0, 0, 0, 0, Hm, Hm, Hm, Hm, Hm, Hm, 0, 0, Hm, Hm, 0],
                mode='lines', line=dict(color='black', width=4), showlegend=False
            ))

            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#e377c2"]
            cargo_legend_data = []
            cx, cy, cz, mh = 0, 0, 0, 0

            for idx, r in clean_df.iterrows():
                current_color = colors[idx % len(colors)]
                cargo_legend_data.append({"name": r['Cargo_Name'], "color": current_color})
                l, w, h = (r['Width_cm'], r['Length_cm'], r['Height_cm']) if r['Rotation'] == "YES" else (r['Length_cm'], r['Width_cm'], r['Height_cm'])
                
                for _ in range(int(r['Quantity'])):
                    if cx + l > Lm: cx = 0; cy += w
                    if cy + w > Wm: cy = 0; cz += mh; mh = 0
                    if cz + h <= Hm:
                        fig.add_trace(go.Mesh3d(x=[cx, cx, cx+l, cx+l, cx, cx, cx+l, cx+l], y=[cy, cy+w, cy+w, cy, cy, cy+w, cy+w, cy], z=[cz, cz, cz, cz, cz+h, cz+h, cz+h, cz+h], color=current_color, opacity=0.75, alphahull=0))
                        cx += l; mh = max(mh, h)

            fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)), margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 🎨 CARGO COLOR IDENTIFICATION")
            legend_cols = st.columns(len(cargo_legend_data))
            for i, item in enumerate(cargo_legend_data):
                with legend_cols[i]:
                    st.markdown(f'<div class="legend-box" style="background-color: {item["color"]};">{item["name"]}</div>', unsafe_allow_html=True)

    elif module == "🏗️ OOG Assessment":
        st.subheader("🏗️ PROJECT CARGO ASSESSMENT")
        with st.form("oog"):
            c1, c2, c3 = st.columns(3)
            with c1: length = st.number_input("Length (cm)", value=1250)
            with c2: width = st.number_input("Width (cm)", value=255)
            with c3: height = st.number_input("Height (cm)", value=310)
            if st.form_submit_button("CHECK OOG"):
                if width > 230 or height > 260: st.error("🚨 OOG STATUS")
                else: st.success("✅ Standard Cargo")

    elif module == "☣️ IMDG Segregation":
        st.subheader("☣️ DG COMPLIANCE CHECK")
        st.info("Module Active. Ready for IMDG Segregation analysis.")

st.markdown("<br><hr><p style='text-align: center; color: gray;'>SMART CONSOL PLANNER - BY SUDATH | v38.0 Final Stable Version</p>", unsafe_allow_html=True)
