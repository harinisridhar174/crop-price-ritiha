import streamlit as st
import pandas as pd
import pickle
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Agri Crop Price Predictor",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: bold;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .prediction-section {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🌾 Agri Crop Price Predictor</h1>', unsafe_allow_html=True)

# Initialize session state
if 'model_data' not in st.session_state:
    st.session_state.model_data = None
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

# File upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.header("📁 Upload Your Trained Model")

uploaded_file = st.file_uploader(
    "Choose a PKL file",
    type=['pkl'],
    help="Upload your trained crop price prediction model"
)

if uploaded_file is not None:
    try:
        # Load the uploaded model
        with st.spinner("Loading model..."):
            model_data = pickle.load(uploaded_file)
        
        # Store in session state
        st.session_state.model_data = model_data
        st.session_state.file_uploaded = True
        
        st.success("✅ Model loaded successfully!")
        
        # Display model information
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Model Type", type(model_data.get('model', 'Unknown')).__name__)
            if 'scaler' in model_data:
                st.metric("Scaler Type", type(model_data['scaler']).__name__)
        
        with col2:
            if 'crop_state_data' in model_data:
                data_shape = model_data['crop_state_data'].shape
                st.metric("Training Data Shape", f"{data_shape[0]} rows × {data_shape[1]} columns")
        
        # Show available crops and states if data exists
        if 'crop_state_data' in model_data:
            crop_state_data = model_data['crop_state_data']
            st.subheader("🌱 Available Data")
            
            col1, col2 = st.columns(2)
            with col1:
                crops = crop_state_data['Crop'].unique() if 'Crop' in crop_state_data.columns else []
                st.write(f"**Crops:** {', '.join(crops[:8])}{'...' if len(crops) > 8 else ''}")
            
            with col2:
                states = crop_state_data['State'].unique() if 'State' in crop_state_data.columns else []
                st.write(f"**States:** {', '.join(states[:8])}{'...' if len(states) > 8 else ''}")
        
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        st.session_state.file_uploaded = False
        st.session_state.model_data = None

st.markdown('</div>', unsafe_allow_html=True)

