import streamlit as st
import pandas as pd
import pickle
import numpy as np
from datetime import datetime, timedelta
import base64  # 👈 Needed for background image

# ----------------- Page Config -----------------
st.set_page_config(page_title="Agri Crop Price Predictor", layout="wide")

# ----------------- Background Image Function -----------------
def add_bg_from_local(image_file):
    """Adds a background image from a local file"""
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the background setter (⚠️ put your image in same folder as this script)
add_bg_from_local("plough_tool.jpg")

# ----------------- Load Model -----------------
with open('crop_price_model.pkl', 'rb') as file:
    model_data = pickle.load(file)

model = model_data['model']
scaler = model_data['scaler']
crop_state_data = model_data['crop_state_data']

# ----------------- Title -----------------
st.title("🌾 Agri Crop Price Predictor")

st.write("Enter the details below to get the predicted price and sell recommendation:")

# ----------------- Farmer Inputs -----------------
crop_name = st.selectbox("Select Crop", crop_state_data['Crop'].unique())
state = st.selectbox("Select State", crop_state_data['State'].unique())
current_price = st.number_input("Enter Current Market Price", min_value=0.0, value=0.0)

# ----------------- Prediction -----------------
if st.button("Predict Price and Recommendation"):
    
    input_df = crop_state_data[(crop_state_data['Crop']==crop_name) & 
                               (crop_state_data['State']==state)].copy()
    
    if input_df.empty:
        st.warning("No data available for this crop & state combination.")
    else:
        last_features = input_df.iloc[-1:].drop(['Price'], axis=1).values
        last_scaled = scaler.transform(last_features)
        
        # Predict price
        predicted_price_scaled = model.predict(last_scaled)
        predicted_price = scaler.inverse_transform(
            np.hstack([last_features[:, :-1], predicted_price_scaled.reshape(-1,1)])
        )[:, -1][0]
        
        # Recommendation logic
        if predicted_price > current_price * 1.05:
            recommendation = "Wait to sell for higher profit"
            best_time = datetime.now() + timedelta(days=7)
        else:
            recommendation = "Sell now"
            best_time = datetime.now()
        
        # ----------------- Display Results -----------------
        st.success(f"Predicted Price: ₹{predicted_price:.2f}")
        st.info(f"Recommendation: {recommendation}")
        st.info(f"Suggested Best Time to Sell: {best_time.strftime('%Y-%m-%d')}")
