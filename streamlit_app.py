import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Config
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# 2. Enhanced CSS
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .utilization-frame { border: 2px solid #004a99; padding: 20px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 20px; }
    .stat-val { font-size: 20px; font-weight: bold; color: #002b5e; }
    </style>
    <div class="main-header">
        <h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1>
        <p>Strategic Freight Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)

# 3. Specs
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# 4. Data Entry
init_data = [
    {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 10000, "Rotation": "NO"},
    {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 10000, "Rotation": "NO"},
    {"Cargo_Name": "P3", "Length_cm": 60, "Width_cm": 40, "Height_cm": 20, "Quantity": 50, "Weight_kg": 600, "Rotation": "YES"}
]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic")

if st.button("GENERATE ADVANCED LOADING PLAN", type="primary"):
    df = df.dropna()
    total_wgt = df['Weight_kg'].sum()
    total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
    best_con = "20GP" if total_wgt <= 26000 and total_cbm <= 31.5 else "40HC"
    util_pct = min((total_cbm / specs[best_con]["vol"]), 1.0)

    # 5. HIGHLIGHTED ANALYTICS
    st.markdown(f"""
        <div class="utilization-frame">
            <div style="display: flex; justify-content: space-around;">
                <div>Total Weight<br><span class="stat-val">{total_wgt:,.0f} kg</span></div>
                <div>Total Volume<br><span class="stat-val">{total_cbm:.3f} CBM</span></div>
                <div>Equipment<br><span class="stat-val">{best_con}</span></div>
            </div>
            <p style="margin-top:15px; font-weight:bold; color:#004a99;">Space Utilization Percentage:</p>
        </div>
    """, unsafe_allow_html=True)
    st.progress(util_pct)

    # 6. STABLE 3D ENGINE
    st.markdown("### 3. ADVANCED 3D PLACEMENT & COLOR KEY")
    fig = go.Figure()
    L, W, H = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
    
    # Draw Container Wireframe
    fig.add_trace(go.Scatter3d(
        x=[0, L, L, 0, 0, 0, L, L, 0, 0, L, L, L, L, 0, 0],
        y=[0, 0, W, W, 0, 0, 0, W, W, 0, 0, 0, W, W, W, W],
        z=[0, 0, 0, 0, 0, H, H, H, H, H, H, 0, 0, H, H, 0],
        mode='lines', line=dict(color='black', width=4), name='Container'
    ))

    # Cube Placement Logic
    x, y, z, max_h = 0, 0, 0, 0
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    
    for i, row in df.iterrows():
        clr = colors[i % len(colors)]
        for _ in range(int(row['Quantity'])):
            if x + row['Length_cm'] > L: x = 0; y += row['Width_cm']
            if y + row['Width_cm'] > W: y = 0; z += max_h; max_h = 0
            
            if z + row['Height_cm'] <= H:
                fig.add_trace(go.Mesh3d(
                    x=[x, x, x+row['Length_cm'], x+row['Length_cm'], x, x, x+row['Length_cm'], x+row['Length_cm']],
                    y=[y, y+row['Width_cm'], y+row['Width_cm'], y, y, y+row['Width_cm'], y+row['Width_cm'], y],
                    z=[z, z, z, z, z+row['Height_cm'], z+row['Height_cm'], z+row['Height_cm'], z+row['Height_cm']],
                    color=clr, opacity=0.8, alphahull=0
                ))
                x += row['Length_cm']; max_h = max(max_h, row['Height_cm'])

    fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)
