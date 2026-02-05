import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG ---
st.set_page_config(page_title="SMART CONSOL PRO - SUDATH", layout="wide")

CONTAINERS = {
    "20GP": {"L": 585, "W": 230, "H": 230, "MAX_CBM": 31.0, "MAX_KG": 28000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "MAX_CBM": 58.0, "MAX_KG": 28000}
}

st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:10px; border-radius:10px;">🚢 SMART CONSOL PRO - SUDATH VERSION</h1>', unsafe_allow_html=True)

# 1. දත්ත ඇතුළත් කිරීම (Default values with your shipment data)
df = st.data_editor(pd.DataFrame([
    {"Cargo":"Shipment_1", "L":120, "W":100, "H":100, "Qty":5, "Weight_kg": 500},
    {"Cargo":"Shipment_2", "L":115, "W":115, "H":115, "Qty":10, "Weight_kg": 1500}
]), num_rows="dynamic", use_container_width=True)

if st.button("GENERATE STACKED 3D PLAN & FINAL WEIGHT", use_container_width=True):
    clean_df = df.dropna().copy()
    
    if not clean_df.empty:
        # --- ✅ පේළියෙන් පේළියට බර ගණනය කිරීම (The Logic You Wanted) ---
        clean_df['Row_Total_Weight'] = clean_df['Weight_kg'] * clean_df['Qty']
        final_gross_weight = clean_df['Row_Total_Weight'].sum()
        
        # --- ✅ බර වැඩි බඩු මුලින්ම ඇසිරීම (Heaviest first for stability) ---
        # Weight_kg එකෙන් sort කරනවා, එවිට බර දේවල් මුලින්ම container එකට වැටෙනවා.
        clean_df = clean_df.sort_values(by='Weight_kg', ascending=False)
        
        # පරිමාව (Volume)
        clean_df['Row_CBM'] = (clean_df['L'] * clean_df['W'] * clean_df['H'] * clean_df['Qty']) / 1000000
        final_total_cbm = clean_df['Row_CBM'].sum()
        
        # Metrics පෙන්වීම
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Cargo Volume", f"{final_total_cbm:.2f} CBM")
        m2.metric("TOTAL GROSS WEIGHT", f"{final_gross_weight:,.0f} kg")
        m3.metric("Utilization %", f"{(final_total_cbm/31)*100:.1f}%")

        # --- 3D Visualization (True Stacking Logic) ---
        fig = go.Figure()
        cx, cy, cz, layer_h = 0, 0, 0, 0
        L_max, W_max, H_max = 585, 230, 230 # 20GP default
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for idx, row in clean_df.reset_index().iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors[idx % len(colors)]
            
            for _ in range(int(row['Qty'])):
                # පළල (Width) පිරුණු විට ඊළඟ පේළියට (Row) යන්න
                if cx + l > L_max:
                    cx = 0
                    cy += w
                
                # දිග (Length) පිරුණු විට ඊළඟ තට්ටුවට (Layer) යන්න
                if cy + w > W_max:
                    cy = 0
                    cx = 0
                    cz += layer_h
                    layer_h = 0
                
                # බඩු ඇසිරීම (Add Box to 3D)
                if cz + h <= H_max:
                    fig.add_trace(go.Mesh3d(
                        x=[cx, cx, cx+l, cx+l, cx, cx, cx+l, cx+l],
                        y=[cy, cy+w, cy+w, cy, cy, cy+w, cy+w, cy],
                        z=[cz, cz, cz, cz, cz+h, cz+h, cz+h, cz+h],
                        color=clr, opacity=0.8, alphahull=0,
                        name=row['Cargo']
                    ))
                    cx += l
                    layer_h = max(layer_h, h)

        fig.update_layout(
            scene=dict(
                xaxis=dict(title='Length (cm)', range=[0, 585]),
                yaxis=dict(title='Width (cm)', range=[0, 230]),
                zaxis=dict(title='Height (cm)', range=[0, 230]),
                aspectmode='manual',
                aspectratio=dict(x=2.5, y=1, z=1)
            ),
            margin=dict(l=0,r=0,b=0,t=0),
            title="SUDATH'S 3D LOADING PLAN (HEAVY CARGO ON BOTTOM)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please enter cargo details first!")
