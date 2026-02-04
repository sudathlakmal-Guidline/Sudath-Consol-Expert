import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධතියේ මූලික සැකසුම් (Page Config)
st.set_page_config(page_title="Smart Consol Planner - By Sudath", layout="wide", page_icon="🚢")

# 2. Professional UI Styling - ඔබ ඉල්ලූ නිල් පැහැති තේමාව
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .header-style {
        background: linear-gradient(135deg, #002b5e 0%, #004a99 100%);
        padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .stMetric { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-bottom: 5px solid #002b5e; 
    }
    .section-header { 
        color: #002b5e; border-left: 6px solid #FFCC00; padding-left: 12px; 
        margin: 25px 0px 15px 0px; font-weight: bold; font-size: 22px; 
    }
    .oog-alert { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border-left: 6px solid #ffc107; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar Navigation ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Operational Module:", 
                        ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment", "☣️ IMDG Segregation"])
    st.divider()
    st.markdown("### ⚙️ SETTINGS")
    is_heavy = st.toggle("Enable 40HC Heavy Duty (28MT)")
    st.divider()
    if st.button("Logout of System"):
        st.cache_data.clear()
        st.rerun()

# --- 4. Main Header (ඔබ ඉල්ලූ නම සමඟ) ---
st.markdown(f"""
    <div class="header-style">
        <h1 style="margin:0; font-size: 40px; font-weight: 800; letter-spacing: 1px;">SMART CONSOL PLANNER</h1>
        <p style="font-size:19px; opacity: 0.9; margin-top:10px;">Strategic Freight Optimization & Intelligence • By Sudath</p>
    </div>
    """, unsafe_allow_html=True)

# Container Specifications Database
container_specs = {
    "20GP": {"vol": 31.5, "kg": 26000, "L": 585, "W": 230, "H": 230},
    "40GP": {"vol": 58.0, "kg": 26000, "L": 1200, "W": 230, "H": 230},
    "40HC": {"vol": 70.0, "kg": 28000 if is_heavy else 26000, "L": 1200, "W": 230, "H": 265}
}

# --- 5. Consolidation Planner Module ---
if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>1. MANIFEST DATA ENTRY</p>", unsafe_allow_html=True)
    
    # ඔබ ඉල්ලූ සියලුම තීරු සහිත දත්ත වගුව
    init_df = pd.DataFrame(columns=[
        "Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"
    ])
    df = st.data_editor(init_df, num_rows="dynamic", key="final_sudath_consol")

    if st.button("EXECUTE 3D PLANNING SIMULATION", type="primary"):
        if not df.empty:
            # Error Fixing: දත්ත පිරිසිදු කිරීම සහ සංඛ්‍යාත්මක බව තහවුරු කිරීම
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna()

            total_qty = df['Quantity'].sum()
            total_wgt = df['Weight_kg'].sum()
            df['CBM_Unit'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm']) / 1000000
            total_cbm = (df['CBM_Unit'] * df['Quantity']).sum()

            # --- 📊 GRAND TOTAL SUMMARY ---
            st.markdown("<p class='section-header'>2. CONSOLIDATION ANALYTICS</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Packages", f"{int(total_qty)} Pcs")
            col2.metric("Gross Weight", f"{total_wgt:,.2f} kg")
            col3.metric("Total Volume", f"{total_cbm:.3f} CBM")

            # හොඳම කන්ටේනරය තෝරාගැනීම
            best_con = next((name for name, s in container_specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), None)

            if best_con:
                st.success(f"✅ Recommended Equipment: **{best_con}**")
                
                # --- 🧊 3D VISUALIZATION ENGINE ---
                st.markdown("<p class='section-header'>3. 3D CARGO PLACEMENT MAP</p>", unsafe_allow_html=True)
                fig = go.Figure()
                colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3', '#FECB52']
                
                L_lim, W_lim, H_lim = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                curr_x, curr_y, curr_z = 0, 0, 0
                max_h_in_row = 0

                for idx, row in df.iterrows():
                    clr = colors[idx % len(colors)]
                    for n in range(int(row['Quantity'])):
                        dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                        
                        # Simple Packing Logic
                        if curr_x + dx > L_lim:
                            curr_x = 0; curr_y += dy
                        if curr_y + dy > W_lim:
                            curr_y = 0; curr_z += max_h_in_row
                        
                        fig.add_trace(go.Mesh3d(
                            x=[curr_x, curr_x, curr_x+dx, curr_x+dx, curr_x, curr_x, curr_x+dx, curr_x+dx],
                            y=[curr_y, curr_y+dy, curr_y+dy, curr_y, curr_y, curr_y+dy, curr_y+dy, curr_y],
                            z=[curr_z, curr_z, curr_z, curr_z, curr_z+dz, curr_z+dz, curr_z+dz, curr_z+dz],
                            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                            color=clr, opacity=0.7, name=row['Cargo_Name']
                        ))
                        curr_x += dx
                        max_h_in_row = max(max_h_in_row, dz)

                fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("<div class='oog-alert'>🚨 CRITICAL: Shipment exceeds all standard container limits. Proceed to OOG Assessment.</div>", unsafe_allow_html=True)

# --- 6. OOG Cargo Assessment Module ---
elif app_mode == "🏗️ OOG Cargo Assessment":
    st.markdown("<p class='section-header'>1. OOG DIMENSIONS & WEIGHT INPUT</p>", unsafe_allow_html=True)
    oog_df = st.data_editor(pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Weight_kg"]), num_rows="dynamic")

    if st.button("ANALYZE OOG LOADING SOLUTION", type="primary"):
        for idx, row in oog_df.dropna().iterrows():
            L, W, H, Wgt = float(row['Length_cm']), float(row['Width_cm']), float(row['Height_cm']), float(row['Weight_kg'])
            st.markdown(f"#### 🔍 Assessment for: {row['Cargo_Name']}")
            
            # OOG හඳුනාගැනීමේ Logic එක
            if L > 1200 or W > 230 or H > 265 or Wgt > 28000:
                st.error("STATUS: OUT-OF-GAUGE (OOG) DETECTED")
                if Wgt > 45000 or L > 1600:
                    st.warning("💡 SOLUTION: **BREAKBULK (BB)** - Specialized vessel handling required.")
                elif L <= 1180 and W <= 350:
                    st.info("💡 SOLUTION: **FLAT RACK (FR)** - Suitable for Over-Width/Over-Height cargo.")
                else:
                    st.info("💡 SOLUTION: **FLATBED / PLATFORM** - Suitable for extra-long cargo.")
            else:
                st.success("✅ STATUS: IN-GAUGE - Can be loaded in a Standard Container.")

# --- 7. IMDG Segregation ---
elif app_mode == "☣️ IMDG Segregation":
    st.info("IMDG Class Segregation Module is active. Ensure Class compatibility before Consolidation.")

# Footer
st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Planner v3.0 | Final Secure Release | By Sudath</p>", unsafe_allow_html=True)
