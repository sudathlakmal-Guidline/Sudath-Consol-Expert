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
        <h3 style="color:#FFCC00;text-align:center;">Authorized Access Only - Logistics Intelligence Suite</h3>
        </div>
        """, unsafe_allow_html=True)

    # Updated Container Specs with exact Internal Dimensions (Length, Width, Height)
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265}
    }

    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose Service:", ["Standard Consolidation", "OOG Handling", "DG Compliance"])

    if app_mode == "Standard Consolidation":
        st.subheader("📦 Standard Container Loading Planner")
        st.info("💡 Note: Please enter the **Total Weight** for the entire quantity in the 'Weight_kg' column.")
        
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                try:
                    for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.dropna()

                    if not df.empty:
                        df['Total_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                        
                        total_cbm = df['Total_CBM'].sum()
                        total_kg = df['Weight_kg'].sum() # Treating input as Total Line Weight
                        
                        # Get max dimensions of a single unit to check fitment
                        max_L = df['Length_cm'].max()
                        max_W = df['Width_cm'].max()
                        max_H = df['Height_cm'].max()

                        st.divider()
                        c1, c2 = st.columns(2)
                        c1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                        c2.metric("Total Weight", f"{total_kg:,.2f} kg")

                        # --- SMART CONTAINER RECOMMENDATION ---
                        best_con = None
                        rejection_reasons = {}

                        for con, specs in container_specs.items():
                            reasons = []
                            # Dimension Check (Fitment)
                            if max_L > specs["L"]: reasons.append(f"Cargo Length ({max_L}cm) exceeds {con} limit ({specs['L']}cm)")
                            if max_W > specs["W"]: reasons.append(f"Cargo Width ({max_W}cm) exceeds {con} limit ({specs['W']}cm)")
                            if max_H > specs["H"]: reasons.append(f"Cargo Height ({max_H}cm) exceeds {con} limit ({specs['H']}cm)")
                            
                            # Capacity Check
                            if total_cbm > specs["max_cbm"]: reasons.append(f"Total Volume ({total_cbm:.2f} CBM) exceeds {con} limit ({specs['max_cbm']} CBM)")
                            if total_kg > specs["max_kg"]: reasons.append(f"Total Weight ({total_kg:,.2f} kg) exceeds {con} limit ({specs['max_kg']} kg)")

                            if not reasons:
                                best_con = con
                                break
                            else:
                                rejection_reasons[con] = reasons
                        
                        if best_con:
                            st.success(f"✅ Recommended Container: **{best_con}**")
                            bal_cbm = container_specs[best_con]["max_cbm"] - total_cbm
                            bal_kg = container_specs[best_con]["max_kg"] - total_kg
                            st.info(f"📊 **Remaining Space in {best_con}:** {bal_cbm:.2f} CBM | **Remaining Weight:** {bal_kg:,.2f} kg")
                        else:
                            st.warning("⚠️ High Load or Oversized Cargo! Single standard container limit exceeded.")

                        # --- WHY NOT 20GP Analysis ---
                        if best_con != "20GP" and "20GP" in rejection_reasons:
                            st.markdown("### 🔍 Why not 20GP?")
                            for r in rejection_reasons["20GP"]:
                                st.error(f"❌ {r}")
                            
                            # Suggestion to fit in 20GP
                            st.markdown("### ⚖️ Optimization for 20GP")
                            to_hold = []
                            for _, row in df.iterrows():
                                if row['Length_cm'] > 585 or row['Width_cm'] > 230 or row['Height_cm'] > 228:
                                    to_hold.append(f"{row['Cargo_Name']} (Oversized)")
                            
                            if to_hold:
                                st.warning(f"💡 To use a **20GP**, you MUST REMOVE these oversized shipments: **{', '.join(to_hold)}**")

                        st.write("### 📋 Loading Details")
                        st.dataframe(df)

                except Exception as e:
                    st.error("🚫 දත්ත ඇතුළත් කිරීමේදී වැරැද්දක් වී ඇත. කරුණාකර අංක පමණක් භාවිතා කරන්න.")
            else:
                st.info("💡 Please enter cargo details in the table.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
