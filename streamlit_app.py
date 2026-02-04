import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Sudath Logistics Expert", layout="wide", page_icon="🚢")

# --- Password Authentication ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Admin Login Required</h2>", unsafe_allow_html=True)
        password = st.text_input("Password:", type="password")
        if st.button("Login"):
            if password == "sudath123":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password.")
        return False
    return True

if check_password():
    st.markdown("""
        <div style="background-color:#002b5e;padding:20px;border-radius:10px;border-bottom: 5px solid #FFCC00;margin-bottom:20px;">
        <h1 style="color:white;text-align:center;margin:0;">🚢 SUDATH LOGISTICS INTELLIGENCE</h1>
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">Advanced 3D Multi-Unit Cargo & DG Specialist</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Sidebar Navigation (මෙහිදී තමයි Menu එක තිබෙන්නේ) ---
    st.sidebar.markdown("### 🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio(
        "Choose a Service:",
        ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"]
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("### ⚙️ SETTINGS")
    is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty (28,000kg)")

    # Container Specs
    hc_payload = 28000 if is_heavy_duty else 26000
    container_specs = {
        "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230},
        "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230},
        "40HC": {"max_cbm": 70.0, "max_kg": hc_payload, "L": 1200, "W": 230, "H": 265}
    }

    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation & 3D Planner")
        
        # Input Table
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_consol_v9")

        if st.button("Generate 3D Loading Plan"):
            if not df.empty:
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
                df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
                
                total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
                total_wgt = df['Weight_kg'].sum()
                total_qty = df['Quantity'].sum()

                # Summary Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Qty", f"{int(total_qty)} Pcs")
                m2.metric("Total Weight", f"{total_wgt:,.0f} kg")
                m3.metric("Total Volume", f"{total_cbm:.2f} CBM")

                best_con = next((name for name, spec in container_specs.items() if total_cbm <= spec["max_cbm"] and total_wgt <= spec["max_kg"]), "None")

                if best_con != "None":
                    st.success(f"✅ Recommended: {best_con}")
                    # 3D Visualization Logic
                    fig = go.Figure()
                    L_limit, W_limit, H_limit = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                    
                    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
                    curr_x, curr_y, curr_z = 0, 0, 0
                    
                    for idx, row in df.iterrows():
                        color = colors[idx % len(colors)]
                        for n in range(int(row['Quantity'])):
                            dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                            
                            # Mesh3d for each box
                            fig.add_trace(go.Mesh3d(
                                x=[curr_x, curr_x, curr_x+dx, curr_x+dx, curr_x, curr_x, curr_x+dx, curr_x+dx],
                                y=[curr_y, curr_y+dy, curr_y+dy, curr_y, curr_y, curr_y+dy, curr_y+dy, curr_y],
                                z=[curr_z, curr_z, curr_z, curr_z, curr_z+dz, curr_z+dz, curr_z+dz, curr_z+dz],
                                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                                color=color, opacity=0.5, name=f"{row['Cargo_Name']} {n+1}"
                            ))
                            curr_x += dx
                            if curr_x + dx > L_limit:
                                curr_x = 0
                                curr_y += dy
                            if curr_y + dy > W_limit:
                                curr_y = 0
                                curr_z += dz

                    fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2, y=0.5, z=0.5)))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("❌ Exceeds Container Limits")

    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG (Out of Gauge) Cargo Checker")
        st.info("විශාල යන්ත්‍ර සූත්‍ර වැනි Flat Rack වල පටවන භාණ්ඩ මෙහිදී පරීක්ෂා කළ හැක.")
        # OOG logic එක මෙතැනට එයි...

    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ IMO/DG Dangerous Goods Segregation")
        st.warning("IMDG Code එකට අනුව භාණ්ඩ වෙන් කර තැබීම (Segregation) මෙහිදී පරීක්ෂා කෙරේ.")
        # DG logic එක මෙතැනට එයි...

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
