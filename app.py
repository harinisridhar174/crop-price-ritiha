# app_crop_with_trend.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Crop Price Predictor with Trend", layout="centered")
st.title("🌾 Crop Price Predictor (with Trend Indicator)")

# ----------------- Sample Data -----------------
# Replace this with your actual CSV later
data = pd.DataFrame({
    'Crop': ['Wheat', 'Rice', 'Maize', 'Sugarcane'],
    'State': ['State1', 'State2', 'State1', 'State2'],
    'Price': [2000, 1500, 1800, 2200]
})

# ----------------- Farmer Input -----------------
crop = st.selectbox("Select Crop", data['Crop'].unique())
state = st.selectbox("Select State", data['State'].unique())
threshold = st.number_input("Enter Threshold Value (₹)", min_value=0, value=1800)

# ----------------- Predict Price & Suggestion -----------------
if st.button("Get Suggestion with Trend"):
    # Filter data for selected crop and state
    df = data[(data['Crop'] == crop) & (data['State'] == state)]
    
    if not df.empty:
        predicted_price = df['Price'].values[0]
        avg_price = data[data['Crop'] == crop]['Price'].mean()
        
        # Suggestion
        suggestion = "Sell" if predicted_price >= avg_price else "Wait"
        
        # Trend Indicator
        if predicted_price > threshold:
            trend = "📈 Increasing (above threshold)"
        elif predicted_price < threshold:
            trend = "📉 Decreasing (below threshold)"
        else:
            trend = "➖ Stable (at threshold)"
        
        # Output
        st.success(f"Predicted Price: ₹{predicted_price}")
        st.info(f"Suggestion: {suggestion}")
        st.warning(f"Trend Indicator: {trend}")
    else:
        st.warning("No data available for this crop/state combination.")
