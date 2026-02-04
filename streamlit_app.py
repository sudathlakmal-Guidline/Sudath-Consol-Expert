import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Sudath Logistics Expert", layout="wide", page_icon="🚢")

# --- IMDG Segregation Logic ---
seg_matrix = {
    "2.1": {"2.1": "X", "2.2": "0", "3": "2", "4.1": "0", "5.1": "2", "8": "1"},
    "3":   {"2.1": "2", "2.2": "0", "3": "X", "4.1": "0", "5.1": "2", "8": "0"},
    "5.1": {"2.1": "2", "2.2": "2", "3": "2", "4.1": "2", "5.1": "X", "8": "2"},
    "8":   {"2.1": "1", "2.2": "0", "3": "0", "4.1": "1", "5.1": "2", "8": "X"}
}

# --- Password System ---
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
    # Header Section
    st.markdown("""
        <div style="background-color:#002b5e;padding:20px;border-radius:10px;border-bottom: 5px solid #FFCC00;margin-bottom:20px;">
        <h1 style="color:white;text-align:center;margin:0;">🚢 SUDATH LOGISTICS INTELLIGENCE</h1>
        <p style="color:#FFCC00;text-align:center;font-size:18px;margin:5px;">Colombo Port Command Center - Global Export Expert</p>
        </div>
        """, unsafe_allow_html=True)

    # --- UPDATED NAVIGATION (No Dropdown) ---
    st.sidebar.markdown("### 🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio(
        "Choose an Option:",
        [
            "1. CONSOL PLANNING", 
            "2. OOG (Out of Gauge) CHECK", 
            "3. IMO/DG (Dangerous Goods) CHECK"
        ],
        index=0
    )
    st.sidebar.divider()

    # Container Specs
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265}
    }

    # --- 1. CONSOL PLANNING ---
    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation Planner")
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="consol_editor")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                try:
                    df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric, errors='coerce')
                    df = df.dropna()
                    
                    max_L, max_W, max_H = df['Length_cm'].max(), df['Width_cm'].max(), df['Height_cm'].max()
                    total_kg = df['Weight_kg'].sum()
                    total_cbm = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']).sum() / 1000000

                    st.divider()
                    best_con = next((c for c, s in container_specs.items() if max_L <= s["L"] and max_W <= s["W"] and max_H <= s["H"] and total_kg <= s["max_kg"] and total_cbm <= s["max_cbm"]), None)
                    
                    col_m1, col_m2 = st.columns(2)
                    col_m1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                    col_m2.metric("Total Weight", f"{total_kg:,.2f} kg")

                    if best_con:
                        st.success(f"✅ Recommended Container: **{best_con}**")
                    else:
                        st.warning("⚠️ Capacity Alert: Cargo exceeds standard single container limits. Check OOG or multi-load.")
                    st.dataframe(df, use_container_width=True)
                except:
                    st.error("Please ensure all dimension fields are numeric.")

    # --- 2. OOG CHECK ---
    elif app_mode == "2. OOG (Out of Gauge) CHECK":
        st.subheader("🏗️ OOG & Special Equipment Advisor")
        st.markdown("Enter dimensions to identify **Non-Containerized** cargo requirements.")
        
        with st.container(border=True):
            col_o1, col_o2, col_o3 = st.columns(3)
            o_l = col_o1.
