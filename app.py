from fastapi import FastAPI
from pydantic import BaseModel,Field,computed_field
from typing import Literal,Annotated
import pickle
import pandas as pd
import numpy as np


app = FastAPI(
    title="Customer Churn Prediction API",
    description="API to predict whether a telecom/banking customer will churn or stay."
)

# Application startup par trained churn model load karna
with open(r'D:\study notes\FastAPI\churn_model.pkl', 'rb') as f:
    churn_model = pickle.load(f)


# Lecture 7 Pattern: Detailed validation using Annotated and Field
class UserInput(BaseModel):
    CustomerID: Annotated[str, Field(description="Unique ID of the customer", 
                                     examples=["CUST-1024"])]
    Age: Annotated[int, Field(gt=0, lt=120, description="Age of the customer in years", 
                              examples=[35])]
    Gender: Annotated[Literal['Male', 'Female'], Field(description="Gender of the customer", 
                                                       examples=["Male"])]
    Tenure: Annotated[int, Field(ge=0, description="Number of months customer has stayed with company", 
                                 examples=[12])]
    MonthlyCharges: Annotated[float, Field(gt=0.0, description="Monthly amount charged to customer", 
                                           examples=[65.50])]
    Contract: Annotated[
        Literal['Month-to-month', 'One year', 'Two year'], 
        Field(description="Type of customer contract", examples=["Month-to-month"])
    ]
    PaymentMethod: Annotated[
        Literal['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], 
        Field(description="Payment method used by customer", examples=["Electronic check"])
    ]
    TotalCharges: Annotated[float, Field(ge=0.0, description="Total amount charged so far", 
                                         examples=[786.00])]


@app.get("/")
def home():
    return {"message": "Customer Churn Prediction API is active!"}


# Lecture 7 Pattern: ML Inference Endpoint
@app.post("/predict")
def predict_churn(data: UserInput):
    # 1. Pydantic model se dictionary lein
    input_dict = data.model_dump()
    customer_id = input_dict.pop('CustomerID')
    
    # 2. Training ke 11 columns ke mutabiq One-Hot Encoding structure banayein
    row = {
        'Age': data.Age,
        'Tenure': data.Tenure,
        'MonthlyCharges': data.MonthlyCharges,
        'TotalCharges': data.TotalCharges,
        'Gender_Male': 1 if data.Gender == 'Male' else 0,
        'Gender_Other': 1 if data.Gender == 'Other' else 0,
        'Contract_One year': 1 if data.Contract == 'One year' else 0,
        'Contract_Two year': 1 if data.Contract == 'Two year' else 0,
        'PaymentMethod_Electronic check': 1 if data.PaymentMethod == 'Electronic check' else 0,
        'PaymentMethod_Credit card': 1 if data.PaymentMethod == 'Credit card' else 0,
        'PaymentMethod_Mailed check': 1 if data.PaymentMethod == 'Mailed check' else 0
    }
    
    # DataFrame banayein jisme exact yhi 11 columns hon
    input_df = pd.DataFrame([row])

    # 3. Model Prediction
    prediction = churn_model.predict(input_df)
    
    # Classification result process karna
    if hasattr(churn_model, "predict_proba"):
        probability = float(churn_model.predict_proba(input_df)[0][1])
    else:
        pred_val = float(prediction[0][0]) if isinstance(prediction[0], (list, np.ndarray)) else float(prediction[0])
        probability = pred_val
        
    churn_status = int(probability > 0.5)
    
    # 4. Final API Response
    return {
        "customer_id": customer_id,
        "churn_prediction": churn_status,
        "churn_probability": round(probability, 4),
        "status": "Likely to Churn" if churn_status == 1 else "Likely to Stay"
    }