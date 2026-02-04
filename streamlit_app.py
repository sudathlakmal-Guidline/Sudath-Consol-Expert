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
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">Advanced 3D Multi-Unit Cargo & Space Optimization</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Sidebar Navigation ---
    st.sidebar.markdown("### 🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio(
        "Choose a Service:",
        ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"]
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("### ⚙️ SETTINGS")
    is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty (28,000kg)")

    # Container Specs
    container_specs = {
        "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230},
        "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230},
        "40HC": {"max_cbm": 70.0, "max_kg": 28000 if is_heavy_duty else 26000, "L": 1200, "W": 230, "H": 265}
    }

    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation & 3D Space Analysis")
        
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_consol_v10")

        if st.button("Generate 3D Loading Plan"):
            if not df.empty:
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
                df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
                
                total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
                total_wgt = df['Weight_kg'].sum()
                total_qty = df['Quantity'].sum()

                # Best Container Recommendation
                best_con = next((name for name, spec in container_specs.items() if total_cbm <= spec["max_cbm"] and total_wgt <= spec["max_kg"]), "None")

                if best_con != "None":
                    max_vol = container_specs[best_con]["max_cbm"]
                    fill_pct = min((total_cbm / max_vol) * 100, 100)
                    remaining_cbm = max_vol - total_cbm

                    # 1. Summary Metrics
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Quantity", f"{int(total_qty)} Pcs")
                    col2.metric("Total Weight", f"{total_wgt:,.0f} kg")
                    col3.metric("Total Volume", f"{total_cbm:.2f} CBM")

                    # 2. Space Utilization Progress Bar
                    st.write(f"### 📊 Container Utilization: {best_con}")
                    st.progress(fill_pct / 100)
                    
                    p1, p2 = st.columns(2)
                    p1.markdown(f"**Filled Space:** `{fill_pct:.1f}%`")
                    p2.markdown(f"**Remaining Capacity:** `{remaining_cbm:.2f} CBM`")
                    st.success(f"Recommended: {best_con}")

                    # 3. 3D Visualization
                    fig = go.Figure()
                    L_limit, W_limit, H_limit = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                    
                    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
                    curr_x, curr_y, curr_z = 0, 0, 0
                    
                    for idx, row in df.iterrows():
                        color = colors[idx % len(colors)]
                        for n in range(int(row['Quantity'])):
                            dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                            
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

                    fig.update_layout(
                        scene=dict(
                            xaxis=dict(title='Length (X)', range=[0, L_limit]),
                            yaxis=dict(title='Width (Y)', range=[0, W_limit]),
                            zaxis=dict(title='Height (Z)', range=[0, H_limit]),
                            aspectmode='manual', aspectratio=dict(x=2, y=0.5, z=0.5)
                        ),
                        margin=dict(l=0, r=0, b=0, t=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("❌ Exceeds Container Limits! Please split the shipment.")

    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG (Out of Gauge) Check")
    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ IMO/DG Segregation")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
