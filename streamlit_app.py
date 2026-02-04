import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Smart Consol Planner - By Sudath", layout="wide", page_icon="🚢")

# 2. Professional Styling
st.markdown("""
    <style>
    .header-style { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    .suggestion-card { background-color: #f0f7ff; border-left: 6px solid #004a99; padding: 15px; border-radius: 8px; margin: 10px 0; color: #002b5e; }
    .section-header { color: #002b5e; border-left: 6px solid #FFCC00; padding-left: 12px; margin: 25px 0px; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Fixed Container Specs (Dimensions & Limits)
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION")
    app_mode = st.radio("Module:", ["📦 Consolidation Planner", "🏗️ OOG Assessment"])
    is_heavy = st.toggle("Enable 28MT Mode (40HC Only)")

# --- Main Header ---
st.markdown(f'<div class="header-style"><h1>🚢 SMART CONSOL PLANNER</h1><p>Strategic Freight Intelligence • By Sudath</p></div>', unsafe_allow_html=True)

if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>1. MANIFEST DATA ENTRY</p>", unsafe_allow_html=True)
    init_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
    df = st.data_editor(init_df, num_rows="dynamic", key="final_v6_sudath")

    if st.button("EXECUTE PLANNING SIMULATION", type="primary"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            total_wgt = df['Weight_kg'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            st.markdown("<p class='section-header'>2. CONSOLIDATION ANALYTICS</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.metric("Total Weight", f"{total_wgt:,.2f} kg")
            c2.metric("Total Volume", f"{total_cbm:.3f} CBM")

            # --- Smart Recommendation & Hold Suggestions ---
            best_con = next((n for n, s in specs.items() if total_cbm <= s["vol"] and total_wgt <= (28000 if is_heavy and n=="40HC" else s["kg"])), None)

            if best_con:
                st.success(f"✅ Recommended: **{best_con}**")
                st.progress(min(total_cbm / specs[best_con]["vol"], 1.0))
            else:
                st.markdown('<div class="suggestion-card">', unsafe_allow_html=True)
                st.error("⚠️ STANDARD EQUIPMENT LIMIT EXCEEDED")
                st.write("### 💡 SUDATH'S LOGISTICS SUGGESTIONS:")
                
                # Weight based Suggestions
                if total_wgt > 26000:
                    st.write(f"🚩 **Weight Issue:** Total {total_wgt:,.0f}kg exceeds 26MT limit.")
                    st.write("👉 **Option 1:** Proceed with **2 x 20GP** containers.")
                    over_weight = total_wgt - 26000
                    # කිනම් බඩු ප්‍රමාණයක් Hold කළ යුතුද?
                    st.write(f"👉 **Option 2:** Hold approximately **{over_weight:,.2f} kg** to proceed with **1 x 20GP**.")
                
                # Volume based Suggestions
                if total_cbm > 31.5 and total_cbm <= 70:
                    st.write(f"🚩 **Volume Issue:** {total_cbm:.3f} CBM is too much for a 20GP.")
                    st.write(f"👉 **Suggestion:** Upgrade to a **40GP or 40HC**.")
                    over_vol = total_cbm - 31.5
                    st.write(f"👉 **Alternative:** Hold **{over_vol:.3f} CBM** worth of cargo to proceed with **20GP**.")
                
                elif total_cbm > 70:
                    st.write(f"🚩 **Critical Volume:** {total_cbm:.3f} CBM exceeds 40HC.")
                    st.write("👉 **Suggestion:** Split into **2 x 40HC** or **1 x 40HC + 1 x 20GP**.")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- 3D Chart with Strict Height & Color Key ---
            st.markdown("<p class='section-header'>3. 3D CARGO PREVIEW & COLOR KEY</p>", unsafe_allow_html=True)
            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3', '#FECB52']
            limit_h = specs[best_con]["H"] if best_con else 265
            
            key_cols = st.columns(len(df))
            fig = go.Figure()
            for i, (idx, row) in enumerate(df.iterrows()):
                clr = colors[i % len(colors)]
                key_cols[i].markdown(f'<div style="background-color:{clr}; width:15px; height:15px; display:inline-block;"></div> {row["Cargo_Name"]}', unsafe_allow_html=True)
                fig.add_trace(go.Mesh3d(x=[0,0,row['Length_cm'],row['Length_cm'],0,0,row['Length_cm'],row['Length_cm']],
                                        y=[0,row['Width_cm'],row['Width_cm'],0,0,row['Width_cm'],row['Width_cm'],0],
                                        z=[0,0,0,0,row['Height_cm'],row['Height_cm'],row['Height_cm'],row['Height_cm']],
                                        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                        color=clr, opacity=0.8))

            fig.update_layout(scene=dict(zaxis=dict(range=[0, limit_h]), aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Planner v6.0 | Final Comprehensive Release | By Sudath</p>", unsafe_allow_html=True)
