import streamlit as st
import pandas as pd

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
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">Colombo Port Command Center - Cargo Loading Specialist</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.markdown("### 🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio(
        "Navigation:",
        ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"]
    )

    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation Planner")
        
        # Heavy Duty Mode Selection
        is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty Mode", help="Increase 40HC Payload to 28,000kg")

        # Container Specs with your specific weight limits
        hc_payload = 28000 if is_heavy_duty else 26000
        
        container_specs = {
            "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230, "door_h": 228},
            "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230, "door_h": 228},
            "40HC": {"max_cbm": 70.0, "max_kg": hc_payload, "L": 1200, "W": 230, "H": 265, "door_h": 258}
        }

        if st.button("🗑️ Clear All Data"):
            st.cache_data.clear()
            st.rerun()

        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_Per_Unit_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="consol_v4")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_Per_Unit_kg"])
                for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_Per_Unit_kg"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.dropna()

                if not df.empty:
                    max_L = df['Length_cm'].max()
                    max_W = df['Width_cm'].max()
                    max_H = df['Height_cm'].max()
                    
                    df['Total_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                    df['Total_Weight'] = df['Weight_Per_Unit_kg'] * df['Quantity']
                    
                    total_cbm = df['Total_CBM'].sum()
                    total_kg = df['Total_Weight'].sum()

                    st.divider()
                    
                    # Recommendation Logic
                    best_option = None
                    for name, spec in container_specs.items():
                        if (max_L <= spec["L"] and max_W <= spec["W"] and max_H <= spec["H"] and 
                            total_kg <= spec["max_kg"] and total_cbm <= spec["max_cbm"]):
                            best_option = name
                            break

                    col1, col2 = st.columns(2)
                    col1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                    col2.metric("Total Weight", f"{total_kg:,.2f} kg")

                    if best_option:
                        st.success(f"✅ Recommended: **{best_option}**")
                        if is_heavy_duty and best_option == "40HC":
                            st.info("Using Heavy Duty Payload (28,000 kg)")
                    else:
                        st.error("❌ Exceeds Standard Payload/Dimensions (26,000kg limit)")
                        if total_kg > 26000 and total_kg <= 28000:
                            st.warning("💡 Tip: Enable 'Heavy Duty Mode' if using a 40HC Heavy Duty container.")
                    
                    st.dataframe(df, use_container_width=True)

    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG Advisor")
    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ DG Advisor")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
