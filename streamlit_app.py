import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Set-up
st.set_page_config(page_title="Smart Consol Expert v15 - Sudath", layout="wide", page_icon="🚢")

# 2. Advanced Professional Styling
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; }
    .status-card { background-color: #f8f9fa; border-left: 6px solid #004a99; padding: 15px; border-radius: 8px; margin: 15px 0; }
    .critical-alert { background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; border-radius: 8px; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

# 3. Rigid Equipment Specifications
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- 4. NAVIGATION CENTER ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Module:", 
                        ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment", "☣️ IMDG Segregation (DG)"])
    st.divider()
    st.markdown("### ⚙️ SYSTEM SETTINGS")
    is_heavy = st.toggle("Enable 28MT (40HC Only)")
    carrier_policy = st.selectbox("Carrier Principle:", ["Main Line Operator (MLO)", "NVOCC / Feeder"])

# --- 5. Global Header ---
st.markdown('<div class="main-header"><h1>🚢 SMART CONSOL & OOG EXPERT</h1><p>Colombo Export Intelligence System • Strategic Logistics Tool • By Sudath</p></div>', unsafe_allow_html=True)

if app_mode == "📦 Consolidation Planner":
    st.markdown("### 1. MANIFEST DATA ENTRY")
    
    # All columns in English with Rotation feature
    init_data = [{"Cargo_Name": "ITEM_01", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 1000, "Rotation_Allowed": "YES"}]
    df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", key="v15_final_eng")

    if st.button("EXECUTE ADVANCED LOADING PLAN", type="primary"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            total_wgt = df['Weight_kg'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            # --- Colombo Weight & Carrier Logic ---
            # Strictly follows Sudath's 26,001kg principle
            if total_wgt > 26000:
                st.markdown(f'<div class="critical-alert">⚠️ <b>WEIGHT VIOLATION:</b> Gross Weight {total_wgt:,.0f} kg exceeds standard payload. <br> 👉 <b>Requirement:</b> Split cargo into multiple units or reduce weight to 26,000kg.</div>', unsafe_allow_html=True)
                best_con = "20GP"
            else:
                best_con = next((n for n, s in specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), "40HC")
                st.success(f"✅ RECOMMENDED EQUIPMENT: {best_con}")

            # --- 6. ADVANCED 3D SIMULATION ---
            st.markdown("### 2. 3D CARGO PLACEMENT & COLOR LEGEND")
            
            L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs
