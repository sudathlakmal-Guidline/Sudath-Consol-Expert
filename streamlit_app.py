import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ==========================================
# 1. පද්ධති සැකසුම් (SYSTEM CONFIG)
# ==========================================
st.set_page_config(page_title="SMART CONSOL PLANNER - BY SUDATH", layout="wide")

# පරිශීලක දත්ත ගබඩාව (Simple CSV Database)
USER_DB = "users_db.csv"

def load_users():
    if os.path.exists(USER_DB):
        return pd.read_csv(USER_DB)
    return pd.DataFrame(columns=["email", "password", "reg_date"])

def save_user(email, password):
    df = load_users()
    if email in df['email'].values:
        return False
    new_user = pd.DataFrame([[email, password, datetime.now().strftime('%Y-%m-%d')]], 
                            columns=["email", "password", "reg_date"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_DB, index=False)
    return True

# ==========================================
# 2. LOGIN & SIGNUP SYSTEM (30-DAY TRIAL)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🚢 SMART CONSOL PLANNER</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 CREATE ACCOUNT (30 DAYS FREE)"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN", use_container_width=True):
                users = load_users()
                user_row = users[users['email'] == email]
                if not user_row.empty and str(user_row.iloc[0]['password']) == pwd:
                    reg_date = datetime.strptime(user_row.iloc[0]['reg_date'], '%Y-%m-%d')
                    expiry_date = reg_date + timedelta(days=30)
                    
                    if datetime.now() <= expiry_date:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.expiry = expiry_date.strftime('%Y-%m-%d')
                        st.rerun()
                    else:
                        st.error(f"Your 30-day trial expired on {expiry_date.strftime('%Y-%m-%d')}. Contact Sudath for full access.")
                else:
                    st.error("Invalid Email or Password.")

    with tab2:
        st.info("New users get 30 days of full access for free.")
        with st.form("signup_form"):
            new_email = st.text_input("Enter your Email")
            new_pwd = st.text_input("Create Password", type="password")
            confirm_pwd = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("CREATE MY ACCOUNT", use_container_width=True):
                if new_pwd != confirm_pwd:
                    st.error("Passwords do not match!")
                elif len(new_pwd) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    if save_user(new_email, new_pwd):
                        st.success("Account created successfully! Please go to the LOGIN tab.")
                    else:
                        st.error("Email already registered!")

else:
    # ==========================================
    # 3. ප්‍රධාන පද්ධතිය (MAIN INTERFACE)
    # ==========================================
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #002b5e 0%, #004a99 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;">
            <h1>🚢 SMART CONSOL PLANNER - BY SUDATH</h1>
            <p>Logged in as: {st.session_state.user_email} | ⏳ Trial Ends: {st.session_state.expiry}</p>
        </div>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_email}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        module = st.radio("OPERATIONAL MODULE:", ["📦 Consolidation Planner", "🏗️ OOG Assessment"])

    # --- CONSOLIDATION ENGINE (Same as v38.0) ---
    if module == "📦 Consolidation Planner":
        st.subheader("1. MANIFEST DATA ENTRY")
        init_df = pd.DataFrame([
            {"Cargo_Name": "P1", "Length_cm": 115, "Width_cm": 115, "Height_cm": 115, "Quantity": 10, "Weight_kg": 1000, "Rotation": "NO"},
            {"Cargo_Name": "P2", "Length_cm": 115, "Width_cm": 115, "Height_cm": 75, "Quantity": 10, "Weight_kg": 500, "Rotation": "NO"}
        ])
        input_df = st.data_editor(init_df, num_rows="dynamic", use_container_width=True)

        if st.button("GENERATE LOADING PLAN", type="primary", use_container_width=True):
            clean_df = input_df.dropna()
            # 3D Visualization Logic (Same as before)
            # ... [කලින් තිබූ 3D Code එකම මෙතනට එනවා] ...
            st.success("Loading Plan Generated Successfully!")
            # (ඉතිරි 3D Visualization කොටස් ටික මෙතන තිබිය යුතුයි)
