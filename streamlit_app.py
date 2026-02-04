import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Smart Consol Planner", layout="wide", page_icon="🚢")

# Professional UI සඳහා CSS එකතු කිරීම
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
    }
    .section-header {
        color: #002b5e;
        border-left: 5px solid #FFCC00;
        padding-left: 10px;
        margin-top: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Password Logic ---
if "password_correct" not in st.session_state:
    st.markdown("<div style='text-align:center; margin-top:50px;'>", unsafe_allow_html=True)
    st.title("🔐 Secure Access")
    pwd = st.text_input("Please enter your access key:", type="password")
    if st.button("Authorize"):
        if pwd == "sudath123":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("Access Denied.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Professional Header ---
st.markdown(f"""
    <div class="header-style">
        <h1 style="margin:0; font-size: 36px; letter-spacing: 1px;">🚢 SMART CONSOL PLANNER</h1>
        <p style="font-size:18px; opacity: 0.8; margin-top:10px;">Strategic Freight Optimization & Intelligence • By Sudath</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with Icons
with st.sidebar:
    st.markdown("### 🛠️ NAVIGATION")
    app_mode = st.radio("Select Module:", ["📦 Consolidation Planner", "🏗️ OOG Assessment", "☣️ IMDG Segregation"])
    st.divider()
    is_heavy = st.toggle("40HC Heavy Duty Mode (28MT)")
    if st.button("Logout"):
        del st.session_state["password_correct"]; st.rerun()

# Container Database
specs = {
    "20GP": {"vol": 31.5, "kg": 26000, "L": 585, "W": 230, "H": 230},
    "40GP": {"vol": 58.0, "kg": 26000, "L": 1200, "W": 230, "H": 230},
    "40HC": {"vol": 70.0, "kg": 28000 if is_heavy else 26000, "L": 1200, "W": 230, "H": 265}
}

if app_mode == "📦 Consolidation Planner":
    st.markdown("<p class='section-header'>MANIFEST DATA ENTRY</p>", unsafe_allow_html=True)
    init_df = pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
    df = st.data_editor(init_df, num_rows="dynamic", key="planner_v14")

    if st.button("Execute 3D Loading Simulation"):
        if not df.empty:
            df = df.dropna().apply(pd.to_numeric, errors='ignore')
            df['CBM'] = (df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000
            
            t_qty, t_wgt, t_cbm = df['Quantity'].sum(), df['Weight_kg'].sum(), df['CBM'].sum()

            # --- Metrics Dashboard ---
            st.markdown("<p class='section-header'>LOADING SUMMARY</p>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Packages", f"{int(t_qty)} Pcs")
            m2.metric("Gross Weight", f"{t_wgt:,.0f} kg")
            m3.metric("Total Volume", f"{t_cbm:.2f} CBM")

            best = next((k for k, v in specs.items() if t_cbm <= v["vol"] and t_wgt <= v["kg"]), None)

            if best:
                util = min((t_cbm / specs[best]["vol"]) * 100, 100)
                st.info(f"💡 Recommended Equipment: **{best}** | Space Utilization: **{util:.1f}%**")
                st.progress(util / 100)

                # --- 3D Engine ---
                fig = go.Figure()
                colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']
                curr_x, curr_y, curr_z = 0, 0, 0
                legend_items = []

                for idx, row in df.iterrows():
                    clr = colors[idx % len(colors)]
                    legend_items.append({"name": row['Cargo_Name'], "clr": clr, "qty": row['Quantity'], "cbm": row['CBM']})
                    for _ in range(int(row['Quantity'])):
                        dx, dy, dz = row['Length_cm'], row['Width_cm'], row['Height_cm']
                        fig.add_trace(go.Mesh3d(
                            x=[curr_x, curr_x, curr_x+dx, curr_x+dx, curr_x, curr_x, curr_x+dx, curr_x+dx],
                            y=[curr_y, curr_y+dy, curr_y+dy, curr_y, curr_y, curr_y+dy, curr_y+dy, curr_y],
                            z=[curr_z, curr_z, curr_z, curr_z, curr_z+dz, curr_z+dz, curr_z+dz, curr_z+dz],
                            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                            color=clr, opacity=0.6, name=row['Cargo_Name']
                        ))
                        curr_x += dx
                        if curr_x + dx > specs[best]["L"]: curr_x, curr_y = 0, curr_y + dy
                        if curr_y + dy > specs[best]["W"]: curr_y, curr_z = 0, curr_z + dz

                fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=2, y=0.5, z=0.5)), margin=dict(l=0,r=0,b=0,t=0))
                st.plotly_chart(fig, use_container_width=True)

                # --- Professional Color Key ---
                st.markdown("<p class='section-header'>CARGO IDENTIFICATION KEY</p>", unsafe_allow_html=True)
                key_html = "<table style='width:100%; border-radius: 10px; overflow: hidden;'>"
                key_html += "<tr style='background-color: #002b5e; color: white;'><th>Color</th><th>Cargo Name</th><th>Qty</th><th>CBM</th></tr>"
                for item in legend_items:
                    key_html += f"<tr><td style='background-color:{item['clr']}; width: 40px;'></td><td style='padding:10px;'><b>{item['name']}</b></td><td>{int(item['qty'])}</td><td>{item['cbm']:.2f}</td></tr>"
                key_html += "</table>"
                st.markdown(key_html, unsafe_allow_html=True)
            else:
                st.error("⚠️ Payload Error: The shipment exceeds maximum container constraints.")
