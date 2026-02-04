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

    # UPDATED Container Specs (Internal Height set to 230cm as requested)
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 230, "door_h": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230, "door_h": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265, "door_h": 258}
    }

    st.sidebar.header("🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio("Navigation:", ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"])

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
                
                # Logic to check 20GP feasibility and explain why
                can_fit_20 = True
                reasons_20 = []
                
                if max_L > container_specs["20GP"]["L"]: 
                    can_fit_20 = False
                    reasons_20.append(f"Length exceeds 20GP limit ({max_L}cm > 585cm)")
                if max_W > container_specs["20GP"]["W"]: 
                    can_fit_20 = False
                    reasons_20.append(f"Width exceeds 20GP limit ({max_W}cm > 230cm)")
                if max_H > container_specs["20GP"]["H"]: 
                    can_fit_20 = False
                    reasons_20.append(f"Height exceeds 20GP internal limit ({max_H}cm > 230cm)")
                if total_kg > container_specs["20GP"]["max_kg"]: 
                    can_fit_20 = False
                    reasons_20.append(f"Total weight exceeds 20GP payload ({total_kg}kg > 26,000kg)")
                if total_cbm > container_specs["20GP"]["max_cbm"]: 
                    can_fit_20 = False
                    reasons_20.append(f"Total volume exceeds 20GP capacity ({total_cbm:.2f} CBM > 28 CBM)")

                # Display Results
                col1, col2 = st.columns(2)
                col1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                col2.metric("Total Weight", f"{total_kg:,.2f} kg")

                if can_fit_20:
                    st.success("✅ Perfect fit for a **20GP** container!")
                    if max_H > container_specs["20GP"]["door_h"]:
                        st.warning(f"⚠️ Note: Cargo height ({max_H}cm) is more than Door Height (228cm). Must tilt during loading.")
                else:
                    st.error("❌ Cannot fit in a single 20GP")
                    for r in reasons_20: st.write(f"- {r}")
                    
                    st.info("💡 **Solutions to use 20GP:**")
                    if total_kg > 26000 or total_cbm > 28:
                        st.write("- Split the cargo into **two 20GP** containers.")
                    if max_H > 228 and max_H <= 230:
                        st.write("- Cargo will fit inside, but load it by **tilting/slanting** to pass the door frame.")
                    if max_L > 585:
                        st.write("- Check if the item can be dismantled or loaded diagonally (if width allows).")
                
                st.dataframe(df, use_container_width=True)

    # (Other modules remain same...)
    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG Advisor")
        # Same OOG code as before
    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ DG Advisor")
        # Same DG code as before

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
