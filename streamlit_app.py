import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Advanced Consol Planner - Sudath", layout="wide", page_icon="🚢")

# 2. Professional UI Styling
st.markdown("""
    <style>
    .header-style { background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; }
    .suggestion-card { background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 20px; border-radius: 10px; margin: 15px 0; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

# 3. ස්ථාවර කන්ටේනර් දත්ත (Lock Dimensions)
specs = {
    "20GP": {"L": 585, "W": 230, "H": 230, "vol": 31.5, "kg": 26000},
    "40GP": {"L": 1200, "W": 230, "H": 230, "vol": 58.0, "kg": 26000},
    "40HC": {"L": 1200, "W": 230, "H": 265, "vol": 70.0, "kg": 28000}
}

# --- Main Header ---
st.markdown('<div class="header-style"><h1>🚢 SMART CONSOL & OOG PLANNER</h1><p>Strategic Freight Intelligence • By Sudath</p></div>', unsafe_allow_html=True)

# Data Editor
st.markdown("### 1. MANIFEST DATA ENTRY")
df = st.data_editor(pd.DataFrame(columns=["Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"]), num_rows="dynamic", key="final_sudath_v9")

if st.button("GENERATE ADVANCED LOADING PLAN", type="primary"):
    if not df.empty:
        df = df.dropna().apply(pd.to_numeric, errors='ignore')
        total_wgt = df['Weight_kg'].sum()
        total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()

        # --- බර සහ යෝජනා (Weight Logic) ---
        if total_wgt > 26000:
            st.markdown(f'<div class="suggestion-card">⚠️ <b>බර සීමාව ඉක්මවා ඇත:</b> මුළු බර {total_wgt:,.0f} kg කි. <br> 💡 20GP/40GP සීමාව 26,000 kg බැවින් මෙය <b>2 x 20GP</b> ලෙස බෙදා පටවන්න.</div>', unsafe_allow_html=True)
            best_con = "20GP" # Default frame for visualization
        else:
            best_con = next((n for n, s in specs.items() if total_cbm <= s["vol"] and total_wgt <= s["kg"]), "40HC")
            st.success(f"✅ Recommended Equipment: {best_con}")

        # --- Advanced 3D Container Wireframe Logic ---
        L_max, W_max, H_max = specs[best_con]["L"], specs[best_con]["W"], specs[best_con]["H"]
        
        fig = go.Figure()
        
        # කන්ටේනරයේ පිටත රාමුව (Wireframe) ඇඳීම - මින් මතු මෙය "නිකන් කොටුවක්" නොවේ
        fig.add_trace(go.Scatter3d(
            x=[0, L_max, L_max, 0, 0, 0, L_max, L_max, 0, 0, L_max, L_max, L_max, L_max, 0, 0],
            y=[0, 0, W_max, W_max, 0, 0, 0, W_max, W_max, 0, 0, 0, W_max, W_max, W_max, W_max],
            z=[0, 0, 0, 0, 0, H_max, H_max, H_max, H_max, H_max, H_max, 0, 0, H_max, H_max, 0],
            mode='lines', line=dict(color='black', width=5), name='Container Frame'
        ))

        # භාණ්ඩ ඇසිරීම
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
        for idx, row in df.iterrows():
            clr = colors[idx % len(colors)]
            # මෙහිදී සරලව පළමු පෙට්ටිය පෙන්වයි (Professional packing logic can be added)
            fig.add_trace(go.Mesh3d(
                x=[10, 10, 10+row['Length_cm'], 10+row['Length_cm'], 10, 10, 10+row['Length_cm'], 10+row['Length_cm']],
                y=[10, 10+row['Width_cm'], 10+row['Width_cm'], 10, 10, 10+row['Width_cm'], 10+row['Width_cm'], 10],
                z=[0, 0, 0, 0, row['Height_cm'], row['Height_cm'], row['Height_cm'], row['Height_cm']],
                color=clr, opacity=0.7, name=row['Cargo_Name']
            ))

        # ප්‍රස්ථාරයේ අක්ෂයන් (Axes) පාලනය
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[-50, L_max+50], title="Length"),
                yaxis=dict(range=[-50, W_max+50], title="Width"),
                zaxis=dict(range=[0, H_max+20], title="Height"), # මෙහිදී උස 230/265 ට හරියටම සීමා වේ
                aspectmode='manual',
                aspectratio=dict(x=2, y=0.8, z=0.8)
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        st.plotly_chart(fig, use_container_width=True)
