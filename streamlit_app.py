import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Sudath Logistics Expert", layout="wide", page_icon="🚢")

# --- IMDG Segregation Matrix Logic ---
seg_matrix = {
    "2.1": {"2.1": "X", "2.2": "0", "3": "2", "4.1": "0", "5.1": "2", "8": "1"},
    "3":   {"2.1": "2", "2.2": "0", "3": "X", "4.1": "0", "5.1": "2", "8": "0"},
    "5.1": {"2.1": "2", "2.2": "2", "3": "2", "4.1": "2", "5.1": "X", "8": "2"},
    "8":   {"2.1": "1", "2.2": "0", "3": "0", "4.1": "1", "5.1": "2", "8": "X"}
}

# --- Password Authentication ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Admin Login Required</h2>", unsafe_allow_html=True)
        password = st.text_input("Please enter Admin Password:", type="password")
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
        <div style="background-color:#002b5e;padding:20px;border-radius:10px;border-bottom: 5px solid #FFCC00;">
        <h1 style="color:white;text-align:center;">🚢 SUDATH LOGISTICS INTELLIGENCE</h1>
        <h3 style="color:#FFCC00;text-align:center;">Colombo Port Global Export Command Center</h3>
        </div>
        """, unsafe_allow_html=True)

    # Container Specs
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265}
    }

    # Custom Navigation per user request
    st.sidebar.header("Select Service")
    app_mode = st.sidebar.radio(
        "Navigation:",
        ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CARGO CHECK"]
    )

    # --- MODULE 1: CONSOL PLANNING ---
    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation Planner")
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="consol_editor")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric, errors='coerce')
                df = df.dropna()
                
                max_L, max_W, max_H = df['Length_cm'].max(), df['Width_cm'].max(), df['Height_cm'].max()
                total_kg = df['Weight_kg'].sum()
                total_cbm = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']).sum() / 1000000

                st.divider()
                best_con = next((c for c, s in container_specs.items() if max_L <= s["L"] and max_W <= s["W"] and max_H <= s["H"] and total_kg <= s["max_kg"] and total_cbm <= s["max_cbm"]), None)
                
                if best_con:
                    st.success(f"✅ Recommended: **{best_con}**")
                    st.metric("Total Volume", f"{total_cbm:.2f} CBM")
                    st.metric("Total Weight", f"{total_kg:,.2f} kg")
                else:
                    st.warning("⚠️ High Volume/Weight: Requires multiple containers or OOG check.")
                st.dataframe(df)

    # --- MODULE 2: OOG CHECK ---
    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ Out of Gauge (OOG) & Special Equipment Advisor")
        st.info("Use this to check cargo exceeding standard container dimensions (1200x230x265cm).")
        
        o_l = st.number_input("Cargo Length (cm):", value=0)
        o_w = st.number_input("Cargo Width (cm):", value=0)
        o_h = st.number_input("Cargo Height (cm):", value=0)

        if st.button("Verify Equipment"):
            st.divider()
            if o_l > 1200:
                st.error("🚨 BREAK BULK / FLAT BED REQUIRED")
                st.write("Reason: Length exceeds 40ft Flat Rack limits.")
            elif o_w > 230 or o_h > 265:
                if o_h > 265 and o_w <= 230:
                    st.warning("🔝 OPEN TOP (OT) RECOMMENDED")
                else:
                    st.warning("🛡️ FLAT RACK (FR) RECOMMENDED")
            else:
                st.success("✅ This cargo can fit in a Standard 40HC container.")

    # --- MODULE 3: IMO/DG CARGO CHECK ---
    elif app_mode == "3. IMO/DG CARGO CHECK":
        st.subheader("☣️ IMDG Dangerous Goods & Colombo Customs Compliance")
        
        c1, c2 = st.columns(2)
        with c1:
            imdg_class = st.selectbox("IMDG Class:", ["2.1", "3", "4.1", "5.1", "6.1", "8", "9"])
            un_no = st.text_input("UN Number:")
            carrier = st.selectbox("Shipping Line:", ["Ma
