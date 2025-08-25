# app_crop_with_trend.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Crop Price Predictor", layout="centered")
st.title("🌾 Crop Price Predictor (With Trend Indicator)")

# ----------------- Sample Data -----------------
# Replace with your actual CSV later
data = pd.DataFrame({
    'Crop': ['Wheat', 'Rice', 'Maize', 'Sugarcane'],
    'State': ['Tamilnadu', 'Telangana', 'Kerala', 'Karnataka'],
    'Price': [2000, 1500, 1800, 2200]
})

# ----------------- Farmer Input -----------------
crop = st.selectbox("Select Crop", data['Crop'].unique())
state = st.selectbox("Select State", data['State'].unique())

# NEW: Threshold input
threshold = st.number_input(
    "Enter Threshold Price (₹)", 
    min_value=100, 
    max_value=10000, 
    value=1800,  # default value
    step=100
)

# ----------------- Predict Price & Suggestion -----------------
if st.button("Get Suggestion with Trend"):
    # Filter data for selected crop and state
    df = data[(data['Crop'] == crop) & (data['State'] == state)]
    
    if not df.empty:
        predicted_price = df['Price'].values[0]
        avg_price = data[data['Crop'] == crop]['Price'].mean()
        suggestion = "✅ Sell" if predicted_price >= avg_price else "⏳ Wait"
        
        # Trend analysis based on threshold
        if predicted_price > threshold:
            trend = "📈 Increasing (above threshold)"
            trend_color = "green"
        elif predicted_price < threshold:
            trend = "📉 Decreasing (below threshold)"
            trend_color = "red"
        else:
            trend = "➖ Stable (equal to threshold)"
            trend_color = "orange"

        # Show results
        st.success(f"Predicted Price: ₹{predicted_price}")
        st.info(f"Suggestion: {suggestion}")
        st.markdown(f"<p style='color:{trend_color}; font-size:18px;'>{trend}</p>", unsafe_allow_html=True)
    else:
        st.warning("No data available for this crop/state combination.")
