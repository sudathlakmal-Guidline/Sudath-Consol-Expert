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
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">3D Cargo Placement & Color-Coded Identification</p>
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
        st.subheader("📦 Standard Consolidation & 3D Visual Index")
        
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_consol_v12")

        if st.button("Generate 3D Loading Plan"):
            if not df.empty:
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
                df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
                
                total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
                total_wgt = df['Weight_kg'].sum()

                best_con = next((name for name, spec in container_specs.items() if total_cbm <= spec["max_cbm"] and total_wgt <= spec["max_kg"]), "None")

                if best_con != "None":
                    max_vol = container_specs[best_con]["max_cbm"]
                    fill_pct = min((total_cbm / max_vol) * 100, 100)
                    remaining_cbm = max_vol - total_cbm

                    # Space Analysis
                    st.write(f"### 📊 Container Utilization: {best_con}")
                    st.progress(fill_pct / 100)
                    st.write(f"**Filled:** `{fill_pct:.1f}%` | **Remaining:** `{remaining_cbm:.2f} CBM`")

                    # 3D Visualization
                    fig = go.Figure()
                    L_limit, W_limit, H_limit = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                    
                    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'yellow', 'brown']
                    curr_x, curr_y, curr_z = 0, 0, 0
                    
                    # Store data for the Legend
                    legend_data = []

                    for idx, row in df.iterrows():
                        color = colors[idx % len(colors)]
                        legend_data.append({"Cargo": row['Cargo_Name'], "Color": color})
                        
                        for n in range(int(row['Quantity'])):
                            dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                            
                            fig.add_trace(go.Mesh3d(
                                x=[curr_x, curr_x, curr_x+dx, curr_x+dx, curr_x, curr_x, curr_x+dx, curr_x+dx],
                                y=[curr_y, curr_y+dy, curr_y+dy, curr_y, curr_y, curr_y+dy, curr_y+dy, curr_y],
                                z=[curr_z, curr_z, curr_z, curr_z, curr_z+dz, curr_z+dz, curr_z+dz, curr_z+dz],
                                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                                color=color, opacity=0.6, name=f"{row['Cargo_Name']}"
                            ))
                            curr_x += dx
                            if curr_x + dx > L_limit:
                                curr_x = 0
                                curr_y += dy
                            if curr_y + dy > W_limit:
                                curr_y = 0
                                curr_z += dz

                    fig.update_layout(scene=dict(xaxis_title='Length (X)', yaxis_title='Width (Y)', zaxis_title='Height (Z)'))
                    st.plotly_chart(fig, use_container_width=True)

                    # --- 🎨 COLOR LEGEND (ඔබ ඉල්ලූ කොටස) ---
                    st.markdown("### 🏷️ Cargo Color Key")
                    cols = st.columns(len(legend_data))
                    for i, item in enumerate(legend_data):
                        with cols[i]:
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                    <div style="width: 20px; height: 20px; background-color: {item['Color']}; border: 1px solid black; margin-right: 10px;"></div>
                                    <span style="font-weight: bold;">{item['Cargo']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("❌ Does not fit in any standard container.")

    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG Check")
    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ IMO/DG Segregation")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
