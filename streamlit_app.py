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

    # Internal Height updated to 230cm for GP
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 230, "door_h": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 230, "door_h": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265, "door_h": 258}
    }

    st.sidebar.header("🛠️ SELECT SERVICE")
    app_mode = st.sidebar.radio("Navigation:", ["1. CONSOL PLANNING", "2. OOG CHECK", "3. IMO/DG CHECK"])

    if app_mode == "1. CONSOL PLANNING":
        st.subheader("📦 Standard Consolidation Planner")
        
        # Helper to clear data
        if st.button("Clear All Data"):
            st.cache_data.clear()
            st.rerun()

        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_Per_Unit_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="consol_editor_v2")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                # Cleaning data: Remove empty rows and convert to numbers
                df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_Per_Unit_kg"])
                for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_Per_Unit_kg"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.dropna()

                if not df.empty:
                    # Calculations
                    max_L = df['Length_cm'].max()
                    max_W = df['Width_cm'].max()
                    max_H = df['Height_cm'].max()
                    
                    df['Line_CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
                    df['Line_Weight'] = df['Weight_Per_Unit_kg'] * df['Quantity']
                    
                    total_cbm = df['Line_CBM'].sum()
                    total_kg = df['Line_Weight'].sum()

                    st.divider()
                    
                    # 20GP Feasibility Logic
                    reasons_20 = []
                    if max_L > container_specs["20GP"]["L"]: reasons_20.append(f"Length exceeds 20GP limit ({max_L}cm > 585cm)")
                    if max_W > container_specs["20GP"]["W"]: reasons_20.append(f"Width exceeds 20GP limit ({max_W}cm > 230cm)")
                    if max_H > container_specs["20GP"]["H"]: reasons_20.append(f"Height exceeds 20GP internal limit ({max_H}cm > 230cm)")
                    if total_kg > container_specs["20GP"]["max_kg"]: reasons_20.append(f"Total weight ({total_kg:,.2f}kg) exceeds 20GP payload (26,000kg)")
                    if total_cbm > container_specs["20GP"]["max_cbm"]: reasons_20.append(f"Total volume ({total_cbm:.2f} CBM) exceeds 20GP capacity (28 CBM)")

                    col1, col2 = st.columns(2)
                    col1.metric("Total Volume", f"{total_cbm:.2f} CBM")
                    col2.metric("Total Weight", f"{total_kg:,.2f} kg")

                    if not reasons_20:
                        st.success("✅ **20GP is Suitable!**")
                        if max_H > 228:
                            st.warning("⚠️ Tilt required to pass 228cm door height.")
                    else:
                        st.error("❌ Cannot fit in a single 20GP")
                        for r in reasons_20: st.write(f"- {r}")
                        
                        st.info("💡 **Expert Advice:**")
                        if total_kg > 26000 or total_cbm > 28:
                            st.write("- **Option A:** Split cargo into **two 20GP** containers.")
                            st.write("- **Option B:** Upgrade to a **40GP** container.")
                        if 228 < max_H <= 230:
                            st.write("- **Option C:** Load using **tilting method** to pass the 228cm door frame.")

                    st.dataframe(df, use_container_width=True)
            else:
                st.warning("Please enter cargo details first.")

    elif app_mode == "2. OOG CHECK":
        st.subheader("🏗️ OOG Advisor")
        l = st.number_input("Length (cm)", value=0)
        w = st.number_input("Width (cm)", value=0)
        h = st.number_input("Height (cm)", value=0)
        if st.button("Check"):
            if l > 1200 or w > 230 or h > 265:
                st.error("🚨 OOG Cargo Detected!")
            else:
                st.success("Fits in standard equipment.")

    elif app_mode == "3. IMO/DG CHECK":
        st.subheader("☣️ DG Advisor")
        st.info("Select IMDG Class to see segregation rules.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
