# File: Final_Project_v003/app_streamlit/pages/predict_page.py
"""
Prediction page for making predictions with trained models.
"""

import streamlit as st
import json
import pandas as pd
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

        # Show feature ranges table if available
        feature_stats = model_info.get("feature_stats", {})
        if feature_stats:
            st.subheader("📋 Feature Ranges (from training data)")
            range_rows = []
            for col in feature_columns:
                stats = feature_stats.get(col, {})
                if stats.get("type") == "numeric":
                    range_rows.append({
                        "Feature": col,
                        "Min": stats["min"],
                        "Max": stats["max"],
                        "Mean": stats["mean"],
                        "Type": "Numeric"
                    })
                elif stats.get("type") == "categorical":
                    vals = ", ".join(str(v) for v in stats.get("values", []))
                    range_rows.append({
                        "Feature": col,
                        "Min": "-",
                        "Max": "-",
                        "Mean": vals,
                        "Type": "Categorical"
                    })
            if range_rows:
                range_df = pd.DataFrame(range_rows)
                range_df.columns = ["Feature", "Min", "Max", "Mean / Values", "Type"]
                st.dataframe(range_df, use_container_width=True, hide_index=True)

        # Create input fields
        features = {}

        # Group features in columns for better layout
        n_cols = 3
        cols = st.columns(n_cols)

        for idx, feature in enumerate(feature_columns):
            stats = feature_stats.get(feature, {})
            default_val = stats.get("mean", 0.0) if stats.get("type") == "numeric" else 0.0
            min_val = stats.get("min", None)
            max_val = stats.get("max", None)

            with cols[idx % n_cols]:
                features[feature] = st.number_input(
                    feature,
                    value=float(default_val),
                    min_value=float(min_val) if min_val is not None else None,
                    max_value=float(max_val) if max_val is not None else None,
                    format="%.2f",
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
                    st.session_state["predict_result"] = result
                    st.session_state["predict_features"] = features
                    st.session_state["predict_model_info"] = model_info

                    # Update token balance from server
                    username = st.session_state.get("username")
                    if username:
                        token_result = api_client.get_tokens(username)
                        if "tokens" in token_result:
                            st.session_state["tokens"] = token_result["tokens"]
                        else:
                            st.session_state["tokens"] -= 5
                    else:
                        st.session_state["tokens"] -= 5

                    st.rerun()

        # Show prediction result after rerun
        if "predict_result" in st.session_state:
            result = st.session_state.pop("predict_result")
            pred_features = st.session_state.pop("predict_features", {})
            pred_model = st.session_state.pop("predict_model_info", {})

            st.success("✅ Prediction completed!")
            st.subheader("📊 Prediction Result")

            pred_val = result["prediction"]
            model_type = result.get("model_type", pred_model.get("model_type", ""))

            if isinstance(pred_val, (int, float)):
                st.metric("Predicted Value", f"{pred_val:,.2f}")
            else:
                st.metric("Predicted Value", str(pred_val))

            # --- Visualization ---
            probabilities = result.get("prediction_probabilities")
            classes = pred_model.get("classes")

            if probabilities and classes:
                # Classification: probability bar chart
                st.subheader("📈 Class Probabilities")
                prob_df = pd.DataFrame({
                    "Class": [str(c) for c in classes],
                    "Probability": probabilities
                }).set_index("Class")
                st.bar_chart(prob_df)

            elif isinstance(pred_val, (int, float)):
                # Regression: feature values chart + prediction gauge
                st.subheader("📈 Input Features")
                feat_df = pd.DataFrame({
                    "Feature": list(pred_features.keys()),
                    "Value": [float(v) for v in pred_features.values()]
                }).set_index("Feature")
                st.bar_chart(feat_df)

            st.info(f"5 tokens deducted. Remaining: {st.session_state.get('tokens', '?')} tokens")

            with st.expander("📋 Full Response"):
                st.json(result)

    st.divider()

    # Quick predictions section
    st.subheader("💡 Quick Tips")
    st.write("- Make sure to use the correct feature names as shown")
    st.write("- Feature values should match the scale used during training")
    st.write("- One-hot encoded features should be 0 or 1")
    st.write("- Date-derived features should be year, month, day numbers")