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

    # Container Specs
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "max_h": 2.38},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "max_h": 2.38},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "max_h": 2.69}
    }

    st.sidebar.header("Navigation")
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
                        df['Total_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                        df['Total_Weight'] = df['Weight_kg'] * df['Quantity']
                        
                        total_cbm = df['Total_CBM'].sum()
                        total_kg = df['Total_Weight'].sum()
                        max_item_h = df['Height_cm'].max() / 100

                        st.divider()
                        c1, c2 = st.columns(2)
                        c1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                        c2.metric("Total Weight", f"{total_kg:.2f} kg")

                        # --- LOGIC: Best Container Selection ---
                        best_con = None
                        for con, specs in container_specs.items():
                            if total_cbm <= specs["max_cbm"] and total_kg <= specs["max_kg"] and max_item_h <= specs["max_h"]:
                                best_con = con
                                break
                        
                        if best_con:
                            st.success(f"✅ Recommended Container: **{best_con}**")
                            # Balance Space Calculation
                            bal_cbm = container_specs[best_con]["max_cbm"] - total_cbm
                            bal_kg = container_specs[best_con]["max_kg"] - total_kg
                            st.info(f"📊 **Remaining Space in {best_con}:** {bal_cbm:.2f} CBM | **Remaining Weight:** {bal_kg:.2f} kg")
                        else:
                            st.warning("⚠️ High Load! This total cargo exceeds a single 40HC container capacity.")

                        # --- ANALYSIS: Why not 20GP? ---
                        if best_con != "20GP":
                            st.markdown("### 🔍 Why not 20GP?")
                            reasons = []
                            if total_cbm > container_specs["20GP"]["max_cbm"]:
                                reasons.append(f"Volume exceeds 20GP limit ({total_cbm:.2f} > 28 CBM)")
                            if total_kg > container_specs["20GP"]["max_kg"]:
                                reasons.append(f"Weight exceeds 20GP limit ({total_kg:.2f} > 26,000 kg)")
                            if max_item_h > container_specs["20GP"]["max_h"]:
                                reasons.append(f"Cargo height ({max_item_h}m) is too tall for 20GP (Max 2.38m)")

                            for r in reasons: st.error(f"❌ {r}")

                            # Decision Support: What to hold back for 20GP?
                            st.markdown("### ⚖️ Optimization for 20GP")
                            temp_df = df.sort_values(by='Total_CBM', ascending=False)
                            running_cbm = 0
                            to_load = []
                            to_hold = []
                            
                            for _, row in temp_df.iterrows():
                                if running_cbm + row['Total_CBM'] <= 28.0:
                                    running_cbm += row['Total_CBM']
                                    to_load.append(row['Cargo_Name'])
                                else:
                                    to_hold.append(row['Cargo_Name'])
                            
                            if to_hold:
                                st.warning(f"💡 To fit into a **20GP**, you should **HOLD** these shipments: {', '.join(to_hold)}")
                                st.write(f"✅ You can successfully load: {', '.join(to_load)}")

                        st.write("### 📋 Full Loading Details")
                        st.dataframe(df)

                except Exception as e:
                    st.error("🚫 Something went wrong. Check if all fields have valid numbers.")
            else:
                st.info("💡 Please enter cargo details in the table.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
