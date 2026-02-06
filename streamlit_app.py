import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- 1. CONFIG & UPDATED SPECS ---
st.set_page_config(page_title="SMART CONSOL PLANNER - SUDATH PRO", layout="wide")

# බහාලුම් මානයන් සහ සීමාවන් (ඔබ ලබා දුන් පරිදි)
CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

# --- 2. LOGIN LOGIC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><h2 style='text-align: center;'>🚢 SMART CONSOL SYSTEM - SUDATH</h2>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        u = st.text_input("User ID", key="user_id")
        p = st.text_input("Password", type="password", key="password")
        if st.button("LOGIN", use_container_width=True):
            if u.strip().lower() == "sudath" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# --- 3. MAIN APP ---
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PLANNER PRO - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.success("✅ Logged in: Sudath")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    st.info(f"Limits: {specs['MAX_CBM']} CBM | {specs['MAX_KG']} KG")
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

st.subheader(f"📊 {c_type} Cargo Entry & Smart Validation")

# දත්ත ඇතුළත් කිරීමේ වගුව
# මෙහි 'Weight_kg' ලෙස හඳුන්වන්නේ මුළු shipment එකේ බරයි.
init_data = [
    {"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500, "Can_Rotate": True},
    {"Cargo": "PKG_002", "L": 115, "W": 115, "H": 115, "Qty": 10, "Weight_kg": 1500, "Can_Rotate": False}
]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        
        # බර අනුව පිළිවෙළට සැකසීම (Heaviest at the bottom)
        clean_df = clean_df.sort_values(by='Weight_kg', ascending=False)
        
        # 1. Individual Package Validation (OOG Check)
        rejects = []
        for idx, row in clean_df.iterrows():
            if row['H'] > specs['H'] or row['L'] > specs['L'] or row['W'] > specs['W']:
                rejects.append(f"⚠️ {row['Cargo']} exceed container dimensions. Suggestion: Breakbulk or Flatrack.")
            
        if rejects:
            for r in rejects: st.warning(r)
            st.error("Please adjust cargo to proceed.")
            st.stop()

        # --- බර සහ පරිමාව ගණනය කිරීම (ඔබ ඉල්ලා සිටි පරිදි සෘජු එකතුව පමණි) ---
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = clean_df['Weight_kg'].sum() # Shipment weights වල එකතුව පමණි
        util_pct = (total_vol / specs['MAX_CBM']) * 100

        # Overload Suggestions (Split shipment logic)
        if total_vol > specs['MAX_CBM'] or total_weight > specs['MAX_KG']:
            st.error(f"⚠️ {c_type} Overloaded! Utilization: {util_pct:.1f}% | Total Weight: {total_weight:,.0f} kg")
            st.subheader("💡 Solutions & Suggestions:")
            vol_containers = int((total_vol // specs['MAX_CBM']) + 1)
            wt_containers = int((total_weight // specs['MAX_KG']) + 1)
            needed = max(vol_containers, wt_containers)
            st.write(f"* **Split Shipment:** Suggesting **{needed} x {c_type}** containers for this load.")
            st.stop()

        # Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{total_vol:.2f} CBM")
        m2.metric("Container Capacity", f"{specs['MAX_CBM']} CBM")
        m3.metric("Utilization", f"{util_pct:.1f}%")
        m4.metric("Total Gross Weight", f"{total_weight:,.0f} kg")

        # 3D Visualization
        fig = go.Figure()
        L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
        fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))

        cx, cy, cz, layer_h = 0, 0, 0, 0
        color_map = [{'hex': '#1f77b4', 'rgb': (31, 119, 180)}, {'hex': '#ff7f0e', 'rgb': (255, 127, 14)}, {'hex': '#2ca02c', 'rgb': (44, 160, 44)}, {'hex': '#d62728', 'rgb': (214, 39, 40)}]

        for idx, row in clean_df.reset_index().iterrows():
            l, w, h = row['L'], row['W'], row['H']
            if row['Can_Rotate'] and (cx + l > L_max): l, w = w, l 
            
            clr = color_map[idx % len(color_map)]['hex']
            for _ in range(int(row['Qty'])):
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo']))
                    cx += l
                    layer_h = max(layer_h, h)

        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF REPORT ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_y(12)
        pdf.cell(190, 10, 'SMART CONSOL LOADING REPORT', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(190, 8, f'Container: {c_type} | Total Weight: {total_weight:,.0f} kg', 0, 1, 'C')
        
        pdf.ln(25); pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12); pdf.cell(100, 10, "Cargo Loading Details", 0, 1)
        
        pdf.set_fill_color(200, 200, 200); pdf.set_font("Arial", 'B', 10)
        cols = [("Color", 15), ("Cargo", 45), ("Qty", 15), ("Dims (cm)", 55), ("Shipment Weight", 45)]
        for text, width in cols: pdf.cell(width, 10, text, 1, 0, 'C', True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        for idx, r in clean_df.iterrows():
            rgb = color_map[list(clean_df.index).index(idx) % len(color_map)]['rgb']
            pdf.set_fill_color(*rgb); pdf.cell(15, 10, '', 1, 0, 'C', True)
            pdf.cell(45, 10, str(r['Cargo']), 1)
            pdf.cell(15, 10, str(int(r['Qty'])), 1, 0, 'C')
            pdf.cell(55, 10, f"{r['L']}x{r['W']}x{r['H']}", 1, 0, 'C')
            pdf.cell(45, 10, f"{r['Weight_kg']:,} kg", 1, 1, 'C')

        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Consol_Report_Sudath.pdf" style="display:inline-block; padding:15px; background-color:#28a745; color:white; border-radius:10px; text-decoration:none; font-weight:bold; width:100%; text-align:center;">📥 DOWNLOAD FINAL LOADING REPORT (PDF)</a>', unsafe_allow_html=True)

st.markdown("<br><hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH PRO</center>", unsafe_allow_html=True)
