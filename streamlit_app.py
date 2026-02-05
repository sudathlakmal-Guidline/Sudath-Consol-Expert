import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG ---
st.set_page_config(page_title="SMART CONSOL PLANNER - SUDATH", layout="wide")

# ප්‍රධාන නම වෙනස් කිරීම
st.markdown('<h1 style="background-color:#004a99; color:white; text-align:center; padding:15px; border-radius:10px;">🚢 SMART CONSOL PLANNER - POWERED BY SUDATH</h1>', unsafe_allow_html=True)

# 2. දත්ත ඇතුළත් කිරීමේ වගුව
df_input = st.data_editor(pd.DataFrame([
    {"Cargo": "Shipment_1", "L": 120, "W": 100, "H": 100, "Qty": 5, "Weight_kg": 500},
    {"Cargo": "Shipment_2", "L": 115, "W": 115, "H": 115, "Qty": 10, "Weight_kg": 1500}
]), num_rows="dynamic", use_container_width=True)

if st.button("🚀 GENERATE STACKED LOADING PLAN", use_container_width=True):
    df = df_input.dropna().copy()
    
    if not df.empty:
        # --- 🔴 1. GROSS WEIGHT එකතුව (Total Sum) ---
        # එක් එක් පේළියේ බර වෙන වෙනම ගණනය කර (Weight * Qty) එහි එකතුව ලබා ගැනීම
        df['Row_Total_Weight'] = df['Weight_kg'] * df['Qty']
        final_gross_weight = df['Row_Total_Weight'].sum()
        
        # --- 🔴 2. HEAVY ON BOTTOM (Sorting by Weight) ---
        # බර වැඩිම අයිතම ලැයිස්තුවේ මුලට ගන්නා නිසා ඒවා පතුලටම ඇසිරේ
        df_sorted = df.sort_values(by='Weight_kg', ascending=False)
        
        # පරිමාව (Volume)
        df['Row_CBM'] = (df['L'] * df['W'] * df['H'] * df['Qty']) / 1000000
        total_cbm = df['Row_CBM'].sum()
        
        # Metrics පෙන්වීම
        m1, m2, m3 = st.columns(3)
        m1.metric("TOTAL GROSS WEIGHT", f"{final_gross_weight:,.0f} kg")
        m2.metric("TOTAL VOLUME", f"{total_cbm:.2f} CBM")
        m3.metric("UTILIZATION %", f"{(total_cbm/31)*100:.1f}%")

        # --- 🚢 3. SMART 3D STACKING ALGORITHM ---
        fig = go.Figure()
        L_max, W_max, H_max = 585, 230, 230
        
        x_p, y_p, z_p = 0, 0, 0
        max_h_layer = 0
        max_w_row = 0

        # වර්ණ කේත
        colors = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd']

        for idx, row in df_sorted.reset_index().iterrows():
            l, w, h = row['L'], row['W'], row['H']
            clr = colors[idx % len(colors)]
            
            for _ in range(int(row['Qty'])):
                # පළල පිරුණොත්
                if y_p + w > W_max:
                    y_p = 0
                    x_p += max_w_row
                    max_w_row = 0
                
                # දිග පිරුණොත් (ඊළඟ තට්ටුව - Layer)
                if x_p + l > L_max:
                    x_p = 0
                    y_p = 0
                    z_p += max_h_layer
                    max_h_layer = 0
                
                # 3D Box ඇඳීම
                if z_p + h <= H_max:
                    fig.add_trace(go.Mesh3d(
                        x=[x_p, x_p, x_p+l, x_p+l, x_p, x_p, x_p+l, x_p+l],
                        y=[y_p, y_p+w, y_p+w, y_p, y_p, y_p+w, y_p+w, y_p],
                        z=[z_p, z_p, z_p, z_p, z_p+h, z_p+h, z_p+h, z_p+h],
                        color=clr, opacity=0.8, alphahull=0,
                        name=f"{row['Cargo']} ({row['Weight_kg']}kg)"
                    ))
                    
                    y_p += w
                    max_w_row = max(max_w_row, l)
                    max_h_layer = max(max_h_layer, h)

        # Container Frame
        fig.add_trace(go.Scatter3d(
            x=[0,L_max,L_max,0,0,0,L_max,L_max,0,0,L_max,L_max,L_max,L_max,0,0],
            y=[0,0,W_max,W_max,0,0,0,W_max,W_max,0,0,0,W_max,W_max,W_max,W_max],
            z=[0,0,0,0,0,H_max,H_max,H_max,H_max,H_max,H_max,0,0,H_max,H_max,0],
            mode='lines', line=dict(color='black', width=3), showlegend=False
        ))

        fig.update_layout(
            scene=dict(aspectmode='data', xaxis_title='L', yaxis_title='W', zaxis_title='H'),
            margin=dict(l=0,r=0,b=0,t=0)
        )
        st.plotly_chart(fig, use_container_width=True)

# පතුලේ ඇති නම
st.markdown("<hr><center>© 2026 SMART CONSOL PLANNER - POWERED BY SUDATH</center>", unsafe_allow_html=True)
