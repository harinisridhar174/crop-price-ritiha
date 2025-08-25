import streamlit as st
import joblib
import numpy as np
from gtts import gTTS
import os

# Page setup
st.set_page_config(page_title="🌾 Crop Price Prediction", layout="centered")
st.title("🌾 Crop Price Prediction App")
st.subheader("Helping Farmers Decide When to Sell Crops")

# Load models
@st.cache_resource
def load_models():
    return joblib.load("lstm_models.joblib")

models = load_models()

# Original Wikipedia images for crops
crop_images = {
    "rice": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Rice_paddy_field_in_Bangladesh.jpg",
    "wheat": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Wheat_close-up.JPG",
    "maize": "https://upload.wikimedia.org/wikipedia/commons/7/79/Maize_field.jpg",
    "sugarcane": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Sugarcane_field.jpg",
    "cotton": "https://upload.wikimedia.org/wikipedia/commons/d/d4/CottonPlant.JPG",
    "soybean": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Soybean_field.jpg",
    "barley": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Barley_field.jpg",
    "pulses": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Pulses_in_India.jpg",
    "groundnut": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Groundnut_field.jpg",
    "mustard": "https://upload.wikimedia.org/wikipedia/commons/1/18/Mustard_field_in_India.jpg"
}

# Language option
language = st.radio("Choose Language", ["English", "தமிழ் (Tamil)", "Both"])

# User input
crop = st.selectbox("Select Crop", sorted({c for c, _ in models.keys()}))
state = st.selectbox("Select State", sorted({s for _, s in models.keys()}))
current_price = st.number_input("Enter Current Price (₹ per quintal)", min_value=0.0, step=0.1)

if st.button("Predict"):
    key = (crop.lower(), state.lower())
    if key in models:
        model, scaler = models[key]

        # Prepare sequence
        last_sequence = np.array([current_price] * 30).reshape(-1, 1)
        last_sequence_scaled = scaler.transform(last_sequence)
        X_input = last_sequence_scaled.reshape(1, 30, 1)

        # Predict price
        predicted_price = model.predict(X_input)[0][0]
        predicted_price = scaler.inverse_transform([[predicted_price]])[0][0]

        # Decision logic
        if predicted_price > current_price:
            decision = "SELL"
            english_advice = f"Price is expected to rise to ₹{predicted_price:.2f}. You can sell now."
            tamil_advice = f"விலை ₹{predicted_price:.2f} வரை உயரும். நீங்கள் இப்போது விற்கலாம்."
            color = "green"
        else:
            decision = "HOLD"
            english_advice = f"Price may drop to ₹{predicted_price:.2f}. It is better to hold."
            tamil_advice = f"விலை ₹{predicted_price:.2f} வரை குறையும். காத்திருப்பது நல்லது."
            color = "red"

        # Show result
        st.markdown(f"### Prediction: <span style='color:{color}; font-size:24px;'>{decision}</span>", unsafe_allow_html=True)

        if language == "English":
            st.write(english_advice)
        elif language == "தமிழ் (Tamil)":
            st.write(f"**தமிழில் அறிவுரை:** {tamil_advice}")
        else:
            st.write(english_advice)
            st.write(f"**தமிழில் அறிவுரை:** {tamil_advice}")

        # Show crop image from Wikipedia
        if crop.lower() in crop_images:
            st.image(crop_images[crop.lower()], caption=f"{crop.capitalize()} Crop", use_column_width=True)

        # Audio for Tamil advice
        if language in ["தமிழ் (Tamil)", "Both"]:
            tts = gTTS(tamil_advice, lang='ta')
            audio_path = "advice_tamil.mp3"
            tts.save(audio_path)
            st.audio(audio_path, format="audio/mp3")
    else:
        st.error("Model for selected crop and state is not available.")
