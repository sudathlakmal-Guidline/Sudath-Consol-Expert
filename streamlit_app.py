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
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">Advanced 3D Multi-Unit Cargo Visualization & Full Summary</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Sidebar Navigation ---
    st.sidebar.markdown("### 🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio("Choose a Service:", ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"])
    st.sidebar.divider()
    is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty (28,000kg)")

    # Container Specs
    container_specs = {
        "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230},
        "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230},
        "40HC": {"max_cbm": 70.0, "max_kg": 28000 if is_heavy_duty else 26000, "L": 1200, "W": 230, "H": 265}
    }

    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Consolidation Summary & 3D Plan")
        
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_consol_v13")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
                df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
                
                # Calculations
                df['Item_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                total_cbm = df['Item_CBM'].sum()
                total_wgt = df['Weight_kg'].sum()
                total_qty = df['Quantity'].sum()

                # --- 1. TOTAL SUMMARY (ඔබ ඉල්ලූ කොටස) ---
                st.markdown("### 📊 Grand Totals")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Packages", f"{int(total_qty)} Pcs")
                c2.metric("Gross Weight", f"{total_wgt:,.2f} kg")
                c3.metric("Total Volume", f"{total_cbm:.2f} CBM")

                best_con = next((name for name, spec in container_specs.items() if total_cbm <= spec["max_cbm"] and total_wgt <= spec["max_kg"]), "None")

                if best_con != "None":
                    max_vol = container_specs[best_con]["max_cbm"]
                    fill_pct = min((total_cbm / max_vol) * 100, 100)
                    remaining_cbm = max_vol - total_cbm

                    # Utilization Bar
                    st.write(f"**Container Fill ({best_con}):** {fill_pct:.1f}% | **Remaining:** {remaining_cbm:.2f} CBM")
                    st.progress(fill_pct / 100)

                    # 3D Plotting
                    fig = go.Figure()
                    L_limit, W_limit, H_limit = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'yellow', 'magenta']
                    curr_x, curr_y, curr_z = 0, 0, 0
                    legend_list = []

                    for idx, row in df.iterrows():
                        color = colors[idx % len(colors)]
                        legend_list.append({"Cargo": row['Cargo_Name'], "Color": color, "Qty": row['Quantity'], "CBM": row['Item_CBM']})
                        
                        for n in range(int(row['Quantity'])):
                            dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                            fig.add_trace(go.Mesh3d(
                                x=[curr_x, curr_x, curr_x+dx, curr_x+dx, curr_x, curr_x, curr_x+dx, curr_x+dx],
                                y=[curr_y, curr_y+dy, curr_y+dy, curr_y, curr_y, curr_y+dy, curr_y+dy, curr_y],
                                z=[curr_z, curr_z, curr_z, curr_z, curr_z+dz, curr_z+dz, curr_z+dz, curr_z+dz],
                                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                                color=color, opacity=0.5, name=row['Cargo_Name']
                            ))
                            curr_x += dx
                            if curr_x + dx > L_limit:
                                curr_x, curr_y = 0, curr_y + dy
                            if curr_y + dy > W_limit:
                                curr_y, curr_z = 0, curr_z + dz

                    fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2, y=0.5, z=0.5)))
                    st.plotly_chart(fig, use_container_width=True)

                    # --- 2. CARGO COLOR KEY TABLE (පැහැදිලි ලැයිස්තුව) ---
                    st.markdown("### 🏷️ Cargo Color Identification")
                    legend_df = pd.DataFrame(legend_list)
                    
                    # HTML Table for better colors
                    html_code = "<table style='width:100%; border-collapse: collapse;'>"
                    html_code += "<tr style='background-color: #f2f2f2;'><th>Color</th><th>Cargo Name</th><th>Quantity</th><th>Volume (CBM)</th></tr>"
                    for item in legend_list:
                        html_code += f"<tr><td style='background-color:{item['Color']}; width: 50px;'></td><td><b>{item['Cargo']}</b></td><td>{int(item['Qty'])}</td><td>{item['CBM']:.2f}</td></tr>"
                    html_code += "</table>"
                    st.markdown(html_code, unsafe_allow_html=True)
                else:
                    st.error("❌ Does not fit! Weight or Volume limit exceeded.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
