# app_basic_crop.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Crop Price Predictor", layout="centered")
st.title("🌾 Crop Price Predictor (Basic Version)")

# ----------------- Sample Data -----------------
# You can replace this with your actual CSV later
data = pd.DataFrame({
    'Crop': ['Wheat', 'Rice', 'Maize', 'Sugarcane'],
    'State': ['State1', 'State2', 'State1', 'State2'],
    'Price': [2000, 1500, 1800, 2200]
})

# ----------------- Farmer Input -----------------
crop = st.selectbox("Select Crop", data['Crop'].unique())
state = st.selectbox("Select State", data['State'].unique())

# ----------------- Predict Price & Suggestion -----------------
if st.button("Get Suggestion"):
    # Filter data for selected crop and state
    df = data[(data['Crop']==crop) & (data['State']==state)]
    
    if not df.empty:
        predicted_price = df['Price'].values[0]
        avg_price = data[data['Crop']==crop]['Price'].mean()
        suggestion = "Sell" if predicted_price >= avg_price else "Wait"
        
        st.success(f"Predicted Price: ₹{predicted_price}")
        st.info(f"Suggestion: {suggestion}")
    else:
        st.warning("No data available for this crop/state combination.")
