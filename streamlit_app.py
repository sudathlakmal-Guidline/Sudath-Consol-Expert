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
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">3D Cargo Placement & Orientation Specialist</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("### 🛠️ CONFIGURATION")
    is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty (28,000kg)")
    
    # Container Specs
    hc_payload = 28000 if is_heavy_duty else 26000
    container_specs = {
        "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230},
        "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230},
        "40HC": {"max_cbm": 70.0, "max_kg": hc_payload, "L": 1200, "W": 230, "H": 265}
    }

    # Input Table with Rotation Option
    initial_df = pd.DataFrame(columns=[
        "Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"
    ])
    # Setting default rotation to False for safety
    df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_3d_v8")

    if st.button("Generate Advanced 3D Plan"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
            
            df['Total_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
            
            total_qty = df['Quantity'].sum()
            total_wgt = df['Weight_kg'].sum()
            total_cbm = df['Total_CBM'].sum()

            # Summary Results
            st.subheader("📋 Shipment Summary")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Qty", f"{int(total_qty)} Pcs")
            c2.metric("Total Weight", f"{total_wgt:,.0f} kg")
            c3.metric("Total Volume", f"{total_cbm:.2f} CBM")
            
            best_con = next((name for name, spec in container_specs.items() if total_cbm <= spec["max_cbm"] and total_wgt <= spec["max_kg"]), "None")
            c4.metric("Recommended", best_con)

            if best_con != "None":
                # Progress Bar
                max_vol = container_specs[best_con]["max_cbm"]
                fill_pct = min((total_cbm / max_vol) * 100, 100)
                st.write(f"**Container Fill:** {fill_pct:.1f}%")
                st.progress(fill_pct / 100)

                # 3D Placement Visualization (Using Scatter3d to show X, Y, Z center points)
                fig = go.Figure()

                # Draw Container Wireframe
                L_limit, W_limit, H_limit = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                
                # Adding cargo as 3D Boxes
                colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
                current_x = 0

                for i, row in df.iterrows():
                    # Simulation: Placing cargo along X-axis
                    # If Rotation is NOT allowed, we keep L, W, H as is.
                    # If Rotation IS allowed, an optimizer would swap them, here we show status.
                    rot_status = "🔄 Rotation OK" if row['Rotation_Allowed'] else "🚫 No Rotation"
                    
                    # Create 3D Box representation
                    fig.add_trace(go.Mesh3d(
                        x=[current_x, current_x, current_x+row['Length_cm'], current_x+row['Length_cm'], current_x, current_x, current_x+row['Length_cm'], current_x+row['Length_cm']],
                        y=[0, row['Width_cm'], row['Width_cm'], 0, 0, row['Width_cm'], row['Width_cm'], 0],
                        z=[0, 0, 0, 0, row['Height_cm'], row['Height_cm'], row['Height_cm'], row['Height_cm']],
                        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                        color=colors[i % len(colors)],
                        name=f"{row['Cargo_Name']} ({rot_status})",
                        opacity=0.6,
                        showlegend=True
                    ))
                    current_x += (row['Length_cm'] * 0.5) # Shift for next item visualization

                fig.update_layout(
                    title=f"3D Cargo Placement Map - {best_con} (X=Length, Y=Width, Z=Height)",
                    scene=dict(
                        xaxis=dict(title='X: Length (cm)', range=[0, L_limit]),
                        yaxis=dict(title='Y: Width (cm)', range=[0, W_limit]),
                        zaxis=dict(title='Z: Height (cm)', range=[0, H_limit]),
                        aspectmode='manual',
                        aspectratio=dict(x=2, y=0.5, z=0.5)
                    ),
                    margin=dict(l=0, r=0, b=0, t=40)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **X අක්ෂය:** දිග | **Y අක්ෂය:** පළල | **Z අක්ෂය:** උස")
            else:
                st.error("Cargo exceeds all container capacities!")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
