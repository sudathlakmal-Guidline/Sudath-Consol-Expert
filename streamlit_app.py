import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. පද්ධති සැකසුම් (SYSTEM CONFIG)
# ==========================================
st.set_page_config(page_title="SMART CONSOL & IMO EXPERT - BY SUDATH", layout="wide")

# වෘත්තීය පෙනුම සඳහා CSS
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    .util-frame { border: 2px solid #004a99; padding: 20px; border-radius: 15px; background-color: #f8fbff; margin-bottom: 20px; }
    .metric-val { font-size: 24px; font-weight: bold; color: #004a99; }
    .dg-warning { background-color: #fff3f3; border-left: 5px solid #ff4b4b; padding: 15px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ආරක්ෂක පිවිසුම (LOGIN SYSTEM)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔒 Restricted Access</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email Address")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN TO SYSTEM", use_container_width=True):
                if email == "sudath@expert.com" and pwd == "admin123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Login Details!")

if not st.session_state.logged_in:
    login_screen()
else:
    # ==========================================
    # 3. ප්‍රධාන පද්ධතිය (MAIN INTERFACE)
    # ==========================================
    st.markdown("""
        <div class="main-header">
            <h1>🚢 SMART CONSOL & IMO EXPERT - BY SUDATH</h1>
            <p>Strategic Freight Intelligence System | v33.0 Final Master</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"### 👤 User: Admin Sudath")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        module = st.radio("SELECT OPERATIONAL MODULE:", 
                          ["📦 Consolidation Planner", "🏗️ OOG Assessment", "☣️ IMDG Segregation"])
        st.divider()
        st.info(f"System Date: {datetime.now().strftime('%Y-%m-%d')}")

    # CONTAINER SPECS
    SPECS = {
        "20GP": {"L": 585, "W": 230, "H": 230, "Cap": 31.5, "MaxKg": 26000},
        "40HC": {"L": 1200, "W": 230, "H": 265, "Cap": 70.0, "MaxKg": 28500}
    }

    # ==========================================
    # 4. CONSOLIDATION MODULE
    # ==========================================
    if module == "📦 Consolidation Planner":
        st.subheader("1. MANIFEST LOAD LIST ENTRY")
        init_df = pd.DataFrame([
            {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 1000},
            {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 500}
        ])
        input_df = st.data_editor(init_df, num_rows="dynamic", use_container_width=True, key="consol_v33")

        if st.button("RUN ADVANCED LOADING SIMULATION", type="primary", use_container_width=True):
            clean_df = input_df.dropna()
            total_cbm = ((clean_df['Length_cm'] * clean_df['Width_cm'] * clean_df['Height_cm'] * clean_df['Quantity']) / 1000000).sum()
            total_wgt = (clean_df['Weight_kg'] * clean_df['Quantity']).sum()
            
            best_eq = "20GP" if total_cbm <= 31.5 and total_wgt <= 26000 else "40HC"
            
            # ANALYTICS DISPLAY
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

            # 3D SIMULATION ENGINE
            st.subheader("3. 3D PLACEMENT VISUALIZATION")
            fig = go.Figure()
            L_max, W_max, H_max = SPECS[best_eq]["L"], SPECS[best_eq]["W"], SPECS[best_eq]["H"]
            
            # Container Frame [cite: image_6cdd75
