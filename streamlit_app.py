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
            <p>Strategic Freight Intelligence System | v32.0 Premium Final</p>
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
        input_df = st.data_editor(init_df, num_rows="dynamic", use_container_width=True, key="consol_v32")

        if st.button("RUN ADVANCED LOADING SIMULATION", type="primary", use_container_width=True):
            clean_df = input_df.dropna()
            total_cbm = ((clean_df['Length_cm'] * clean_df['Width_cm'] * clean_df['Height_cm'] * clean_df['Quantity']) / 1000000).sum()
            total_wgt = (clean_df['Weight_kg'] * clean_df['Quantity']).sum()
            
            # ප්ලෑන් එක තෝරා ගැනීම
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
            
            # Container Outline
            fig.add_trace(go.Scatter3d(
                x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0],
                y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max],
                z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0],
                mode='lines', line=dict(color='black', width=4), name='Container'
            ))

            # Cargo Placement Logic
            curr_x, curr_y, curr_z, max_h_row = 0, 0, 0, 0
            for i, row in clean_df.iterrows():
                for _ in range(int(row['Quantity'])):
                    if curr_x + row['Length_cm'] > L_max:
                        curr_x = 0; curr_y += row['Width_cm']
                    if curr_y + row['Width_cm'] > W_max:
                        curr_y = 0; curr_z += max_h_row; max_h_row = 0
                    
                    if curr_z + row['Height_cm'] <= H_max:
                        fig.add_trace(go.Mesh3d(
                            x=[curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm'], curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm']],
                            y=[curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y, curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y],
                            z=[curr_z, curr_z, curr_z, curr_z, curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm']],
                            color=f"rgb({(i*50)%255}, 100, 200)", opacity=0.8, alphahull=0
                        ))
                        curr_x += row['Length_cm']
                        max_h_row = max(max_h_row, row['Height_cm'])

            fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # 5. OOG ASSESSMENT MODULE
    # ==========================================
    elif module == "🏗️ OOG Assessment":
        st.subheader("🏗️ PROJECT CARGO & OOG ANALYZER")
        with st.form("oog_calc"):
            c1, c2, c3 = st.columns(3)
            with c1: length = st.number_input("Length (cm)", value=1250)
            with c2: width = st.number_input("Width (cm)", value=255)
            with c3: height = st.number_input("Height (cm)", value=310)
            if st.form_submit_button("RUN ASSESSMENT"):
                if width > 230 or height > 260 or length > 1200:
                    st.error("🚨 CARGO STATUS: OUT-OF-GAUGE (OOG)")
                    st.info("Requirement: Flat Rack or Open Top equipment needed.")
                else:
                    st.success("✅ CARGO STATUS: IN-GAUGE (Standard Container)")

    # ==========================================
    # 6. IMDG MODULE
    # ==========================================
    elif module == "☣️ IMDG Segregation":
        st.subheader("☣️ IMDG DG SEGREGATION COMPLIANCE")
        imdg_data = {
