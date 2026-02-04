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

    # Sidebar Navigation (Clean & Simple)
    st.sidebar.markdown("### 🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio(
        "Navigation:",
        ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"]
    )
    
    # 40HC Heavy Duty Toggle (Only for special cases)
    is_heavy_duty = st.sidebar.toggle("Enable 40HC Heavy Duty (28,000kg)")

    # Container Specs - Weights are 26,000kg unless Heavy Duty 40HC is selected
    hc_payload = 28000 if is_heavy_duty else 26000
    container_specs = {
        "20GP": {"max_cbm": 31.5, "max_kg": 26000, "L": 585, "W": 230, "H": 230},
        "40GP": {"max_cbm": 58.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230},
        "40HC": {"max_cbm": 70.0, "max_kg": hc_payload, "L": 1200, "W": 230, "H": 265}
    }

    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation Planner")
        
        if st.button("🗑️ Reset All Data"):
            st.cache_data.clear()
            st.rerun()

        # Input Table (Simplified)
        # Note: Weight_kg is treated as the total weight for that specific shipment/line
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="sudath_editor_final")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                # Cleaning data
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
                for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.dropna()

                if not df.empty:
                    # Logic: Each row's Weight_kg is already the total for that line
                    # Each row's CBM = (L*W*H*Qty)/1,000,000
                    df['Total_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                    
                    # Totals for the entire shipment
                    grand_total_cbm = df['Total_CBM'].sum()
                    grand_total_weight = df['Weight_kg'].sum() # Auto SUM of all lines

                    st.divider()
                    
                    # Displaying Summary Metrics
                    m1, m2 = st.columns(2)
                    m1.metric("Total Volume (All Items)", f"{grand_total_cbm:.2f} CBM")
                    m2.metric("Total Weight (All Items)", f"{grand_total_weight:,.2f} kg")

                    # Checking for the best container match
                    max_L, max_W, max_H = df['Length_cm'].max(), df['Width_cm'].max(), df['Height_cm'].max()
                    
                    best_option = None
                    for name, spec in container_specs.items():
                        if (max_L <= spec["L"] and max_W <= spec["W"] and max_H <= spec["H"] and 
                            grand_total_weight <= spec["max_kg"] and grand_total_cbm <= spec["max_cbm"]):
                            best_option = name
                            break

                    if best_option:
                        st.success(f"✅ Recommended Container: **{best_option}**")
                    else:
                        st.error(f"❌ Exceeds Standard Capacity (Max: {hc_payload:,.0f}kg)")
                        if grand_total_weight > 26000 and not is_heavy_duty:
                            st.info("💡 Note: If you are using a 40HC Heavy Duty, enable the toggle in the sidebar.")
                    
                    st.dataframe(df, use_container_width=True)

    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG (Out of Gauge) Check")
        # Same OOG logic
    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ IMO/DG Cargo Check")
        # Same DG logic

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
