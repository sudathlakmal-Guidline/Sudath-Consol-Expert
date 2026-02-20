import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai
import io

# --- 1. CONFIG ---
st.set_page_config(page_title="SMART CONSOL PRO - Sudath", layout="wide")

# --- 2. 3D PACKING LOGIC (නිවැරදිව ප්ලෑන් එක පෙන්වීමට) ---
def generate_3d_plan(df, container_specs):
    fig = go.Figure()
    colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA']
    x, y, z = 0, 0, 0
    max_h, max_w = 0, 0
    
    for idx, row in df.iterrows():
        l, w, h = row['L'], row['W'], row['H']
        clr = colors[idx % len(colors)]
        for _ in range(int(row['Qty'])):
            # සරල Tight Loading Logic
            if x + l > container_specs['L']:
                x = 0; y += max_w; max_w = 0
            if y + w > container_specs['W']:
                y = 0; z += max_h; max_h = 0
            
            if z + h <= container_specs['H']:
                # 3D Mesh එකක් ලෙස පෙට්ටිය ඇඳීම
                fig.add_trace(go.Mesh3d(
                    x=[x, x, x+l, x+l, x, x, x+l, x+l],
                    y=[y, y+w, y+w, y, y, y+w, y+w, y],
                    z=[z, z, z, z, z+h, z+h, z+h, z+h],
                    color=clr, opacity=0.8, alphahull=0, name=row['Cargo'], showlegend=True
                ))
                x += l
                max_h = max(max_h, h)
                max_w = max(max_w, w)
    
    fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    return fig

# --- 3. MAIN INTERFACE ---
st.markdown(f'<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - Powered by Sudath</h1>', unsafe_allow_html=True)

container_specs = {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0}

# Cargo Entry Table
df_input = st.data_editor(pd.DataFrame([{"Cargo": "PKG_001", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500}]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE VALIDATED 3D PLAN & REPORT", use_container_width=True):
    clean_df = df_input.dropna()
    if not clean_df.empty:
        # Metrics Display
        vol = (clean_df['L']*clean_df['W']*clean_df['H']*clean_df['Qty']).sum() / 1000000
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Volume", f"{vol:.2f} CBM")
        m2.metric("Utilization", f"{(vol/container_specs['MAX_CBM'])*100:.1f}%")
        m3.metric("Total Weight", f"{clean_df['Weight_kg'].sum()} kg")

        # 3D Visualization
        fig = generate_3d_plan(clean_df, container_specs)
        st.plotly_chart(fig, use_container_width=True)

        # PDF Fix (Image Capture Fail එක මඟහැරීමට)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 16)
        pdf.text(50, 25, "SMART CONSOL LOADING REPORT")
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 12)
        pdf.ln(45)
        pdf.cell(0, 10, f"Summary: {vol:.2f} CBM | Weight: {clean_df['Weight_kg'].sum()} kg", 0, 1)

        # 3D Plan එක PDF එකට ඇතුළත් කිරීමේ උත්සාහය
        try:
            img_bytes = fig.to_image(format="png", engine="kaleido")
            pdf.image(io.BytesIO(img_bytes), x=10, y=70, w=190)
        except Exception:
            # පින්තූරය fail වුවහොත් පණිවිඩයක් පෙන්වීම
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, "Note: 3D Plan capture failed. Please use screenshot of the app.", 0, 1)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Sudath_Consol_Report.pdf" style="display:block; padding:15px; background:#28a745; color:white; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none;">📥 DOWNLOAD FINAL REPORT</a>', unsafe_allow_html=True)
