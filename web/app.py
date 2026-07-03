import streamlit as st
import pandas as pd
import os
import joblib
from datetime import datetime

# 1. Configuration
st.set_page_config(
    page_title="WaterRangers", 
    page_icon="assets/icon.png", 
    layout="centered"
)

# Initialize session state to keep track of analysis status
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# 2. Header and Logos
col_logo1, col_titre, col_logo2 = st.columns([2, 4, 2])

with col_logo1:
    if os.path.exists("assets/logo_kmutt.webp"):
        st.image("assets/logo_kmutt.webp", width=160)

with col_logo2:
    if os.path.exists("assets/logo_esiea.png"):
        st.image("assets/logo_esiea.png", width=160)

st.title("Water Rangers")
st.markdown("Enter the sample parameters below to evaluate potability. All fields are required.")

# 3. Input Form
with st.form("prediction_form"):
    st.subheader("Sample Characteristics")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        ph = st.number_input("pH Level (0-14)", min_value=0.0, max_value=14.0, value=9.45)
        hardness = st.number_input("Hardness (mg/L)", value=145.81)
        solids = st.number_input("Solids / TDS (ppm)", value=13168.53)
        
    with c2:
        chloramines = st.number_input("Chloramines (ppm)", value=9.44)
        sulfate = st.number_input("Sulfate (mg/L)", value=310.58)
        conductivity = st.number_input("Conductivity (μS/cm)", value=592.66)
        
    with c3:
        organic_carbon = st.number_input("Organic Carbon (ppm)", value=8.61)
        trihalomethanes = st.number_input("Trihalomethanes (μg/L)", value=77.58)
        turbidity = st.number_input("Turbidity (NTU)", value=3.88)
        
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Run Analysis", use_container_width=True)

# 4. Prediction Logic
if submitted:
    # Cache inputs in session state so they persist after rerun
    st.session_state.inputs = {
        "ph": ph, "Hardness": hardness, "Solids": solids,
        "Chloramines": chloramines, "Sulfate": sulfate, 
        "Conductivity": conductivity, "Organic_carbon": organic_carbon,
        "Trihalomethanes": trihalomethanes, "Turbidity": turbidity
    }
    
    # Convert in DataFrame for model input
    input_data = pd.DataFrame([st.session_state.inputs])
    
    # Loading Models
    rf_model = joblib.load("model/random_forest.pkl")
    gb_model = joblib.load("model/gradient_boosting.pkl")
    xgb_model = joblib.load("model/xgboost.pkl")
    
    # Do predictions and store in session state
    st.session_state.pred_rf = rf_model.predict(input_data)[0]
    st.session_state.pred_gb = gb_model.predict(input_data)[0]
    st.session_state.pred_xgb = xgb_model.predict(input_data)[0]
    
    st.session_state.analysis_done = True

# 5. Display Results and Save Data
if st.session_state.analysis_done:
    
    # Display results inside a styled container
    with st.container(border=True):
        st.subheader("Analysis Results")
        
        r1, r2, r3 = st.columns(3)
        
        def render_result(col, model_name, pred):
            status = "Safe" if pred == 1 else "Unsafe"
            color = "#2e7d32" if pred == 1 else "#d32f2f"
            col.markdown(f"**{model_name}**")
            col.markdown(f"<h3 style='color: {color}; margin-top: 0px;'>{status}</h3>", unsafe_allow_html=True)
            
        render_result(r1, "Random Forest", st.session_state.pred_rf)
        render_result(r2, "Gradient Boosting", st.session_state.pred_gb)
        render_result(r3, "XGBoost", st.session_state.pred_xgb)
        
        st.markdown("---")
        
        # Section to save records for future research
        st.markdown("**Contribute to our research**")
        st.caption("Note: Saving this record will help us train the next version of our deep learning model.")
        st.caption("WARNING: The accuracy of our models does not exceed 68%; this project is for educational purposes only, and it cannot detect the presence of hidden bacteria or heavy metals.")
        
        location = st.text_input("Location (Optional)", placeholder="e.g., Bangkok, Chao Phraya River")
        
        if st.button("Save Record", type="primary"):
            # Prepare the data dictionary for saving
            new_data = st.session_state.inputs.copy()
            new_data["Location"] = location
            new_data["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data["RF_Pred"] = st.session_state.pred_rf
            new_data["GB_Pred"] = st.session_state.pred_gb
            new_data["XGB_Pred"] = st.session_state.pred_xgb
            
            df_new = pd.DataFrame([new_data])
            
            # Save to CSV (standard format for tabular data)
            file_path = "data/save.csv"
            
            # Ensure the data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Append to CSV (or create if it doesn't exist)
            if os.path.exists(file_path):
                df_new.to_csv(file_path, mode='a', header=False, index=False)
            else:
                df_new.to_csv(file_path, mode='w', header=True, index=False)
                
            st.success("Record successfully saved to database. Thank you!")