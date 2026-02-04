import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sudath DG Consol Expert", layout="wide", page_icon="☣️")

# --- IMDG Segregation Logic ---
# 1: Away from, 2: Separated from, 3: Separated by a complete compartment, 4: Longitudinally separated
seg_matrix = {
    "2.1": {"2.1": "X", "2.2": "0", "3": "2", "4.1": "0", "5.1": "2", "8": "1"},
    "3":   {"2.1": "2", "2.2": "0", "3": "X", "4.1": "0", "5.1": "2", "8": "0"},
    "5.1": {"2.1": "2", "2.2": "2", "3": "2", "4.1": "2", "5.1": "X", "8": "2"},
    "8":   {"2.1": "1", "2.2": "0", "3": "0", "4.1": "1", "5.1": "2", "8": "X"}
}

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
        <div style="background-color:#800000;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">☣️ SUDATH DG & CONSOL EXPERT</h1>
        <h3 style="color:#FFCC00;text-align:center;">IMDG Compliance & Global Export Advisor</h3>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose Service:", ["Consolidation & OOG Check", "DG Compliance & Segregation"])

    if app_mode == "DG Compliance & Segregation":
        st.subheader("⚠️ IMDG Class Segregation & Documentation Check")
        
        col1, col2 = st.columns(2)
        with col1:
            imdg_class = st.selectbox("Select IMDG Class of Cargo:", ["2.1", "2.2", "3", "4.1", "5.1", "6.1", "8", "9"])
            un_number = st.text_input("UN Number (e.g., 1993):")
            carrier = st.selectbox("Shipping Line / Carrier:", ["Maersk", "MSC", "Hapag-Lloyd", "CMA CGM", "OOCL", "ONE", "NVOCC"])

        with col2:
            st.info("💡 **Required Documents for Export (Colombo):**")
            st.markdown("""
            * **MSDS** (Latest version - 16 sections)
            * **DGD** (Dangerous Goods Declaration)
            * **Container Packing Certificate**
            * **Technical Name** for 'NOS' Cargo
            """)

        if st.button("Check Compliance"):
            st.divider()
            st.write(f"### 🛡️ Expert Advice for UN {un_number} (Class {imdg_class}) via {carrier}")
            
            # Segregation Tip
            st.warning(f"**Segregation Note:** Class {imdg_class} must be kept according to IMDG Table 7.2.1.1.")
            if imdg_class in seg_matrix:
                st.write("Common Segregation Rules:")
                for other_class, rule in seg_matrix[imdg_class].items():
                    if rule == "2":
                        st.write(f"- ❌ **Separated from Class {other_class}:** 6 meters minimum distance.")
                    elif rule == "1":
                        st.write(f"- ⚠️ **Away from Class {other_class}:** 3 meters minimum distance.")

            # Carrier Specifics
            if carrier in ["Maersk", "MSC"]:
                st.error(f"🔔 **{carrier} Special Requirement:** Requires pre-approval before gating in. Ensure Net Explosive Quantity (NEQ) is mentioned if applicable.")
            
            # Labeling
            st.markdown("### 🏷️ Labeling Requirements")
            st.image("https://www.shippingschool.com/wp-content/uploads/2018/09/Hazard-Class-3-Flammable-Liquid.png", width=100)
            st.write(f"Ensure **Inner Packaging** has UN Specification markings and **Outer Container** has 4 placards (all sides).")

    elif app_mode == "Consolidation & OOG Check":
        # (මීට පෙර සාදාගත් Consolidation Code එක මෙතැනට ඇතුළත් වේ)
        st.write("Consolidation & OOG Module is Active.")
        # ... [පරණ Code එක මෙතැනට] ...

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
