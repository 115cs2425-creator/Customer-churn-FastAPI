import os
import shutil
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel, Field
from typing import Literal
from typing_extensions import Annotated
import pandas as pd
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

app = FastAPI(
    title="Customer Churn Prediction API",
    description="API to predict whether a telecom/banking customer will churn or stay."
)

# 1. Recreate exact Sequential architecture to bypass Keras version deserialization bugs
churn_model = Sequential([
    Input(shape=(11,)),
    Dense(6, activation='relu', kernel_regularizer='l2'),
    Dense(5, activation='relu', kernel_regularizer='l2'),
    Dense(5, activation='relu', kernel_regularizer='l2'),
    Dense(3, activation='relu', kernel_regularizer='l2'),
    Dense(4, activation='relu', kernel_regularizer='l2'),
    Dense(1, activation='sigmoid')
])

# 2. Copy and load only raw weights safely to /tmp
model_source = os.path.join(os.path.dirname(__file__), "churn_model.keras")
model_path = "/tmp/churn_model.keras"

model_loaded_successfully = False
try:
    if not os.path.exists(model_path):
        shutil.copy(model_source, model_path)
    
    print("Loading model weights...")
    churn_model.load_weights(model_path)
    model_loaded_successfully = True
    print("Model weights loaded successfully!")
except Exception as e:
    print(f"CRITICAL ERROR loading weights: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "Customer Churn Prediction API is Live! -V2",
        "model_loaded": model_loaded_successfully
    }

handler = Mangum(app, api_gateway_base_path="/")

class UserInput(BaseModel):
    CustomerID: Annotated[str, Field(description="Unique ID of the customer", examples=["CUST-1024"])]
    Age: Annotated[int, Field(gt=0, lt=120, description="Age of the customer in years", examples=[35])]
    Gender: Annotated[Literal["Male", "Female"], Field(description="Gender of the customer", examples=["Male"])]
    Tenure: Annotated[int, Field(ge=0, description="Number of months customer has stayed with company", examples=[12])]
    MonthlyCharges: Annotated[float, Field(gt=0.0, description="Monthly amount charged to customer", examples=[65.50])]
    Contract: Annotated[
        Literal["Month-to-month", "One year", "Two year"],
        Field(description="Type of customer contract", examples=["Month-to-month"])
    ]
    PaymentMethod: Annotated[
        Literal["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        Field(description="Payment method used by customer", examples=["Electronic check"])
    ]
    TotalCharges: Annotated[float, Field(ge=0.0, description="Total amount charged so far", examples=[786.00])]

@app.post("/predict")
def predict_churn(data: UserInput):
    if not model_loaded_successfully:
        return {"error": "Model weights failed to load on startup. Check CloudWatch logs."}
    
    try:
        input_dict = data.model_dump()
        customer_id = input_dict.pop('CustomerID')

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

        input_df = pd.DataFrame([row])
        input_tensor = tf.convert_to_tensor(input_df, dtype=tf.float32)
        prediction = churn_model.predict(input_tensor)
        
        pred_val = float(prediction[0][0]) if isinstance(prediction[0], (list, np.ndarray)) else float(prediction[0])
        probability = pred_val
        churn_status = int(probability > 0.5)

        return {
            "customer_id": customer_id,
            "churn_prediction": churn_status,
            "churn_probability": round(probability, 4)
        }
    except Exception as e:
        return {"error": str(e)}