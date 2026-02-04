import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Config
st.set_page_config(page_title="Smart Consol Expert - Sudath", layout="wide")

# 2. Professional Header
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; }
    </style>
    <div class="main-header"><h1>🚢 SMART CONSOL EXPERT</h1><p>Strategic Package-Level 3D Simulation</p></div>
    """, unsafe_allow_html=True)

# 3. Equipment Specs
specs = {"20GP": {"L": 585, "W": 230, "H": 230}, "40HC": {"L": 1200, "W": 230, "H": 265}}

# Sidebar Settings
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "☣️ IMDG Segregation"])

if app_mode == "📦 Consolidation Planner":
    st.markdown("### 1. MANIFEST DATA ENTRY")
    init_data = [
        {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 4, "Weight_kg": 4000},
        {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 4, "Weight_kg": 4000}
    ]
    df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic")

    if st.button("EXECUTE 3D CUBE SIMULATION", type="primary"):
        # Logic to pick container
        total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
        best_con = "20GP" if total_cbm < 30 else "40HC"
        L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
        
        st.success(f"Equipment: {best_con} | Total Volume: {total_cbm:.3f} CBM")

        # --- 4. ADVANCED 3D CUBE ENGINE ---
        fig = go.Figure()
        colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA']
        
        # Draw Container Frame
        fig.add_trace(go.Scatter3d(
            x=[0, L_lim, L_lim, 0, 0, 0, L_lim, L_lim, 0, 0, L_lim, L_lim, L_lim, L_lim, 0, 0],
            y=[0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, W_lim, W_lim],
            z=[0, 0, 0, 0, 0, H_lim, H_lim, H_lim, H_lim, H_lim, H_lim, 0, 0, H_lim, H_lim, 0],
            mode='lines', line=dict(color='black', width=4), name='Container'
        ))

        # Packing logic as Cubes
        curr_x, curr_y, curr_z = 0, 0, 0
        max_h_row = 0

        for i, row in df.iterrows():
            clr = colors[i % len(colors)]
            for q in range(int(row['Quantity'])):
                # Simple grid placement for 3D view
                if curr_x + row['Length_cm'] > L_lim:
                    curr_x = 0; curr_y += row['Width_cm']
                if curr_y + row['Width_cm'] > W_lim:
                    curr_y = 0; curr_z += max_h_row; max_h_row = 0

                # Adding a Cube (Mesh3d)
                l, w, h = row['Length_cm'], row['Width_cm'], row['Height_cm']
                fig.add_trace(go.Mesh3d(
                    x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                    y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                    z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                    color=clr, opacity=0.9, alphahull=0, name=f"{row['Cargo_Name']}"
                ))
                curr_x += l
                max_h_row = max(max_h_row, h)

        fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)))
        st.plotly_chart(fig, use_container_width=True)
