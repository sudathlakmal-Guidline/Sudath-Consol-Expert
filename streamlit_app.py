import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Set-up
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# 2. Advanced CSS for Highlighting & Headers
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; }
    .utilization-frame {
        border: 3px solid #004a99;
        padding: 20px;
        border-radius: 15px;
        background-color: #f0f7ff;
        margin: 15px 0px;
    }
    .stat-text { font-size: 18px; font-weight: bold; color: #002b5e; }
    </style>
    <div class="main-header">
        <h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1>
        <p>Strategic Freight Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)

# 3. Equipment Specs
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "🏗️ OOG Assessment", "☣️ IMDG Segregation"])
    st.divider()
    carrier_policy = st.selectbox("Carrier Principle:", ["Main Line Operator (MLO)", "NVOCC / Feeder"])

if app_mode == "📦 Consolidation Planner":
    st.markdown("### 1. MANIFEST DATA ENTRY")
    # Data structure from your current version
    init_data = [
        {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 10000, "Rotation": "NO"},
        {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 10000, "Rotation": "NO"},
        {"Cargo_Name": "3", "Length_cm": 60, "Width_cm": 40, "Height_cm": 20, "Quantity": 300, "Weight_kg": 6000, "Rotation": "YES"}
    ]
    df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", key="v20_sudath_final")

    if st.button("GENERATE ADVANCED LOADING PLAN", type="primary"):
        df = df.dropna()
        total_wgt = df['Weight_kg'].sum()
        total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
        
        # Container Recommendation
        best_con = "20GP" if total_wgt <= 26000 and total_cbm <= 31.5 else "40HC"
        util_pct = min((total_cbm / specs[best_con]["vol"]), 1.0)

        # 5. HIGHLIGHTED ANALYTICS FRAME (As requested)
        st.markdown("### 2. CONSOLIDATION ANALYTICS")
        st.markdown(f"""
            <div class="utilization-frame">
                <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
                    <div class="stat-text">Total Weight: {total_wgt:,.2f} kg</div>
                    <div class="stat-text">Total Volume: {total_cbm:.3f} CBM</div>
                    <div class="stat-text">Equipment: {best_con}</div>
                </div>
                <div style="font-weight: bold; margin-bottom: 5px; color: #004a99;">Space Utilization Percentage:</div>
            </div>
        """, unsafe_allow_html=True)
        st.progress(util_pct) # Percent bar highlighted inside frame
        
        st.success(f"✅ Calculation Complete for {best_con} loading.")

        # 6. 3D CUBE ENGINE & COLOR KEY
        st.markdown("### 3. ADVANCED 3D PLACEMENT & COLOR KEY")
        
        L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
        fig = go.Figure()
        colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']

        # Legend Grid
        st.write("📦 **Cargo Legend:**")
        legend_cols = st.columns(min(len(df), 6))
        
        curr_x, curr_y, curr_z = 0, 0, 0
        max_h_layer = 0
        
        # Container Frame Trace
        fig.add_trace(go.Scatter3d(
            x=[0, L_lim, L_lim, 0, 0, 0, L_lim, L_lim, 0, 0, L_lim, L_lim, L_lim, L_lim, 0, 0],
            y=[0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, W_lim, W_lim],
            z=[0, 0, 0, 0, 0, H_lim, H_lim, H_lim, H_lim, H_lim, H_lim, 0, 0, H_lim, H_lim, 0],
            mode='lines', line=dict(color='black', width=5), name='Container Frame'
        ))
