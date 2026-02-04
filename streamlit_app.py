import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. System Config
st.set_page_config(page_title="Smart Consol Expert v17 - Sudath", layout="wide", page_icon="🚢")

# 2. Professional UI Styling (English Only)
st.markdown("""
    <style>
    .main-header { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; }
    .status-card { background-color: #f0f4f8; border-left: 6px solid #002b5e; padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. Equipment Specs
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- 4. NAVIGATION CENTER ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment", "☣️ IMDG Segregation (DG)"])
    st.divider()
    carrier_policy = st.selectbox("Carrier Principle:", ["Main Line Operator (MLO)", "NVOCC / Feeder"])

st.markdown('<div class="main-header"><h1>🚢 SMART CONSOL & OOG EXPERT</h1><p>Strategic Freight Intelligence System • By Sudath</p></div>', unsafe_allow_html=True)

if app_mode == "📦 Consolidation Planner":
    st.markdown("### 1. MANIFEST DATA ENTRY")
    
    # Pre-filling your exact data for a quick start
    init_data = [
        {"Cargo_Name": "1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 10000, "Rotation_Allowed": "NO"},
        {"Cargo_Name": "2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 10000, "Rotation_Allowed": "NO"},
        {"Cargo_Name": "3", "Length_cm": 60, "Width_cm": 40, "Height_cm": 20, "Quantity": 50, "Weight_kg": 600, "Rotation_Allowed": "YES"}
    ]
    df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", key="v17_stable")

    if st.button("EXECUTE ADVANCED LOADING PLAN", type="primary"):
        if not df.empty:
            # FIX: Force data to be numeric to ensure 3D works
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            total_wgt = df['Weight_kg'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            # Recommendation Logic
            best_con = "20GP" if total_wgt <= 26000 and total_cbm <= 31.5 else "40HC"
            st.success(f"✅ RECOMMENDED EQUIPMENT: {best_con}")

            # --- 5. 3D ENGINE (STABLE VERSION) ---
            st.markdown("### 2. 3D CARGO PLACEMENT & COLOR LEGEND")
            L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
            
            fig = go.Figure()
            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']
            
            # Draw Container Frame
            fig.add_trace(go.Scatter3d(
                x=[0, L_lim, L_lim, 0, 0, 0, L_lim, L_lim, 0, 0, L_lim, L_lim, L_lim, L_lim, 0, 0],
                y=[0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, W_lim, W_lim],
                z=[0, 0, 0, 0, 0, H_lim, H_lim, H_lim, H_lim, H_lim, H_lim, 0, 0, H_lim, H_lim, 0],
                mode='lines', line=dict(color='#2c3e50', width=5), name='Container'
            ))

            # Auto-stacking Logic
            curr_x, curr_y, curr_z = 0, 0, 0
            max_h_row = 0
            
            for i, (idx, row) in enumerate(df.iterrows()):
                clr = colors[i % len(colors)]
                for q in range(int(row['Quantity'])):
                    if curr_x + row['Length_cm'] > L_lim:
                        curr_x = 0; curr_y += row['Width_cm']
                    if curr_y + row['Width_cm'] > W_lim:
                        curr_y = 0; curr_z += max_h_row; max_h_row = 0
                    
                    if curr_z + row['Height_cm'] <= H_lim:
                        fig.add_trace(go.Mesh3d(
                            x=[curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm'], curr_x, curr_x, curr_x+row['Length_cm'], curr_x+row['Length_cm']],
                            y=[curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y, curr_y, curr_y+row['Width_cm'], curr_y+row['Width_cm'], curr_y],
                            z=[curr_z, curr_z, curr_z, curr_z, curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm'], curr_z+row['Height_cm']],
                            color=clr, opacity=0.8, name=f"Item {row['Cargo_Name']}"
                        ))
                        curr_x += row['Length_cm']
                        max_h_row = max(max_h_row, row['Height_cm'])

            fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2.5, y=1, z=1)), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Expert v17.0 | Colombo Edition | By Sudath</p>", unsafe_allow_html=True)
