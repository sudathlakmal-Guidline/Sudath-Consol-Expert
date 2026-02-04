import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Smart Consol Planner - By Sudath", layout="wide", page_icon="🚢")

# 2. නිල් පැහැති වෘත්තීය තේමාව සහ Styles
st.markdown("""
    <style>
    .header-style {
        background: linear-gradient(135deg, #002b5e 0%, #004a99 100%);
        padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;
    }
    .suggestion-box {
        background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; border-radius: 5px; margin: 10px 0;
    }
    .section-header { color: #002b5e; border-left: 6px solid #FFCC00; padding-left: 12px; margin: 25px 0px; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ස්ථාවර කන්ටේනර් දත්ත (Lock කර ඇත)
container_specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment"])
    st.divider()
    is_heavy = st.toggle("40HC Heavy Duty Mode (28MT)")

# --- Header ---
st.markdown(f"""
    <div class="header-style">
        <h1 style="margin:0; font-size: 38px;">SMART CONSOL PLANNER</h1>
        <p style="font-size:18px; opacity: 0.9; margin-top:10px;">Strategic Freight Optimization • By Sudath</p>
    </div>
    """, unsafe_allow_html=True)

# --- Module: Consolidation Planner ---
if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>1. MANIFEST DATA ENTRY</p>", unsafe_allow_html=True)
    init_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
    df = st.data_editor(init_df, num_rows="dynamic", key="final_sudath_v4")

    if st.button("EXECUTE PLANNING SIMULATION", type="primary"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            total_wgt = df['Weight_kg'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            # --- Analytics & % Bar ---
            st.markdown("<p class='section-header'>2. CONSOLIDATION ANALYTICS</p>", unsafe_allow_html=True)
            
            # පද්ධතිය විසින් ස්වයංක්‍රීයව හොඳම කන්ටේනරය තෝරා ගැනීම
            best_con = next((name for name, s in container_specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), None)
            
            if best_con:
                fill_p = (total_cbm / container_specs[best_con]["vol"]) * 100
                st.write(f"**Filled:** {fill_p:.1f}% | **Remaining:** {container_specs[best_con]['vol'] - total_cbm:.3f} CBM")
                st.progress(fill_p / 100) # ඔබ ඉල්ලූ % Bar එක
                st.success(f"✅ Recommended Equipment: **{best_con}**")
            else:
                # --- බර හෝ පරිමාව වැඩි නම්Suggestions ලබා දීම ---
                st.markdown("<div class='suggestion-box'>", unsafe_allow_html=True)
                st.error("⚠️ STANDARD EQUIPMENT LIMIT EXCEEDED")
                st.write("**Reasons & Suggestions:**")
                if total_wgt > 28000:
                    st.write(f"- **Weight Issue:** Total weight ({total_wgt:,.0f}kg) is over 40HC limit. **Suggestion:** Split into 2 x 20GP or 1 x 40GP + 1 x 20GP.")
                if total_cbm > 70:
                    st.write(f"- **Volume Issue:** Total volume ({total_cbm:.3f} CBM) is over 40HC capacity. **Suggestion:** Use multiple containers.")
                st.markdown("</div>", unsafe_allow_html=True)

            # --- 3D Chart with Locked Axis ---
            st.markdown("<p class='section-header'>3. 3D CARGO PREVIEW</p>", unsafe_allow_html=True)
            fig = go.Figure()
            # Default visualization limit (40HC)
            limit_h = 265 
            for _, r in df.iterrows():
                fig.add_trace(go.Mesh3d(x=[0,0,r['Length_cm'],r['Length_cm'],0,0,r['Length_cm'],r['Length_cm']],
                                        y=[0,r['Width_cm'],r['Width_cm'],0,0,r['Width_cm'],r['Width_cm'],0],
                                        z=[0,0,0,0,r['Height_cm'],r['Height_cm'],r['Height_cm'],r['Height_cm']],
                                        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                        opacity=0.6, color='blue', name=r['Cargo_Name']))
            fig.update_layout(scene=dict(zaxis=dict(range=[0, limit_h])), margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)

# --- Module: OOG Assessment (තනි පැකේජය විශාල නම් පමණයි) ---
elif app_mode == "🏗️ OOG Cargo Assessment":
    st.markdown("<p class='section-header'>🏗️ OOG (OUT-OF-GAUGE) ASSESSMENT</p>", unsafe_allow_html=True)
    st.info("Note: Use this ONLY for single units that cannot fit inside a standard container.")
    oog_in = st.data_editor(pd.DataFrame(columns=["Unit_Name", "Length_cm", "Width_cm", "Height_cm", "Weight_kg"]), num_rows="dynamic")
    
    if st.button("CHECK OOG STATUS"):
        for _, r in oog_in.dropna().iterrows():
            L, W, H, Wgt = float(r['Length_cm']), float(r['Width_cm']), float(r['Height_cm']), float(r['Weight_kg'])
            if L > 1200 or W > 230 or H > 265:
                st.error(f"🚨 {r['Unit_Name']} is OOG. Suggestion: **Flat Rack / Flatbed**")
            elif Wgt > 30000:
                st.warning(f"🚨 {r['Unit_Name']} is Heavy-Lift. Suggestion: **Breakbulk**")
            else:
                st.success(f"✅ {r['Unit_Name']} fits in Standard Container.")

st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Planner v4.0 | By Sudath</p>", unsafe_allow_html=True)
