import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# පද්ධතියේ මූලික සැකසුම්
st.set_page_config(page_title="Smart Consol & OOG Planner", layout="wide", page_icon="🏗️")

# Professional UI Styling
st.markdown("""
    <style>
    .header-style {
        background: linear-gradient(135deg, #021d38 0%, #0b4a8a 100%);
        padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;
    }
    .solution-card {
        background-color: #ffffff; padding: 20px; border-radius: 10px; 
        border-left: 10px solid #FFCC00; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .section-header { color: #002b5e; border-left: 5px solid #FFCC00; padding-left: 10px; margin: 25px 0px; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
    <div class="header-style">
        <h1 style="margin:0; font-size: 38px;">🚢 SMART CONSOL & OOG PLANNER</h1>
        <p style="font-size:18px; opacity: 0.9; margin-top:10px;">Strategic Freight Intelligence • By Sudath</p>
    </div>
    """, unsafe_allow_html=True)

# --- Data Input (Rotation Allowed සමඟ) ---
st.markdown("<p class='section-header'>1. MANIFEST & CARGO DATA ENTRY</p>", unsafe_allow_html=True)

# ඔබ ඉල්ලූ Rotation_Allowed තීරුව මෙහි ඇත
init_df = pd.DataFrame(columns=[
    "Cargo_Name", "Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg", "Rotation_Allowed"
])
df = st.data_editor(init_df, num_rows="dynamic", key="final_ultimate_planner")

if st.button("ANALYZE LOADING & OOG SOLUTION", type="primary"):
    if not df.empty:
        # දත්ත පිරිසිදු කිරීම (Errors වළක්වා ගැනීමට)
        df = df.dropna(subset=["Length_cm", "Width_cm", "Height_cm", "Quantity", "Weight_kg"])
        df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']] = df[['Length_cm', 'Width_cm', 'Height_cm', 'Quantity', 'Weight_kg']].apply(pd.to_numeric)
        
        # මුළු එකතුව පෙන්වීම
        total_cbm = ((df['Length_cm'] * df['Width_cm'] * df['Height_cm'] * df['Quantity']) / 1000000).sum()
        total_wgt = df['Weight_kg'].sum()
        
        st.markdown("<p class='section-header'>2. CONSOLIDATION & OOG ANALYTICS</p>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Total Shipment Volume", f"{total_cbm:.3f} CBM")
        m2.metric("Total Gross Weight", f"{total_wgt:,.2f} kg")

        for idx, row in df.iterrows():
            L, W, H, Wgt = row['Length_cm'], row['Width_cm'], row['Height_cm'], row['Weight_kg']
            rotate = row.get('Rotation_Allowed', 'YES')
            name = row['Cargo_Name']
            
            # --- OOG හඳුනාගැනීමේ Logic එක ---
            is_oog = False
            solution = ""
            
            # සාමාන්‍ය කන්ටේනර් පරීක්ෂාව (20GP සහ 40HC)
            fit_20 = (L <= 585 and W <= 230 and H <= 230 and Wgt <= 26000)
            fit_40 = (L <= 1200 and W <= 230 and H <= 265 and Wgt <= 28000)
            
            if fit_20: solution = "Standard 20GP Container"
            elif fit_40: solution = "Standard 40HC Container"
            else:
                is_oog = True
                # OOG වර්ගීකරණය සහ උපකරණ තෝරාගැනීම
                if Wgt > 45000 or L > 1600:
                    solution = "🚨 BREAKBULK (BB) - Heavy Lift Vessel required."
                elif L <= 1180 and W <= 350 and H <= 380:
                    solution = "💡 40ft FLAT RACK (FR) - Over-Width/Height Cargo."
                elif L > 1200 and L <= 1600:
                    solution = "💡 FLATBED / PLATFORM - Extra Long Cargo Solution."
                else:
                    solution = "💡 SPECIALIZED OOG EQUIPMENT"

            # --- Result Cards ---
            st.markdown(f"<div class='solution-card'>", unsafe_allow_html=True)
            st.subheader(f"📦 Item: {name}")
            if is_oog:
                st.error(f"**STATUS: OOG (Out-of-Gauge)** | Rotation Allowed: {rotate}")
            else:
                st.success(f"**STATUS: In-Gauge (Standard)** | Rotation Allowed: {rotate}")
            
            st.write(f"**RECOMMENDED EQUIPMENT:** {solution}")
            st.markdown("</div>", unsafe_allow_html=True)

        # 3D Visual Preview (භාණ්ඩයේ හැඩය පෙන්වීමට)
        st.markdown("<p class='section-header'>3. 3D CARGO VISUALIZATION</p>", unsafe_allow_html=True)
        fig = go.Figure()
        for _, r in df.iterrows():
            fig.add_trace(go.Mesh3d(x=[0,0,r['Length_cm'],r['Length_cm'],0,0,r['Length_cm'],r['Length_cm']],
                                    y=[0,r['Width_cm'],r['Width_cm'],0,0,r['Width_cm'],r['Width_cm'],0],
                                    z=[0,0,0,0,r['Height_cm'],r['Height_cm'],r['Height_cm'],r['Height_cm']],
                                    i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                    color='blue', opacity=0.6, name=r['Cargo_Name']))
        st.plotly_chart(fig, use_container_width=True)
