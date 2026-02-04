import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Set-up
st.set_page_config(page_title="Smart Consol Expert v16 - Sudath", layout="wide", page_icon="🚢")

# 2. Professional Styling
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; }
    .critical-alert { background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; border-radius: 8px; color: #856404; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Equipment Specifications
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- 4. NAVIGATION & SETTINGS ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment", "☣️ IMDG Segregation (DG)"])
    st.divider()
    carrier_policy = st.selectbox("Carrier Principle:", ["Main Line Operator (MLO)", "NVOCC / Feeder"])

st.markdown('<div class="main-header"><h1>🚢 SMART CONSOL & OOG EXPERT</h1><p>Colombo Export Intelligence System • By Sudath</p></div>', unsafe_allow_html=True)

if app_mode == "📦 Consolidation Planner":
    st.markdown("### 1. MANIFEST DATA ENTRY")
    
    # Pre-loading data from your latest screenshot
    init_data = [
        {"Cargo_Name": "1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 10000, "Rotation_Allowed": "NO"},
        {"Cargo_Name": "2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 10000, "Rotation_Allowed": "NO"},
        {"Cargo_Name": "3", "Length_cm": 60, "Width_cm": 40, "Height_cm": 20, "Quantity": 50, "Weight_kg": 6001, "Rotation_Allowed": "YES"}
    ]
    df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", key="v16_final")

    if st.button("EXECUTE ADVANCED LOADING PLAN", type="primary"):
        if not df.empty:
            # Data Cleaning to ensure 3D rendering works
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            total_wgt = df['Weight_kg'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            # Weight Restriction Logic
            if total_wgt > 26000:
                st.markdown(f'<div class="critical-alert">🚨 WEIGHT LIMIT EXCEEDED: {total_wgt:,.0f} kg. Please use 2x20GP or reduce weight.</div>', unsafe_allow_html=True)
                best_con = "20GP"
            else:
                best_con = next((n for n, s in specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), "40HC")
                st.success(f"✅ RECOMMENDED EQUIPMENT: {best_con}")

            # --- 5. RE-BUILT 3D ENGINE ---
            st.markdown("### 2. 3D CARGO PLACEMENT & COLOR LEGEND")
            L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
            fig = go.Figure()
            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']
            
            #
