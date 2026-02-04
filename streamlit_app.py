import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sudath Consol Expert", layout="wide", page_icon="🔐")

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
        <div style="background-color:#003366;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">🚀 SUDATH CONSOL EXPERT</h1>
        <h3 style="color:#FFCC00;text-align:center;">Logistics Intelligence Suite</h3>
        </div>
        """, unsafe_allow_html=True)

    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "max_h": 2.38},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "max_h": 2.38},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "max_h": 2.69}
    }

    st.sidebar.header("Settings")
    weight_mode = st.sidebar.radio("Weight Input Mode:", ["Weight is Per Unit", "Weight is Total per Line"])
    app_mode = st.sidebar.selectbox("Choose Service:", ["Standard Consolidation", "OOG Handling", "DG Compliance"])

    if app_mode == "Standard Consolidation":
        st.subheader("📦 Standard Container Loading Planner")
        
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                try:
                    for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.dropna()

                    if not df.empty:
                        # CBM ගණනය කිරීම
                        df['Total_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                        
                        # Weight ගණනය කිරීම (මෙහිදී ඔබ තේරූ Mode එක අනුව ක්‍රියා කරයි)
                        if weight_mode == "Weight is Per Unit":
                            df['Total_Weight'] = df['Weight_kg'] * df['Quantity']
                        else:
                            df['Total_Weight'] = df['Weight_kg']
                        
                        total_cbm = df['Total_CBM'].sum()
                        total_kg = df['Total_Weight'].sum()
                        max_item_h = df['Height_cm'].max() / 100

                        st.divider()
                        c1, c2 = st.columns(2)
                        c1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                        c2.metric("Total Weight", f"{total_kg:,.2f} kg") # දහස්ස්ථාන වෙන් කර පෙන්වයි

                        # --- Container Logic ---
                        best_con = None
                        for con, specs in container_specs.items():
                            if total_cbm <= specs["max_cbm"] and total_kg <= specs["max_kg"] and max_item_h <= specs["max_h"]:
                                best_con = con
                                break
                        
                        if best_con:
                            st.success(f"✅ Recommended Container: **{best_con}**")
                            st.info(f"📊 Remaining Space: {specs['max_cbm']-total_cbm:.2f} CBM | Remaining Weight: {specs['max_kg']-total_kg:,.2f} kg")
                        else:
                            st.warning("⚠️ High Load! Capacity Exceeded.")

                        # Why not 20GP analysis
                        if best_con != "20GP":
                            st.markdown("### 🔍 Why not 20GP?")
                            if total_kg > 26000: st.error(f"❌ Weight exceeds 20GP limit ({total_kg:,.2f} > 26,000 kg)")
                            if total_cbm > 28: st.error(f"❌ Volume exceeds 20GP limit ({total_cbm:.2f} > 28 CBM)")

                        st.write("### 📋 Loading Details")
                        st.dataframe(df)

                except Exception:
                    st.error("🚫 Calculation failed. Please enter valid numbers.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
