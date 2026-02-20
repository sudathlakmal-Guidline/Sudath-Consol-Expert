import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai
import io

# --- 1. CONFIG & HIGH SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Powered by Sudath", layout="wide")

API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Configuration Error: {e}")

# --- 2. DATABASE & AUTH (ඔබේ මුල් කේතය එලෙසම තබා ඇත) ---
# ... [මෙහි ඇති Login සහ Database කොටස් ඔබ ලබා දුන් මුල් කේතයම වේ]

# --- 4. MAIN INTERFACE ---
st.markdown(f'<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - Powered by Sudath</h1>', unsafe_allow_html=True)

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

with st.sidebar:
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

# --- CARGO ENTRY ---
st.subheader(f"📊 {c_type} Cargo Entry")
init_data = [
    {"Cargo": "Heavy_Box", "L": 200, "W": 200, "H": 100, "Qty": 1, "Gross_Weight_kg": 5000, "Can_Rotate": False},
    {"Cargo": "Cartons", "L": 60, "W": 40, "H": 30, "Qty": 100, "Gross_Weight_kg": 3000, "Can_Rotate": True},
    {"Cargo": "Pallets", "L": 115, "W": 115, "H": 115, "Qty": 2, "Gross_Weight_kg": 2000, "Can_Rotate": False}
]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df.dropna().copy()
    if not clean_df.empty:
        total_vol = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']).sum() / 1000000
        total_weight = clean_df['Gross_Weight_kg'].sum()
        
        # 3D Visualization Logic
        fig = go.Figure()
        # ස්ථාවර පාට 3ක් ලබා දීම (Blue, Orange, Green)
        colors_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        L_max, W_max, H_max = specs['L'], specs['W'], specs['H']
        
        # Container Wireframe
        fig.add_trace(go.Scatter3d(x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0], y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max], z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0], mode='lines', line=dict(color='black', width=2), showlegend=False))
        
        cx, cy, cz, layer_h = 0, 0, 0, 0
        shipment_colors = {} # PDF එක සඳහා පාට ගබඩා කර ගැනීම
        
        for idx, row in clean_df.reset_index().iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors_list[idx % len(colors_list)]
            shipment_colors[row['Cargo']] = clr
            
            for _ in range(int(row['Qty'])):
                # Rotation Logic: ඉඩ මදි නම් හරවා බැලීම
                if row['Can_Rotate'] and (cx + l > L_max):
                    l, w = w, l 
                
                if cx + l > L_max: cx = 0; cy += w
                if cy + w > W_max: cy = 0; cz += layer_h; layer_h = 0
                
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(x=[cx,cx,cx+l,cx+l,cx,cx,cx+l,cx+l], y=[cy,cy+w,cy+w,cy,cy,cy+w,cy+w,cy], z=[cz,cz,cz,cz,cz+h,cz+h,cz+h,cz+h], color=clr, opacity=0.8, alphahull=0, name=row['Cargo'], showlegend=True))
                    cx += l
                    layer_h = max(layer_h, h)
        
        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF Generation ---
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_fill_color(0, 74, 153); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 22); pdf.text(40, 25, "SMART CONSOL LOADING REPORT")
        
        # Summary
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12); pdf.ln(45)
        pdf.cell(0, 10, f"Summary: {total_vol:.2f} CBM | Total Gross Weight: {total_weight} kg", 0, 1)
        
        # --- COLOR KEY CHART (PDF එකේ 3D එකට උඩින්) ---
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, "COLOR KEY / SHIPMENT IDENTIFICATION:", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        for cargo_name, color_hex in shipment_colors.items():
            # පාට කොටුව ඇඳීම
            r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            pdf.set_fill_color(r, g, b)
            pdf.rect(10, pdf.get_y() + 1, 5, 5, 'F')
            pdf.set_x(20)
            pdf.cell(0, 7, f"- {cargo_name}", 0, 1)

        # 3D පින්තූරය ඇතුළත් කිරීම
        try:
            img_bytes = fig.to_image(format="png", width=800, height=500)
            pdf.image(io.BytesIO(img_bytes), x=10, y=pdf.get_y() + 5, w=190)
        except:
            pdf.ln(10); pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, "Note: 3D Plan capture failed. Please screenshot the app view.", 0, 1)

        # Download Link
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Sudath_Consol_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD FINAL REPORT (WITH COLOR CHART)</a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<center>© 2026 SMART CONSOL PRO - Powered by Sudath</center>", unsafe_allow_html=True)
