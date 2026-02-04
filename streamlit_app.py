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
        <h3 style="color:#FFCC00;text-align:center;">Logistics Intelligence & OOG Advisor</h3>
        </div>
        """, unsafe_allow_html=True)

    # Standard Internal Limits
    std_limits = {"L": 1200, "W": 230, "H": 265, "Weight": 26500}

    # Container Specs for Standard Logic
    container_specs = {
        "20GP": {"max_cbm": 28.0, "max_kg": 26000, "L": 585, "W": 230, "H": 228},
        "40GP": {"max_cbm": 55.0, "max_kg": 26000, "L": 1200, "W": 230, "H": 228},
        "40HC": {"max_cbm": 68.0, "max_kg": 26500, "L": 1200, "W": 230, "H": 265}
    }

    st.sidebar.header("Expert Mode")
    app_mode = st.sidebar.selectbox("Service:", ["Consolidation & OOG Check", "DG Compliance"])

    if app_mode == "Consolidation & OOG Check":
        st.subheader("📦 Smart Loading Planner (Standard & OOG)")
        
        initial_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df = st.data_editor(initial_df, num_rows="dynamic")

        if st.button("Analyze Shipment"):
            if not df.empty:
                try:
                    for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.dropna()

                    if not df.empty:
                        max_L = df['Length_cm'].max()
                        max_W = df['Width_cm'].max()
                        max_H = df['Height_cm'].max()
                        total_kg = df['Weight_kg'].sum()
                        total_cbm = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']).sum() / 1000000

                        st.divider()
                        
                        # --- OOG / NON-CONTAINERIZED LOGIC ---
                        is_oog = False
                        if max_L > std_limits["L"] or max_W > std_limits["W"] or max_H > std_limits["H"]:
                            is_oog = True

                        if is_oog:
                            st.error("⚠️ ALERT: NON-CONTAINERIZED / OOG CARGO DETECTED")
                            st.warning("Based on International Maritime Standards, this cargo cannot fit into standard GP/HC containers.")
                            
                            # Recommendation Logic
                            if max_L > 1200:
                                rec = "BREAK BULK / FLAT BED"
                                note = "Cargo length exceeds 40ft limit. Requires vessel deck loading or multi-axle flatbed trailers."
                            elif max_W > 230 or max_H > 265:
                                if max_H > 265 and max_W <= 230:
                                    rec = "OPEN TOP (OT) CONTAINER"
                                    note = "Cargo is over-height but fits standard width. Use OT with tarpaulin."
                                else:
                                    rec = "FLAT RACK (FR) CONTAINER"
                                    note = "Cargo is over-width/over-height. Requires Flat Rack for side or top loading."
                            
                            st.subheader(f"Recommended Solution: {rec}")
                            st.info(f"💡 Reason: {note}")
                            
                        
                        else:
                            # --- STANDARD CONTAINER LOGIC ---
                            best_con = None
                            for con, specs in container_specs.items():
                                if max_L <= specs["L"] and max_W <= specs["W"] and max_H <= specs["H"] and total_kg <= specs["max_kg"] and total_cbm <= specs["max_cbm"]:
                                    best_con = con
                                    break
                            
                            if best_con:
                                st.success(f"✅ Recommended Standard Container: **{best_con}**")
                                st.write(f"Remaining: {container_specs[best_con]['max_cbm']-total_cbm:.2f} CBM")
                            else:
                                st.warning("Fits dimensions but exceeds total weight/volume capacity for a single container.")

                        st.markdown("---")
                        st.caption("🔍 Sources: Guidelines based on International Maritime Organization (IMO) Cargo Stowing and Standard ISO Container Internal Specs.")
                        st.dataframe(df)

                except Exception:
                    st.error("🚫 Please enter numeric values correctly.")

    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()
