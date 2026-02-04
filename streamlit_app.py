import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Smart Consol Planner - By Sudath", layout="wide", page_icon="🚢")

# 2. Professional CSS Styling
st.markdown("""
    <style>
    .header-style {
        background: linear-gradient(135deg, #002b5e 0%, #004a99 100%);
        padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px;
    }
    .suggestion-card {
        background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 20px; border-radius: 10px; margin: 15px 0; color: #856404; font-size: 16px;
    }
    .section-header { color: #002b5e; border-left: 6px solid #FFCC00; padding-left: 12px; margin: 20px 0px; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ස්ථාවර කන්ටේනර් දත්ත (Lock Dimensions)
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- 4. NAVIGATION CENTER (Sidebar) ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Operational Module:", 
                        ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment", "☣️ IMDG Segregation"])
    st.divider()
    st.markdown("### ⚙️ SYSTEM SETTINGS")
    is_heavy = st.toggle("Enable 40HC Heavy Duty (28,000kg)")
    st.divider()
    if st.button("Logout of System"):
        st.cache_data.clear()
        st.rerun()

# --- 5. Main Header ---
st.markdown(f'<div class="header-style"><h1 style="margin:0;">🚢 SMART CONSOL & OOG PLANNER</h1><p>Strategic Freight Optimization & Intelligence • By Sudath</p></div>', unsafe_allow_html=True)

if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>1. MANIFEST DATA INPUT</p>", unsafe_allow_html=True)
    
    # දත්ත ඇතුළත් කරන වගුව
    init_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"])
    df = st.data_editor(init_df, num_rows="dynamic", key="final_v10_sudath")

    if st.button("EXECUTE 3D PLANNING SIMULATION", type="primary"):
        if not df.empty:
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            for col in ["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            total_wgt = df['Weight_kg'].sum()
            total_qty = df['Quantity'].sum()
            total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

            # --- Analytics Summary ---
            st.markdown("<p class='section-header'>2. CONSOLIDATION ANALYTICS</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Packages", f"{int(total_qty)} Pcs")
            col2.metric("Gross Weight", f"{total_wgt:,.2f} kg")
            col3.metric("Total Volume", f"{total_cbm:.3f} CBM")

            # --- බර සහ යෝජනා (Weight Logic) ---
            # බර 26,000kg ට වැඩිනම් 40HC යෝජනා නොකර කෙලින්ම split කරන්න කියනවා
            if total_wgt > 26000:
                st.markdown('<div class="suggestion-card">', unsafe_allow_html=True)
                st.error(f"🚨 CRITICAL WEIGHT: {total_wgt:,.0f} kg exceeds standard payload limits.")
                st.write("### 💡 LOGISTICS SUGGESTIONS:")
                st.write(f"👉 **Split Cargo:** Proceed with **2 x 20GP** containers.")
                st.write(f"👉 **Optimization:** Hold approximately **{(total_wgt - 26000):,.2f} kg** to use **1 x 20GP**.")
                st.markdown('</div>', unsafe_allow_html=True)
                best_con = "20GP" # Visualization පෙන්වීමට default එකක්
            else:
                best_con = next((n for n, s in specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), "40HC")
                st.success(f"✅ Recommended Equipment: **{best_con}**")
                fill_p = (total_cbm / specs[best_con]["vol"]) * 100
                st.progress(min(fill_p/100, 1.0))
                st.write(f"**Utilization:** {fill_p:.1f}%")

            # --- ADVANCED 3D CONTAINER VIEW ---
            st.markdown("<p class='section-header'>3. ADVANCED 3D CARGO PLACEMENT MAP</p>", unsafe_allow_html=True)
            
            # කන්ටේනරයේ සැබෑ සීමාවන්
            L_lim, W_lim, H_lim = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
            
            fig = go.Figure()
            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3', '#FECB52']
            
            # 1. කන්ටේනරයේ යකඩ රාමුව (Wireframe) - "නිකන් කොටුවක් නෙවෙයි"
            fig.add_trace(go.Scatter3d(
                x=[0, L_lim, L_lim, 0, 0, 0, L_lim, L_lim, 0, 0, L_lim, L_lim, L_lim, L_lim, 0, 0],
                y=[0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, 0, 0, 0, W_lim, W_lim, W_lim, W_lim],
                z=[0, 0, 0, 0, 0, H_lim, H_lim, H_lim, H_lim, H_lim, H_lim, 0, 0, H_lim, H_lim, 0],
                mode='lines', line=dict(color='#2c3e50', width=6), name=f'{best_con} Frame'
            ))

            # 2. Cargo Color Key
            st.write("**📦 Cargo Color Key:**")
            key_cols = st.columns(len(df))
            for i, (idx, row) in enumerate(df.iterrows()):
                clr = colors[i % len(colors)]
                key_cols[i].markdown(f'<div style="background-color:{clr}; width:15px; height:15px; display:inline-block; border-radius:2px;"></div> {row["Cargo_Name"]}', unsafe_allow_html=True)
                
                # භාණ්ඩයේ 3D රූපය (Mesh)
                fig.add_trace(go.Mesh3d(
                    x=[10, 10, 10+row['Length_cm'], 10+row['Length_cm'], 10, 10, 10+row['Length_cm'], 10+row['Length_cm']],
                    y=[10, 10+row['Width_cm'], 10+row['Width_cm'], 10, 10, 10+row['Width_cm'], 10+row['Width_cm'], 10],
                    z=[0, 0, 0, 0, row['Height_cm'], row['Height_cm'], row['Height_cm'], row['Height_cm']],
                    color=clr, opacity=0.8, name=row['Cargo_Name']
                ))

            # 3. ප්‍රස්ථාරයේ අක්ෂයන් සහ උස හරියටම පාලනය කිරීම
            fig.update_layout(
                scene=dict(
                    xaxis=dict(range=[-50, L_lim+50], title="Length (cm)"),
                    yaxis=dict(range=[-50, W_lim+50], title="Width (cm)"),
                    zaxis=dict(range=[0, H_lim], title="Height (cm)"), # මෙහිදී උස 230 හෝ 265 ට හරියටම සීමා වේ
                    aspectmode='manual',
                    aspectratio=dict(x=2.5, y=1, z=1) # දිගටි Professional පෙනුම
                ),
                margin=dict(l=0, r=0, b=0, t=0)
            )
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Planner v10.0 | Strategic Intelligence | By Sudath</p>", unsafe_allow_html=True)
