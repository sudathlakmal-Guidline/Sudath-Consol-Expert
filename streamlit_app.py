import streamlit as st
import pandas as pd

# වෙබ් පිටුවේ සැකසුම්
st.set_page_config(page_title="Sudath Consol Expert", layout="wide", page_icon="🔐")

# --- සරල Password ආරක්ෂණ පද්ධතිය ---
def check_password():
    """මුරපදය නිවැරදි දැයි පරීක්ෂා කරයි."""
    if "password_correct" not in st.session_state:
        # පළමු වරට පිවිසෙන විට login පෙන්වයි
        st.markdown("<h2 style='text-align: center;'>🔐 Admin Login Required</h2>", unsafe_allow_html=True)
        password = st.text_input("Please enter Admin Password:", type="password")
        if st.button("Login"):
            # මෙහි 'sudath123' යනු ඔබගේ Password එකයි. අවශ්‍ය නම් මෙය වෙනස් කරන්න.
            if password == "sudath123":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password. Please try again.")
        return False
    else:
        return True

# Password එක නිවැරදි නම් පමණක් ප්‍රධාන ඇප් එක පෙන්වන්න
if check_password():
    # Header කොටස
    st.markdown("""
        <div style="background-color:#003366;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">🚀 SUDATH CONSOL EXPERT</h1>
        <h3 style="color:#FFCC00;text-align:center;">Authorized Access Only - Logistics Intelligence Suite</h3>
        </div>
        """, unsafe_allow_html=True)

    # පසෙකින් ඇති මෙනුව (Sidebar)
    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose Service:", ["Standard Consolidation", "OOG Handling (Coming Soon)", "DG Compliance (Coming Soon)"])

    # කන්ටේනර් දත්ත
    containers = {
        "20GP": {"vol": 28, "max_h": 2.38, "max_w": 2.34},
        "40GP": {"vol": 58, "max_h": 2.38, "max_w": 2.34},
        "40HC": {"vol": 68, "max_h": 2.69, "max_w": 2.34}
    }

    if app_mode == "Standard Consolidation":
        st.subheader("📦 Standard Container Loading Planner")
        df = st.data_editor(pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]), num_rows="dynamic")

        if st.button("Generate Loading Plan"):
            if not df.empty:
                df['CBM_per_unit'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm']) / 1000000
                df['Total_CBM'] = df['CBM_per_unit'] * df['Quantity']
                total_vol = df['Total_CBM'].sum()
                max_h = df['Height_cm'].max() / 100

                st.divider()
                st.metric("Total Volume", f"{total_vol:.2f} CBM")

                rec = "Multiple Containers Needed"
                for name, specs in containers.items():
                    if total_vol <= specs["vol"] and max_h <= specs["max_h"]:
                        rec = name
                        st.success(f"✅ Recommended: **{name}**")
                        break
                st.dataframe(df)
            else:
                st.warning("Please enter cargo details first.")

    # Logout බොත්තම
    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
