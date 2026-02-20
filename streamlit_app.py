import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import sqlite3
from datetime import datetime
import google.generativeai as genai
import io
from PIL import Image

# --- 1. CONFIG & SECURITY ---
st.set_page_config(page_title="SMART CONSOL PRO - Sudath", layout="wide")

# (ඔබේ පැරණි API Key එක මෙහි ඇතුළත් කරන්න)
API_KEY = "AIzaSyC3olT0UFAGBy4GiLbARwv0eA6BIsKbkzQ" 
try:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except:
    pass

# CSS for Security
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# --- 2. CONTAINER SPECS ---
CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "MAX_CBM": 70.0, "MAX_KG": 26000}
}

# --- 3. MAIN APP ---
st.title("🚢 SMART CONSOL PRO - High Efficiency Edition")

with st.sidebar:
    st.subheader("Settings")
    c_type = st.selectbox("Select Container Type:", list(CONTAINERS.keys()))
    specs = CONTAINERS[c_type]

# Cargo Entry with Rotation Option
st.subheader("📦 Cargo Details Entry")
init_data = [
    {"Cargo": "Heavy Box", "L": 200, "W": 200, "H": 100, "Qty": 1, "Weight_kg": 5000, "Rotate": False},
    {"Cargo": "Cartons", "L": 60, "W": 40, "H": 30, "Qty": 100, "Weight_kg": 3000, "Rotate": True},
    {"Cargo": "Pallets", "L": 115, "W": 115, "H": 115, "Qty": 2, "Weight_kg": 2000, "Rotate": False}
]
df = st.data_editor(pd.DataFrame(init_data), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE PERFECT 3D LOADING PLAN", use_container_width=True):
    # Calculations
    total_vol = (df['L'] * df['W'] * df['H'] * df['Qty']).sum() / 1000000
    total_weight = (df['Weight_kg']).sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Volume", f"{total_vol:.2f} CBM")
    col2.metric("Utilization", f"{(total_vol/specs['MAX_CBM'])*100:.1f}%")
    col3.metric("Total Weight", f"{total_weight} kg")

    # 3D Visualization Logic
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Simple Packing Logic (Tight Fit)
    curr_x, curr_y, curr_z = 0, 0, 0
    max_h_in_row = 0
    
    for idx, row in df.iterrows():
        clr = colors[idx % len(colors)]
        for _ in range(int(row['Qty'])):
            l, w, h = row['L'], row['W'], row['H']
            
            # Rotation logic if space is tight
            if row['Rotate'] and (curr_x + l > specs['L']):
                l, w = w, l 

            if curr_x + l > specs['L']:
                curr_x = 0
                curr_y += w
            if curr_y + w > specs['W']:
                curr_y = 0
                curr_z += max_h_in_row
                max_h_in_row = 0
            
            if curr_z + h <= specs['H']:
                fig.add_trace(go.Mesh3d(
                    x=[curr_x, curr_x, curr_x+l, curr_x+l, curr_x, curr_x, curr_x+l, curr_x+l],
                    y=[curr_y, curr_y+w, curr_y+w, curr_y, curr_y, curr_y+w, curr_y+w, curr_y],
                    z=[curr_z, curr_z, curr_z, curr_z, curr_z+h, curr_z+h, curr_z+h, curr_z+h],
                    color=clr, opacity=0.8, alphahull=0, name=row['Cargo']
                ))
                curr_x += l
                max_h_in_row = max(max_h_in_row, h)

    fig.update_layout(scene=dict(aspectmode='data'), title="3D Loading Optimization View")
    st.plotly_chart(fig, use_container_width=True)

    # --- PDF REPORT GENERATION WITH IMAGE ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "SMART CONSOL LOADING REPORT", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Container: {c_type} | Volume: {total_vol:.2f} CBM | Weight: {total_weight} kg", ln=True)
    
    # Save chart as image for PDF
    img_bytes = fig.to_image(format="png", width=800, height=500)
    img_io = io.BytesIO(img_bytes)
    img = Image.open(img_io)
    img.save("temp_3d_plan.png")
    
    pdf.image("temp_3d_plan.png", x=10, y=50, w=190)
    
    # Color Legend in PDF
    pdf.set_y(160)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Color Legend:", ln=True)
    pdf.set_font("Arial", '', 10)
    for idx, row in df.iterrows():
        pdf.cell(200, 8, f"- {row['Cargo']}: (Shown in Plot)", ln=True)

    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Loading_Plan.pdf" style="text-decoration:none;"><button style="width:100%; background-color:#28a745; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold;">📥 DOWNLOAD FINAL PDF REPORT WITH 3D PLAN</button></a>', unsafe_allow_html=True)
