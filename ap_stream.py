import streamlit as st
import numpy as np
import pickle
import pandas as pd

# Page configuration
st.set_page_config(page_title="Customer Churn Prediction", page_icon="📊", layout="centered")

# Model load karne ke liye function
@st.cache_resource
def load_churn_model():
    with open('churn_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

model = load_churn_model()

st.title("📊 Customer Churn Prediction App")
st.write("Enter the customer details below to predict whether the customer is likely to churn.")

# User inputs form matching 11 training features
with st.form("churn_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=18, max_value=120, value=35)
        tenure = st.number_input("Tenure (Months)", min_value=0, max_value=120, value=12)
        monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=65.50)
        total_charges = st.number_input("Total Charges", min_value=0.0, value=786.00)
        gender = st.selectbox("Gender", ["Male", "Female"])
        
    with col2:
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
        payment_method = st.selectbox("Payment Method", [
            "Electronic check", "Mailed check", "Bank transfer", "Credit card"
        ])

    # Submit button
    submit_button = st.form_submit_button(label="Predict Churn")

if submit_button:
    # Training ke 11 columns ke mutabiq One-Hot Encoding structure banayein
    row = {
        'Age': age,
        'Tenure': tenure,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges,
        'Gender_Male': 1 if gender == 'Male' else 0,
        'Gender_Other': 0,  # Agar training me 'Other' category bhi thi
        'Contract_One year': 1 if contract == 'One year' else 0,
        'Contract_Two year': 1 if contract == 'Two year' else 0,
        'PaymentMethod_Electronic check': 1 if payment_method == 'Electronic check' else 0,
        'PaymentMethod_Credit card': 1 if payment_method == 'Credit card' else 0,
        'PaymentMethod_Mailed check': 1 if payment_method == 'Mailed check' else 0
    }
    
    # 11 features wala DataFrame banayein
    input_df = pd.DataFrame([row])
    
    # Model prediction
    prediction = model.predict(input_df)
    
    # Probability handling (ANN / Sigmoid threshold)
    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(input_df)[0][1])
    else:
        pred_val = float(prediction[0][0]) if isinstance(prediction[0], (list, np.ndarray)) else float(prediction[0])
        probability = pred_val
        
    churn_status = int(probability > 0.5)
    
    st.subheader("Prediction Result:")
    if churn_status == 1:
        st.error(f"⚠️ The customer is **likely to churn**! (Probability: {probability:.4f})")
    else:
        st.success(f"✅ The customer is **likely to stay**. (Probability: {probability:.4f})")