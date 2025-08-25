# app_crop_with_trend_bg.py
import streamlit as st
import pandas as pd
import base64  # for background image

# ----------------- Page Config -----------------
st.set_page_config(page_title="Crop Price Predictor", layout="centered")

# ----------------- Background Image Function -----------------
def add_bg_from_local(image_file):
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

# Call background (make sure 2.png is in the same folder as this script)
add_bg_from_local("2.png")

# ----------------- Title -----------------
st.title("🌾 Crop Price Predictor (With Trend Indicator + Background)")

# ----------------- Sample Data -----------------
data = pd.DataFrame({
    'Crop': ['Wheat', 'Rice', 'Maize', 'Sugarcane'],
    'State': ['Tamil Nadu', 'Kerala', 'Karnataka', 'Andhra Pradesh'],
    'Price': [2000, 1500, 1800, 2200]
})

# ----------------- Farmer Input -----------------
crop = st.selectbox("Select Crop", data['Crop'].unique())
state = st.selectbox("Select State", data['State'].unique())

# Threshold value input
threshold = st.number_input(
    "Enter Threshold Price (₹)", 
    min_value=100, 
    max_value=10000, 
    value=1800, 
    step=100
)

# ----------------- Predict Price & Suggestion -----------------
if st.button("Get Suggestion"):
    df = data[(data['Crop']==crop) & (data['State']==state)]
    
    if not df.empty:
        predicted_price = df['Price'].values[0]
        avg_price = data[data['Crop']==crop]['Price'].mean()
        suggestion = "Sell" if predicted_price >= avg_price else "Wait"
        
        if predicted_price > threshold:
            trend = "📈 Increasing"
        elif predicted_price < threshold:
            trend = "📉 Decreasing"
        else:
            trend = "➡️ Stable"
        
        st.success(f"Predicted Price: ₹{predicted_price}")
        st.info(f"Suggestion: {suggestion}")
        st.warning(f"Trend Indicator: {trend}")
    else:
        st.warning("No data available for this crop/state combination.")
