import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධති සැකසුම් (System Settings)
st.set_page_config(page_title="SMART CONSOL PLANNER - POWERED BY SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 33.0},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 67.0},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 76.0}
}

st.markdown("""
    <style>
    .header { background: #004a99; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; }
    .stButton>button { background-color: #004a99; color: white; font-weight: bold; width: 100%; height: 3.5em; border-radius: 8px; }
    .nav-bar { background: #e1e4e8; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center; font-weight: bold; color: #004a99; }
    .color-box { display: inline-block; width: 18px; height: 18px; border-radius: 3px; margin-right: 8px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# 2. ආරක්ෂිත පිවිසුම (Login)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM</h2>", unsafe_allow_html=True)
    with st.columns([1,1.5,1])[1]:
        u = st.text_input("Username (sudath)")
        p = st.text_input("Password (admin123)", type="password")
        if st.button("LOGIN"):
            if u == "sudath" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
else:
    # 3. ප්‍රධාන පද්ධතිය (Main System)
    st.markdown('<div class="header"><h1>🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-bar">MENU: [📦 3D PLANNER] | [🏗️ OOG CHECK] | [🔄 AUTO-ROTATE]</div>', unsafe_allow_html=True)

    with st.sidebar:
        c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    specs = CONTAINERS[c_type]
    st.subheader(f"📊 {c_type} Entry & Smart Validation")
    
    # දත්ත ඇතුළත් කිරීමේ වගුව
    df = st.data_editor(pd.DataFrame([
        {"Cargo":"P1", "L":120, "W":100, "H":100, "Qty":10, "Allow_Rotate": True}
    ]), num_rows="dynamic", use_container_width=True)

    if st.button("GENERATE VALIDATED 3D PLAN"):
        clean_df = df.dropna()
        if clean_df.empty:
            st.warning("Please enter cargo data first.")
        else:
            errors = []
            shipments_to_check = []
            total_vol = 0
            
            # ධාරිතා සහ ප්‍රමාණය පරීක්ෂා කිරීම (Validation)
            for i, r in clean_df.iterrows():
                vol = (r['L'] * r['W'] * r['H'] * r['Qty']) / 1000000
                total_vol += vol
                shipments_to_check.append({"name": r['Cargo'], "vol": vol})
                
                # මානයන් පරීක්ෂාව (Dimension Check)
                if not r['Allow_Rotate']:
                    if r['L'] > specs['L'] or r['W'] > specs['W'] or r['H'] > specs['H']:
                        errors.append(f"❌ {r['Cargo']} exceeds {c_type} dimensions!")
                else:
                    # Rotate කරලත් ලොකුද බලන්න
                    if (r['L'] > specs['L'] and r['W'] > specs['L']) or r['H'] > specs['H']:
                        errors.append(f"❌ {r['Cargo']} is too large even with rotation!")

            # 1. CBM Overload පරීක්ෂාව
            if total_vol > specs['MAX_CBM']:
                st.error(f"🚨 OVERLOAD: Total {total_vol:.2f} CBM exceeds {c_type} limit ({specs['MAX_CBM']} CBM)!")
                sorted_list = sorted(shipments_to_check, key=lambda x: x['vol'], reverse=True)
                st.info(f"💡 **Sudath's Advice:** Please hold shipment **'{sorted_list[0]['name']}'** ({sorted_list[0]['vol']:.2f} CBM) to fit the rest.")
            
            # 2. Error නැත්නම් 3D එක අඳින්න
            elif errors:
                for e in errors: st.error(e)
            else:
                st.success(f"✅ {c_type} Validated! Total: {total_vol:.2f} CBM")
                
                fig = go.Figure()
                CL, CW, CH = specs['L'], specs['W'], specs['H']
                # Container Wireframe
                fig.add_trace(go.Scatter3d(x=[0,CL,CL,0,0,0,CL,CL,0,0,CL,CL,CL,CL,0,0], y=[0,0,CW,CW,0,0,0,CW,CW,0,0,0,CW,CW,CW,CW], z=[0,0,0,0,0,CH,CH,CH,CH,CH,CH,0,0,CH,CH,0], mode='lines', line=dict(color='black', width=3), showlegend=False))

                colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
                cx, cy, cz, mh = 0, 0, 0, 0
                legend_html = "<div style='margin-top:20px;'><b>🎨 Cargo Color Key:</b><br>"

                for i, r in clean_df.iterrows():
                    clr = colors[i % len(colors)]
                    legend_html += f'<span><span class="color-box" style="background:{clr}"></span>{r["Cargo"]}</span> &nbsp;&nbsp;'
                    l, w, h = r['L'], r['W'], r['H']
                    
                    for _ in range(int(r['Qty'])):
                        u_l, u_w = l, w
                        # Smart Rotation
                        if r['Allow_Rotate'] and (cx + l > CL) and (cx + w <= CL and l <= CW):
                            u_l, u_w = w, l
                        
                        if cx + u_l > CL: cx = 0; cy += u_w
                        if cy + u_w > CW: cy = 0; cz += mh; mh = 0
                        
                        if cz + h <= CH:
                            fig.add_trace(go.Mesh3d(x=[cx,cx,cx+u_l,cx+u_l,cx,cx,cx+u_l,cx+u_l], y=[cy,cy+u_w,cy+u_w,cy,cy,cy+u_w,cy+u_w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.7, alphahull=0))
                            cx += u_l; mh = max(mh, h)

                fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(legend_html + "</div>", unsafe_allow_html=True)

st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
