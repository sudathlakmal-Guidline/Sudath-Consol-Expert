import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Final Consol Planner - Sudath", layout="wide", page_icon="🚢")

# 2. Professional CSS Styling
st.markdown("""
    <style>
    .header-style { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; }
    .suggestion-card { background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; border-radius: 10px; margin: 10px 0; color: #856404; }
    .section-header { color: #002b5e; border-left: 6px solid #FFCC00; padding-left: 12px; margin: 20px 0px; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ස්ථාවර කන්ටේනර් දත්ත
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- 4. NAVIGATION CENTER (Sidebar) ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Operational Module:", ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment"])
    st.divider()
    is_heavy = st.toggle("Enable 40HC Heavy Duty (28MT)")

# --- 5. Main Header ---
st.markdown('<div class="header-style"><h1>🚢 SMART CONSOL & OOG PLANNER</h1><p>Strategic Freight Intelligence • By Sudath</p></div>', unsafe_allow_html=True)

if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>1. MANIFEST DATA INPUT</p>", unsafe_allow_html=True)
    
    # Rotation_Allowed තීරුව සහිත දත්ත වගුව
    init_df = pd.DataFrame([{"Cargo_Name": "Item 1", "Length_cm": 100, "Width_cm": 100, "Height_cm": 100, "Quantity": 1, "Weight_kg": 500, "Rotation_Allowed": "YES"}])
    df = st.data_editor(init_df, num_rows="dynamic", key="final_v12_sudath")

    if st.button("EXECUTE 3D PLANNING SIMULATION", type="primary"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            total_wgt = df['Weight_kg'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            # Weight & Suggestion Logic
            if total_wgt > 26000:
                st.markdown(f'<div class="suggestion-card">🚨 <b>බර වැඩියි ({total_wgt:,.0f}kg):</b> 20GP දෙකක් හෝ බර අඩු කිරීම අවශ්‍යයි.</div>', unsafe_allow_html=True)
                best_con = "20GP"
            else:
                best_con = next((n for n, s in specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), "40HC")
                st.success(f"✅ Recommended Equipment: {best_con}")

            # --- 6. ADVANCED 3D CHART WITH AUTO-PACKING ---
            st.markdown("<p class='section-header'>3. 3D CARGO PLACEMENT & COLOR KEY</p>", unsafe_allow_html=True)
            L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
            
            fig = go.Figure()
            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']
            
            # Container Wireframe
            fig.add_trace(go.Scatter3d(
                x=[0, L_lim, L_lim, 0, 0, 0, L_lim, L_lim, 0, 0, L_lim, L_lim, L_lim, L_lim, 0, 0],
                y=[0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, W_lim, W_lim],
                z=[0, 0, 0, 0, 0, H_lim, H_lim, H_lim, H_lim, H_lim, H_lim, 0, 0, H_lim, H_lim, 0],
                mode='lines', line=dict(color='#2c3e50', width=6), name='Frame'
            ))

            curr_x, curr_y, curr_z = 0, 0, 0
            max_h_in_row = 0

            for i, (idx, row) in enumerate(df.iterrows()):
                clr = colors[i % len(colors)]
                
                for q in range(int(row['Quantity'])):
                    # Packing Logic
                    if curr_x + row['Length_cm'] > L_lim:
                        curr_x = 0
                        curr_y += row['Width_cm']
                    if curr_y + row['Width_cm'] > W_lim:
                        curr_y = 0
                        curr_z += max_h_in_row
                        max_h_in_row = 0
                    
                    fig.add_trace(go.Mesh3d(
                        x=[curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm'], curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm']],
                        y=[curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y, curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y],
                        z=[curr_z, curr_z, curr_z, curr_z, curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm']],
                        color=clr, opacity=0.8, name=row['Cargo_Name']
                    ))
                    
                    curr_x += row['Length_cm']
                    max_h_in_row = max(max_h_in_row, row['Height_cm'])

            fig.update_layout(scene=dict(
                xaxis=dict(range=[0, L_lim]), yaxis=dict(range=[0, W_lim]), zaxis=dict(range=[0, H_lim]),
                aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)
            ), margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Planner v12.0 | By Sudath</p>", unsafe_allow_html=True)
