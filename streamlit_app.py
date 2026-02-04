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
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">Advanced 3D Multi-Unit Cargo Visualization</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("### 🛠️ CONFIGURATION")
    is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty (28,000kg)")
    
    container_specs = {
        "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230},
        "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230},
        "40HC": {"max_cbm": 70.0, "max_kg": 28000 if is_heavy_duty else 26000, "L": 1200, "W": 230, "H": 265}
    }

    # Data Input
    initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
    df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_3d_final")

    if st.button("Generate 3D Loading Plan"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
            
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
            total_wgt = df['Weight_kg'].sum()
            
            best_con = next((name for name, spec in container_specs.items() if total_cbm <= spec["max_cbm"] and total_wgt <= spec["max_kg"]), "None")

            if best_con != "None":
                st.subheader(f"📦 Loading Visualization: {best_con}")
                fig = go.Figure()
                
                # Container limits
                L_limit = container_specs[best_con]["L"]
                W_limit = container_specs[best_con]["W"]
                H_limit = container_specs[best_con]["H"]

                # Logic to show all units
                colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
                
                # Simple stacking algorithm for visualization
                curr_x, curr_y, curr_z = 0, 0, 0
                
                for idx, row in df.iterrows():
                    qty = int(row['Quantity'])
                    color = colors[idx % len(colors)]
                    
                    for n in range(qty):
                        # Calculate box corners
                        x, y, z = curr_x, curr_y, curr_z
                        dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                        
                        fig.add_trace(go.Mesh3d(
                            x=[x, x, x+dx, x+dx, x, x, x+dx, x+dx],
                            y=[y, y+dy, y+dy, y, y, y+dy, y+dy, y],
                            z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                            color=color, opacity=0.5
