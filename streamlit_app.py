import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Sudath DG & Consol Expert", layout="wide", page_icon="☣️")

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

# --- Main App Logic ---
if check_password():
    st.markdown("""
        <div style="background-color:#800000;padding:20px;border-radius:10px">
        <h1 style="color:white;text-align:center;">☣️ SUDATH DG & CONSOL EXPERT</h1>
        <h3 style="color:#FFCC00;text-align:center;">IMDG Compliance & Colombo Export Advisor</h3>
        </div>
        """, unsafe_allow_html=True)

    # Standard Container Specifications
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265}
    }

    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose Service:", ["Consolidation & OOG Check", "DG Compliance & Segregation"])

    # --- MODULE 1: CONSOLIDATION & OOG ---
    if app_mode == "Consolidation & OOG Check":
        st.subheader("📦 Standard & OOG Cargo Planner")
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic", key="consol_editor")

        if st.button("Analyze Shipment"):
            if not df.empty:
                try:
                    df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric, errors='coerce')
                    df = df.dropna()
                    
                    max_L, max_W, max_H = df['Length_cm'].max(), df['Width_cm'].max(), df['Height_cm'].max()
                    total_kg = df['Weight_kg'].sum()
                    total_cbm = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']).sum() / 1000000

                    st.divider()
                    if max_L > 1200 or max_W > 230 or max_H > 265:
                        st.error("⚠️ OOG / NON-CONTAINERIZED CARGO DETECTED")
                        rec = "BREAK BULK / FLAT BED" if max_L > 1200 else "FLAT RACK / OPEN TOP"
                        st.info(f"Recommended Solution: **{rec}**")
                    else:
                        best_con = None
                        for con, specs in container_specs.items():
                            if max_L <= specs["L"] and max_W <= specs["W"] and max_H <= specs["H"] and total_kg <= specs["max_kg"] and total_cbm <= specs["max_cbm"]:
                                best_con = con
                                break
                        
                        if best_con:
                            st.success(f"✅ Use **{best_con}** | Space left: {container_specs[best_con]['max_cbm']-total_cbm:.2f} CBM")
                        else:
                            st.warning("Cargo fits dimensions but exceeds weight/volume for one container.")
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- MODULE 2: DG COMPLIANCE ---
    elif app_mode == "DG Compliance & Segregation":
        st.subheader("⚠️ IMDG Class & Colombo Customs Compliance")
        
        c1, c2 = st.columns(2)
        with c1:
            imdg_class = st.selectbox("IMDG Class:", ["2.1", "3", "4.1", "5.1", "6.1", "8", "9"])
            un_no = st.text_input("UN Number:")
            carrier = st.selectbox("Line:", ["Maersk", "MSC", "Hapag-Lloyd", "CMA CGM", "ONE", "Other"])
        
        with c2:
            st.markdown("### 📄 Required Docs (Colombo Customs)")
            st.write("- **CUSDEC** (Customs Declaration)")
            st.write("- **DGD** (Dangerous Goods Declaration)")
            st.write("- **MSDS** (16 Sections mandatory)")
            st.write("- **CDN / Boat Note**")

        if st.button("Check DG Compliance"):
            st.divider()
            st.subheader(f"Advice for Class {imdg_class} via {carrier}")
            
            if imdg_class in seg_matrix:
                st.info("🔍 **IMDG Segregation Advisor:**")
                for other, rule in seg_matrix[imdg_class].items():
                    if rule == "2": st.error(f"❌ **Separated from** Class {other} (min 6m)")
                    if rule == "1": st.warning(f"⚠️ **Away from** Class {other} (min 3m)")

            st.markdown("### 🏷️ Labeling")
            st.write(f"Ensure Class {imdg_class} placards are on all 4 sides of the container.")
            
            if carrier in ["Maersk", "MSC"]:
                st.error(f"🛑 {carrier} requires DG approval before gate-in.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
