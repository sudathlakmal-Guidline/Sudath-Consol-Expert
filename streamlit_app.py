import streamlit as st
import pandas as pd

# වෙබ් පිටුවේ සැකසුම්
st.set_page_config(page_title="Sudath Consol Expert", layout="wide", page_icon="🔐")

# --- සරල Password ආරක්ෂණ පද්ධතිය ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Admin Login Required</h2>", unsafe_allow_html=True)
        password = st.text_input("Please enter Admin Password:", type="password")
        if st.button("Login"):
            if password == "sudath123":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password. Please try again.")
        return False
    return True

if check_password():
    # Header කොටස
    st.markdown("""
        <div style="background-color:#003366;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">🚀 SUDATH CONSOL EXPERT</h1>
        <h3 style="color:#FFCC00;text-align:center;">Logistics Intelligence Suite</h3>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose Service:", ["Standard Consolidation", "OOG Handling", "DG Compliance"])

    containers = {
        "20GP": {"vol": 28, "max_h": 2.38},
        "40GP": {"vol": 58, "max_h": 2.38},
        "40HC": {"vol": 68, "max_h": 2.69}
    }

    if app_mode == "Standard Consolidation":
        st.subheader("📦 Standard Container Loading Planner")
        
        # දත්ත වගුව - මෙහිදී column types නිවැරදිව ලබා දී ඇත
        initial_data = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_data, num_rows="dynamic")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                try:
                    # වැදගත්ම කොටස: සියලුම අගයන් බලහත්කාරයෙන් අංක (Numeric) බවට පත් කිරීම
                    for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # හිස් පේළි ඉවත් කිරීම
                    df = df.dropna()

                    if not df.empty:
                        # ගණනය කිරීම්
                        df['CBM_per_unit'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm']) / 1000000
                        df['Total_CBM'] = df['CBM_per_unit'] * df['Quantity']
                        df['Total_Weight'] = df['Weight_kg'] * df['Quantity']
                        
                        total_vol = df['Total_CBM'].sum()
                        total_weight = df['Total_Weight'].sum()
                        max_h = df['Height_cm'].max() / 100

                        st.divider()
                        col1, col2 = st.columns(2)
                        col1.metric("Total Volume", f"{total_vol:.2f} CBM")
                        col2.metric("Total Weight", f"{total_weight:.2f} kg")

                        # Container Recommendation
                        found = False
                        for name, specs in containers.items():
                            if total_vol <= specs["vol"] and max_h <= specs["max_h"]:
                                st.success(f"✅ Recommended Container: **{name}**")
                                found = True
                                break
                        if not found:
                            st.warning("⚠️ High Volume! You may need multiple containers or a special equipment.")
                        
                        st.write("### 📋 Loading Details")
                        st.dataframe(df)
                    else:
                        st.error("⚠️ කරුණාකර වගුවේ සියලුම කොටු නිවැරදිව පුරවන්න (අංක පමණක් භාවිතා කරන්න).")
                except Exception as e:
                    st.error(f"🚫 Error: Calculation failed. Please check your inputs.")
            else:
                st.info("💡 Please add cargo details to the table above.")

    # Logout
    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