# Prediction section (only show if model is loaded)
if st.session_state.file_uploaded and st.session_state.model_data is not None:
    st.markdown('<div class="prediction-section">', unsafe_allow_html=True)
    st.header("🔮 Make Predictions")
    
    model_data = st.session_state.model_data
    model = model_data.get('model')
    scaler = model_data.get('scaler')
    crop_state_data = model_data.get('crop_state_data')
    
    if model is None or scaler is None or crop_state_data is None:
        st.error("❌ Required model components not found. Please check your model file.")
    else:
        # Input form
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Crop' in crop_state_data.columns:
                crop_name = st.selectbox("Select Crop", sorted(crop_state_data['Crop'].unique()))
            else:
                crop_name = st.text_input("Enter Crop Name")
        
        with col2:
            if 'State' in crop_state_data.columns:
                state = st.selectbox("Select State", sorted(crop_state_data['State'].unique()))
            else:
                state = st.text_input("Enter State Name")
        
        with col3:
            current_price = st.number_input(
                "Current Market Price (₹)",
                min_value=0.0,
                value=1000.0,
                step=100.0
            )
        
        # Additional inputs based on available features
        additional_inputs = {}
        if 'crop_state_data' in model_data:
            sample_row = crop_state_data.iloc[0] if not crop_state_data.empty else None
            if sample_row is not None:
                feature_columns = [col for col in sample_row.index if col not in ['Crop', 'State', 'Price']]
                
                if feature_columns:
                    st.subheader("🔧 Additional Features")
                    cols = st.columns(min(3, len(feature_columns)))
                    
                    for i, feature in enumerate(feature_columns):
                        col_idx = i % 3
                        with cols[col_idx]:
                            if pd.api.types.is_numeric_dtype(crop_state_data[feature]):
                                additional_inputs[feature] = st.number_input(
                                    f"{feature}",
                                    value=float(sample_row[feature]),
                                    step=0.01
                                )
                            else:
                                additional_inputs[feature] = st.text_input(
                                    f"{feature}",
                                    value=str(sample_row[feature])
                                )
        
        # Prediction button
        if st.button("🚀 Predict Price and Get Recommendation", type="primary"):
            try:
                with st.spinner("Making prediction..."):
                    # Prepare input for model
                    if 'Crop' in crop_state_data.columns and 'State' in crop_state_data.columns:
                        input_df = crop_state_data[
                            (crop_state_data['Crop'] == crop_name) & 
                            (crop_state_data['State'] == state)
                        ].copy()
                        
                        if input_df.empty:
                            st.warning("⚠️ No data available for this crop & state combination.")
                        else:
                            # Use the last available row as base
                            base_row = input_df.iloc[-1:].copy()
                            
                            # Update with additional inputs if provided
                            for feature, value in additional_inputs.items():
                                if feature in base_row.columns:
                                    base_row[feature] = value
                            
                            # Prepare features for prediction
                            feature_columns = [col for col in base_row.columns if col not in ['Crop', 'State', 'Price']]
                            features = base_row[feature_columns].values
                            
                            # Scale features
                            features_scaled = scaler.transform(features)
                            
                            # Make prediction
                            predicted_price_scaled = model.predict(features_scaled)
                            
                            # Inverse transform to get actual price
                            dummy_array = np.zeros((1, scaler.n_features_in_))
                            dummy_array[0, :len(features[0])] = features[0]
                            dummy_array[0, -1] = predicted_price_scaled[0]
                            
                            predicted_price = scaler.inverse_transform(dummy_array)[0, -1]
                            predicted_price = max(0, predicted_price)
                            
                            # Calculate price change
                            price_change = predicted_price - current_price
                            price_change_percent = (price_change / current_price) * 100
                            
                            # Recommendation logic
                            if predicted_price > current_price * 1.1:
                                recommendation = "🟢 **WAIT TO SELL** - Expected higher profit"
                                recommendation_color = "success"
                                best_time = datetime.now() + timedelta(days=14)
                                confidence = "High"
                            elif predicted_price > current_price * 1.05:
                                recommendation = "🟡 **CONSIDER WAITING** - Moderate profit potential"
                                recommendation_color = "warning"
                                best_time = datetime.now() + timedelta(days=7)
                                confidence = "Medium"
                            else:
                                recommendation = "🔴 **SELL NOW** - Limited upside potential"
                                recommendation_color = "error"
                                best_time = datetime.now()
                                confidence = "Low"
                            
                            # Display results
                            st.subheader("📊 Prediction Results")
                            
                            # Metrics in cards
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Current Price", f"₹{current_price:,.2f}")
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric(
                                    "Predicted Price",
                                    f"₹{predicted_price:,.2f}",
                                    delta=f"{price_change:+,.2f} ({price_change_percent:+.1f}%)"
                                )
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Confidence", confidence)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Recommendation
                            st.subheader("💡 Sell Recommendation")
                            if recommendation_color == "success":
                                st.success(recommendation)
                            elif recommendation_color == "warning":
                                st.warning(recommendation)
                            else:
                                st.error(recommendation)
                            
                            st.info(f"**Suggested Best Time to Sell:** {best_time.strftime('%B %d, %Y')}")
                            
                            # Market insights
                            st.subheader("📈 Market Insights")
                            
                            if price_change > 0:
                                st.success(f"💰 **Potential Profit:** ₹{price_change:,.2f} per unit")
                                if price_change_percent > 20:
                                    st.info("🎯 **High Growth Potential:** Strong upward momentum")
                                elif price_change_percent > 10:
                                    st.info("📈 **Good Growth Potential:** Consider holding")
                                else:
                                    st.info("📊 **Moderate Growth:** Small positive movement")
                            else:
                                st.warning(f"📉 **Potential Loss:** ₹{abs(price_change):,.2f} per unit")
                                st.info("⚠️ **Market Caution:** Consider selling soon")
                            
                            # Historical context
                            if len(input_df) > 1:
                                st.subheader("📚 Historical Context")
                                historical_prices = input_df['Price'].tail(10) if 'Price' in input_df.columns else []
                                if len(historical_prices) > 1:
                                    price_trend = "↗️ Increasing" if historical_prices.iloc[-1] > historical_prices.iloc[0] else "↘️ Decreasing"
                                    st.write(f"**Recent Trend:** {price_trend}")
                                    st.write(f"**Price Range:** ₹{historical_prices.min():,.2f} - ₹{historical_prices.max():,.2f}")
                    
                    else:
                        st.error("❌ Model data structure not compatible. Please check your model file.")
                        
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
                st.info("💡 **Troubleshooting:** Check model components and feature compatibility")

    st.markdown('</div>', unsafe_allow_html=True)

# Instructions section
if not st.session_state.file_uploaded:
    st.markdown("---")
    st.subheader("📋 How to Use")
    st.write("""
    1. **Upload Model**: Upload your trained crop price prediction model (.pkl file)
    2. **Select Parameters**: Choose crop, state, and enter current market price
    3. **Get Predictions**: Receive price predictions and sell recommendations
    4. **Make Decisions**: Use the insights to optimize your selling strategy
    """)
    
    st.subheader("🔧 Model Requirements")
    st.write("""
    Your PKL file should contain:
    - **model**: Trained machine learning model
    - **scaler**: Fitted scaler for feature normalization
    - **crop_state_data**: DataFrame with crop, state, and feature columns
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🌾 Built with Streamlit | Agricultural Commodity Price Predictor"
    "</div>",
    unsafe_allow_html=True
)
