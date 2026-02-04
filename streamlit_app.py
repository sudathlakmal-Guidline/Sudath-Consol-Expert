import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Smart Consol & OOG Planner", layout="wide", page_icon="🏗️")

# Professional UI Styling
st.markdown("""
    <style>
    .header-style {
        background: linear-gradient(135deg, #021d38 0%, #0b4a8a 100%);
        padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;
    }
    .oog-alert {
        background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107;
    }
    .section-header { color: #002b5e; border-left: 5px solid #FFCC00; padding-left: 10px; margin: 25px 0px; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
    <div class="header-style">
        <h1 style="margin:0; font-size: 38px;">🏗️ SMART CONSOL & OOG PLANNER</h1>
        <p style="font-size:18px; opacity: 0.9; margin-top:10px;">Strategic Freight Intelligence for Standard & Over-Dimensional Cargo • By Sudath</p>
    </div>
    """, unsafe_allow_html=True)

# Container & Special Equipment Database
standard_specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "Payload": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "Payload": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "Payload": 28000}
}

# --- Data Input ---
st.markdown("<p class='section-header'>1. CARGO DIMENSIONS & WEIGHT INPUT</p>", unsafe_allow_html=True)
init_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
df = st.data_editor(init_df, num_rows="dynamic", key="oog_planner_v1")

if st.button("ANALYZE LOADING SOLUTION", type="primary"):
    if not df.empty:
        df = df.dropna().apply(pd.to_numeric, errors='ignore')
        
        for idx, row in df.iterrows():
            L, W, H, Wgt = row['Length_cm'], row['Width_cm'], row['Height_cm'], row['Weight_kg']
            name = row['Cargo_Name']
            
            st.markdown(f"### 🔍 Analysis for: {name}")
            
            # 1. Standard Container Check
            fit_standard = False
            for c_name, s in standard_specs.items():
                if L <= s["L"] and W <= s["W"] and H <= s["H"] and Wgt <= s["Payload"]:
                    st.success(f"✅ Fits in Standard Equipment: **{c_name}**")
                    fit_standard = True
                    break
            
            # 2. OOG Solution Logic (සාමාන්‍ය එකට නොගැලපේ නම්)
            if not fit_standard:
                st.markdown("<div class='oog-alert'>⚠️ **OOG DETECTED:** This item exceeds standard container dimensions.</div>", unsafe_allow_html=True)
                
                # Solution Decision Tree
                if H <= 400 and W <= 350 and Wgt <= 45000:
                    if L <= 1180:
                        st.info("💡 Solution: **40ft FLAT RACK (FR)** - Suitable for over-width/height cargo.")
                    else:
                        st.info("💡 Solution: **FLATBED TRAILER / PLATFORM** - Suitable for extra-long and over-width cargo.")
                
                elif Wgt > 45000 or L > 1500:
                    st.warning("🚨 Solution: **BREAKBULK (BB)** - Cargo is too heavy or large for containerized equipment. Specialized vessel handling required.")
                
                else:
                    st.info("💡 Solution: **OPEN TOP (OT)** - Suitable if only height is the issue and it can be craned from above.")

            # --- 📊 Metrics ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Dimensions (LxWxH)", f"{L} x {W} x {H} cm")
            c2.metric("Unit Weight", f"{Wgt:,.0f} kg")
            c3.metric("Volume", f"{(L*W*H)/1000000:.2f} CBM")

        # --- 🧊 3D Preview (Simple Box Visualization) ---
        st.markdown("<p class='section-header'>2. CARGO VISUALIZATION</p>", unsafe_allow_html=True)
        fig = go.Figure()
        for idx, row in df.iterrows():
            dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
            fig.add_trace(go.Mesh3d(
                x=[0, 0, dx, dx, 0, 0, dx, dx], y=[0, dy, dy, 0, 0, dy, dy, 0], z=[0, 0, 0, 0, dz, dz, dz, dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.6, color='blue', name=row['Cargo_Name']
            ))
        fig.update_layout(scene=dict(aspectmode='data'))
        st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("### 🚢 SUDATH LOGISTICS")
st.sidebar.info("OOG Module: Identifies Flat Rack, Flatbed, and Breakbulk solutions based on cargo profile.")
