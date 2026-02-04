import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Config
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# 2. Professional CSS Header & Highlight Frame
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    .utilization-frame { border: 3px solid #004a99; padding: 20px; border-radius: 15px; background-color: #f0f7ff; margin: 15px 0px; }
    .stat-text { font-size: 19px; font-weight: bold; color: #002b5e; }
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

# 4. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "🏗️ OOG Assessment", "☣️ IMDG Segregation"])
    st.divider()
    carrier_policy = st.selectbox("Carrier Principle:", ["Main Line Operator (MLO)", "NVOCC / Feeder"])

if app_mode == "📦 Consolidation Planner":
    st.markdown("### 1. MANIFEST DATA ENTRY")
    init_data = [
        {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 10000},
        {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 10000}
    ]
    df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", key="v22_final")

    if st.button("GENERATE ADVANCED LOADING PLAN", type="primary"):
        df = df.dropna()
        total_wgt = df['Weight_kg'].sum()
        total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
        best_con = "20GP" if total_wgt <= 26000 and total_cbm <= 31.5 else "40HC"
        util_pct = min((total_cbm / specs[best_con]["vol"]), 1.0)

        # 5. CONSOLIDATION ANALYTICS (Highlighted)
        st.markdown("### 2. CONSOLIDATION ANALYTICS")
        st.markdown(f"""
            <div class="utilization-frame">
                <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
                    <div class="stat-text">Total Weight: {total_wgt:,.0f} kg</div>
                    <div class="stat-text">Total Volume: {total_cbm:.3f} CBM</div>
                    <div class="stat-text">Equipment: {best_con}</div>
                </div>
                <div style="font-weight: bold; margin-bottom: 5px; color: #004a99;">Space Utilization Percentage:</div>
            </div>
        """, unsafe_allow_html=True)
        st.progress(util_pct)

        # 6. 3D CHART ENGINE
        st.markdown("### 3. ADVANCED 3D PLACEMENT")
        fig = go.Figure()
        L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
        
        # Container Frame
        fig.add_trace(go.Scatter3d(
            x=[0, L_lim, L_lim, 0, 0, 0, L_lim, L_lim, 0, 0, L_lim, L_lim, L_lim, L_lim, 0, 0],
            y=[0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, W_lim, W_lim],
            z=[0, 0, 0, 0, 0, H_lim, H_lim, H_lim, H_lim, H_lim, H_lim, 0, 0, H_lim, H_lim, 0],
            mode='lines', line=dict(color='black', width=5), name='Frame'
        ))

        colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA']
        curr_x, curr_y, curr_z, max_h = 0, 0, 0, 0

        for i, row in df.iterrows():
            clr = colors[i % len(colors)]
            for q in range(int(row['Quantity'])):
                if curr_x + row['Length_cm'] > L_lim:
                    curr_x = 0; curr_y += row['Width_cm']
                if curr_y + row['Width_cm'] > W_lim:
                    curr_y = 0; curr_z += max_h; max_h = 0
                
                if curr_z + row['Height_cm'] <= H_lim:
                    fig.add_trace(go.Mesh3d(
                        x=[curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm'], curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm']],
                        y=[curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y, curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y],
                        z=[curr_z, curr_z, curr_z, curr_z, curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm']],
                        color=clr, opacity=0.8, alphahull=0
                    ))
                    curr_x += row['Length_cm']
                    max_h = max(max_h, row['Height_cm'])

        fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><hr><p style='text-align: center; color: gray;'>SMART CONSOL PLANNER - BY SUDATH | v22.0 Final</p>", unsafe_allow_html=True)
