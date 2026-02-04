import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# පද්ධතියේ මූලික සැකසුම් (Page Configuration)
st.set_page_config(page_title="Smart Consol Planner", layout="wide", page_icon="🚢")

# වෘත්තීය මට්ටමේ පෙනුමක් ලබා දීම සඳහා CSS (Custom UI Styling)
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-bottom: 4px solid #002b5e;
    }
    .header-style {
        background: linear-gradient(135deg, #002b5e 0%, #004a99 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .section-header {
        color: #002b5e;
        border-left: 5px solid #FFCC00;
        padding-left: 10px;
        margin: 25px 0px 15px 0px;
        font-weight: bold;
        font-size: 22px;
    }
    .card-bg {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ආරක්ෂිත ඇතුළුවීම (Password Logic) ---
if "password_correct" not in st.session_state:
    st.markdown("<div style='text-align:center; margin-top:100px;'>", unsafe_allow_html=True)
    st.title("🚢 Smart Consol Planner")
    st.subheader("🔐 Access Control")
    pwd = st.text_input("Enter your unique access key:", type="password")
    if st.button("Authenticate"):
        if pwd == "sudath123":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("🚫 Access Key Invalid.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ප්‍රධාන Header එක (Modern Header) ---
st.markdown(f"""
    <div class="header-style">
        <h1 style="margin:0; font-size: 42px; letter-spacing: 2px; font-weight: 800;">SMART CONSOL PLANNER</h1>
        <p style="font-size:20px; opacity: 0.9; margin-top:10px; letter-spacing: 1px;">
            Strategic Freight Optimization & Intelligence • By Sudath
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- වම් පස මෙනුව (Navigation Sidebar) ---
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION CENTER")
    app_mode = st.radio("Select Operational Module:", 
                        ["📦 Consolidation Planner", "🏗️ OOG Cargo Assessment", "☣️ IMDG Segregation"])
    st.divider()
    st.markdown("### ⚙️ SYSTEM SETTINGS")
    is_heavy = st.toggle("Enable 40HC Heavy Duty (28,000kg)")
    st.divider()
    if st.button("Logout of System"):
        del st.session_state["password_correct"]
        st.rerun()

# Container Specification Database
container_specs = {
    "20GP": {"vol": 31.5, "kg": 26000, "L": 585, "W": 230, "H": 230},
    "40GP": {"vol": 58.0, "kg": 26000, "L": 1200, "W": 230, "H": 230},
    "40HC": {"vol": 70.0, "kg": 28000 if is_heavy else 26000, "L": 1200, "W": 230, "H": 265}
}

if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>1. MANIFEST DATA INPUT</p>", unsafe_allow_html=True)
    
    # දත්ත ඇතුළත් කරන වගුව (සියලුම අවශ්‍යතා සහිතව)
    init_df = pd.DataFrame(columns=[
        "Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"
    ])
    df = st.data_editor(init_df, num_rows="dynamic", key="final_planner_sudath")

    if st.button("EXECUTE 3D PLANNING SIMULATION", type="primary"):
        if not df.empty:
            # දත්ත පිරිසිදු කිරීම සහ ගණනය කිරීම
            df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
            df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
            
            df['CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
            total_qty = df['Quantity'].sum()
            total_wgt = df['Weight_kg'].sum()
            total_cbm = df['CBM'].sum()

            # --- 📊 GRAND TOTAL SUMMARY ---
            st.markdown("<p class='section-header'>2. CONSOLIDATION ANALYTICS</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Packages", f"{int(total_qty)} Pcs")
            col2.metric("Gross Weight", f"{total_wgt:,.2f} kg")
            col3.metric("Total Volume", f"{total_cbm:.3f} CBM")

            # හොඳම කන්ටේනරය තෝරා ගැනීම
            best_con = next((name for name, s in container_specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), None)

            if best_con:
                max_v = container_specs[best_con]["vol"]
                fill_p = min((total_cbm / max_v) * 100, 100)
                rem_cbm = max_v - total_cbm

                st.info(f"✅ Recommended Equipment: **{best_con}** | Space Utilization: **{fill_p:.1f}%**")
                st.progress(fill_p / 100)
                st.write(f"**Remaining Capacity:** `{rem_cbm:.3f} CBM` available.")

                # --- 🧊 3D VISUALIZATION ENGINE ---
                st.markdown("<p class='section-header'>3. 3D CARGO PLACEMENT MAP</p>", unsafe_allow_html=True)
                fig = go.Figure()
                colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3', '#FECB52', '#FF97FF']
                curr_x, curr_y, curr_z = 0, 0, 0
                L_lim, W_lim, H_lim = container_specs[best_con]["L"], container_specs[best_con]["W"], container_specs[best_con]["H"]
                
                legend_list = []

                for idx, row in df.iterrows():
                    clr = colors[idx % len(colors)]
                    legend_list.append({"name": row['Cargo_Name'], "color": clr, "qty": row['Quantity'], "cbm": row['CBM']})
                    
                    for n in range(int(row['Quantity'])):
                        dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                        
                        # Smart Rotation Logic
                        if row.get('Rotation_Allowed', True) and (curr_x + dx > L_lim):
                            dx, dy = dy, dx # Rotate if it fits better

                        fig.add_trace(go.Mesh3d(
                            x=[curr_x, curr_x, curr_x+dx, curr_x+dx, curr_x, curr_x, curr_x+dx, curr_x+dx],
                            y=[curr_y, curr_y+dy, curr_y+dy, curr_y, curr_y, curr_y+dy, curr_y+dy, curr_y],
                            z=[curr_z, curr_z, curr_z, curr_z, curr_z+dz, curr_z+dz, curr_z+dz, curr_z+dz],
                            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                            color=clr, opacity=0.7, name=f"{row['Cargo_Name']} ({n+1})"
                        ))
                        
                        # Placement Logic
                        curr_x += dx
                        if curr_x + dx > L_lim:
                            curr_x = 0
                            curr_y += dy
                        if curr_y + dy > W_lim:
                            curr_y = 0
                            curr_z += dz

                fig.update_layout(
                    scene=dict(
                        xaxis=dict(title='Length (X)', range=[0, L_lim]),
                        yaxis=dict(title='Width (Y)', range=[0, W_lim]),
                        zaxis=dict(title='Height (Z)', range=[0, H_lim]),
                        aspectmode='manual', aspectratio=dict(x=2, y=0.5, z=0.5)
                    ),
                    margin=dict(l=0, r=0, b=0, t=0)
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- 🎨 PROFESSIONAL COLOR IDENTIFICATION KEY ---
                st.markdown("<p class='section-header'>4. CARGO IDENTIFICATION KEY</p>", unsafe_allow_html=True)
                key_html = """
                <table style='width:100%; border-collapse: collapse; border-radius: 10px; overflow: hidden; font-family: sans-serif;'>
                    <tr style='background-color: #002b5e; color: white; text-align: left;'>
                        <th style='padding: 15px;'>Color Indicator</th>
                        <th style='padding: 15px;'>Cargo Name</th>
                        <th style='padding: 15px;'>Unit Quantity</th>
                        <th style='padding: 15px;'>Total Volume (CBM)</th>
                    </tr>
                """
                for item in legend_list:
                    key_html += f"""
                    <tr style='border-bottom: 1px solid #ddd; background-color: white;'>
                        <td style='padding: 15px;'><div style='width: 60px; height: 25px; background-color: {item['color']}; border-radius: 5px; border: 1px solid #999;'></div></td>
                        <td style='padding: 15px; font-weight: bold;'>{item['name']}</td>
                        <td style='padding: 15px;'>{int(item['qty'])} Pcs</td>
                        <td style='padding: 15px;'>{item['cbm']:.3f} CBM</td>
                    </tr>
                    """
                key_html += "</table>"
                st.markdown(key_html, unsafe_allow_html=True)
                
            else:
                st.error("❌ CRITICAL ERROR: Total shipment exceeds all standard container payload or volume limits. Please split the cargo.")

    elif app_mode == "🏗️ OOG Cargo Assessment":
        st.subheader("Out-of-Gauge (OOG) Assessment Module")
        st.info("Coming Soon: Precision analysis for Flat Rack and Open Top loading.")

    elif app_mode == "☣️ IMDG Segregation":
        st.subheader("Dangerous Goods (DG) Segregation Module")
        st.warning("Ensure compatibility based on IMDG Class before consolidation.")

# Footer
st.markdown("<br><hr><p style='text-align: center; color: gray;'>Smart Consol Planner v3.0 | Secure Intelligence System</p>", unsafe_allow_html=True)
