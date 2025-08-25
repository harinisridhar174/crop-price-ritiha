import streamlit as st
import pandas as pd
import pickle
import numpy as np
from datetime import datetime, timedelta

# Load the trained LSTM model
with open('lstm_models.pkl', 'rb') as file:   # ✅ corrected filename
    model_data = pickle.load(file)

model = model_data['model']
scaler = model_data['scaler']
crop_state_data = model_data['crop_state_data']  # Data to map crop & state to numeric if needed

# Title
st.title("Agri Crop Price Predictor")

st.write("Enter the details below to get the predicted price and sell recommendation:")

# Farmer inputs
crop_name = st.selectbox("Select Crop", crop_state_data['Crop'].unique())
state = st.selectbox("Select State", crop_state_data['State'].unique())
current_price = st.number_input("Enter Current Market Price", min_value=0.0, value=0.0)

# Button to predict
if st.button("Predict Price and Recommendation"):
    
    # Prepare input for model
    input_df = crop_state_data[(crop_state_data['Crop']==crop_name) & 
                               (crop_state_data['State']==state)].copy()
    
    if input_df.empty:
        st.warning("No data available for this crop & state combination.")
    else:
        # Take last available features
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
            best_time = datetime.now() + timedelta(days=7)  # Example: 1 week later
        else:
            recommendation = "Sell now"
            best_time = datetime.now()
        
        # Display results
        st.success(f"Predicted Price: ₹{predicted_price:.2f}")
        st.info(f"Recommendation: {recommendation}")
        st.info(f"Suggested Best Time to Sell: {best_time.strftime('%Y-%m-%d')}")
