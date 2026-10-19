# 🚀 Customer Churn Prediction API (FastAPI + Deep Learning)

An end-to-end Machine Learning pipeline and RESTful API built with **FastAPI** and **TensorFlow/Keras** to predict customer churn based on demographic and subscription attributes.

## 📌 Project Overview
This repository contains a deployed Artificial Neural Network (ANN) model served via a high-performance FastAPI backend. It features dynamic payload parsing, one-hot feature alignment, and schema validation with Pydantic.

## 🛠️ Tech Stack
- **Framework:** FastAPI, Uvicorn
- **Machine Learning / Deep Learning:** TensorFlow/Keras, Pandas, NumPy, Scikit-learn
- **Data Validation:** Pydantic
- **Version Control:** Git & GitHub

## 📂 Project Structure
```text
.
├── app.py                  # Core FastAPI application & predict endpoint
├── churn_model.pkl         # Trained ANN model / preprocessor artifact
├── churn_model.ipynb       # Model training & EDA notebook
├── requirements.txt        # Dependencies list
└── README.md               # Project documentation
