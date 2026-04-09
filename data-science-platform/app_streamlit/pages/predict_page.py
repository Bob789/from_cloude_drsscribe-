# File: Final_Project_v003/app_streamlit/pages/predict_page.py
"""
Prediction page for making predictions with trained models.
"""

import streamlit as st
import json
from components.api_client import APIClient

api_client = APIClient()

def show():
    st.title("🔮 Make Prediction")
    st.write("Select a trained model and provide feature values to get predictions.")

    # Display token cost
    st.warning("💰 Each prediction costs **5 tokens**")

    # Get list of models
    result = api_client.list_models()

    if "error" in result:
        st.error(f"Failed to load models: {result['error']}")
        return

    models = result.get("models", [])

    if not models:
        st.info("No trained models available. Please train a model first!")
        return

    # Model selection
    st.subheader("1️⃣ Select Model")
    model_names = [m["model_name"] for m in models]
    selected_model = st.selectbox("Choose a model", model_names)

    # Get model details
    model_info = next((m for m in models if m["model_name"] == selected_model), None)

    if model_info:
        # Display model info
        with st.expander("ℹ️ Model Information"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Model Type:** {model_info.get('model_type', 'N/A')}")
                st.write(f"**Trained:** {model_info.get('trained_at', 'N/A')}")

            with col2:
                if "metrics" in model_info:
                    st.write("**Performance:**")
                    metrics = model_info['metrics']

                    # Handle different metric formats (holdout: test_r2, CV: r2_mean)
                    r2_value = metrics.get('test_r2') or metrics.get('r2_mean') or metrics.get('r2')
                    rmse_value = metrics.get('test_rmse') or metrics.get('rmse_mean') or metrics.get('rmse')

                    if r2_value is not None:
                        st.write(f"- R²: {r2_value:.4f}")
                    if rmse_value is not None:
                        st.write(f"- RMSE: {rmse_value:.4f}")

        # Feature input
        st.subheader("2️⃣ Enter Feature Values")

        # Get feature columns from metadata
        feature_columns = model_info.get("feature_columns", [])

        if not feature_columns:
            st.error("Model metadata is incomplete. Cannot make predictions.")
            return

        st.write(f"This model requires **{len(feature_columns)}** features:")

        # Create input fields
        features = {}

        # Group features in columns for better layout
        n_cols = 3
        cols = st.columns(n_cols)

        for idx, feature in enumerate(feature_columns):
            with cols[idx % n_cols]:
                features[feature] = st.number_input(
                    feature,
                    value=0.0,
                    format="%.4f",
                    key=f"feature_{feature}"
                )

        # Alternative: JSON input
        with st.expander("📝 Or enter features as JSON"):
            json_input = st.text_area(
                "Feature JSON",
                value=json.dumps({f: 0.0 for f in feature_columns}, indent=2),
                height=200
            )

            if st.button("Load from JSON"):
                try:
                    features = json.loads(json_input)
                    st.success("Features loaded from JSON!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid JSON: {str(e)}")

        # Display current features
        st.subheader("3️⃣ Review & Predict")
        st.json(features)

        # Predict button
        if st.button("🚀 Make Prediction", type="primary"):
            with st.spinner("Making prediction..."):
                result = api_client.predict(selected_model, features)

                if "error" in result:
                    st.error(f"Prediction failed: {result['error']}")
                    if result.get("status_code") == 402:
                        st.warning("Insufficient tokens! Please purchase more tokens.")
                elif "prediction" in result:
                    st.success("✅ Prediction completed!")

                    # Display result
                    st.subheader("📊 Prediction Result")
                    st.metric("Predicted Value", f"{result['prediction']:.4f}")

                    # Update token balance from server
                    username = st.session_state.get("username")
                    if username:
                        token_result = api_client.get_tokens(username)
                        if "tokens" in token_result:
                            st.session_state["tokens"] = token_result["tokens"]
                            st.info(f"5 tokens deducted. Remaining: {token_result['tokens']} tokens")
                        else:
                            st.session_state["tokens"] -= 5
                            st.info(f"5 tokens deducted. Remaining: {st.session_state['tokens']} tokens")
                    else:
                        st.session_state["tokens"] -= 5
                        st.info(f"5 tokens deducted. Remaining: {st.session_state['tokens']} tokens")

                    # Force refresh to update token display in sidebar
                    st.rerun()

                    # Show full response
                    with st.expander("📋 Full Response"):
                        st.json(result)

    st.divider()

    # Quick predictions section
    st.subheader("💡 Quick Tips")
    st.write("- Make sure to use the correct feature names as shown")
    st.write("- Feature values should match the scale used during training")
    st.write("- One-hot encoded features should be 0 or 1")
    st.write("- Date-derived features should be year, month, day numbers")