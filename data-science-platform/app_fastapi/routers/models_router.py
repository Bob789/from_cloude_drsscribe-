# File: app_fastapi/routers/models_router.py
"""
Models router for training, prediction, and model management.

All endpoints are protected with JWT and require tokens.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from pydantic import BaseModel
from typing import List, Optional
from app_fastapi.services import model_service
from app_fastapi.services.auth_dependency import get_current_user
from app_fastapi.services.token_service import validate_and_deduct_tokens, refund_tokens
from app_fastapi.services.logger_service import log_model_training, log_prediction, log_validation_error
from app_fastapi import database_manager as db
import os

router = APIRouter()
UPLOAD_DIR = "app_fastapi/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class PredictRequest(BaseModel):
    """Schema for prediction requests."""
    model_name: str
    features: dict


def _pick_primary_metric(metrics: dict, primary: str = None) -> str:
    """Select the best metric key for summary display."""
    if primary:
        for cand in [f"{primary}_mean", f"test_{primary}", primary]:
            if cand in metrics:
                return cand
    for cand in ["f1_weighted_mean", "accuracy_mean", "test_f1_weighted", "test_accuracy",
                 "rmse_mean", "test_rmse", "r2_mean", "test_r2"]:
        if cand in metrics:
            return cand
    return None


@router.post("/train")
async def train_model(
        file: UploadFile = File(...), model_name: str = Form(...),
        feature_columns: str = Form(...), label_column: str = Form(...),
        test_size: float = Form(0.2), model_type: str = Form("linear_regression"),
        evaluation_strategy: str = Form("cv"), cv_folds: int = Form(5),
        cv_repeats: int = Form(1), stratify: bool = Form(True),
        primary_metric: Optional[str] = Form(None),
        current_user: dict = Depends(get_current_user)):
    """Train a machine learning model from uploaded CSV file."""
    username = current_user["sub"]
    validate_and_deduct_tokens(username, "train")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        feature_list = [col.strip() for col in feature_columns.split(",")]
        metadata = model_service.train_model_from_csv(
            file_path=file_path, model_name=model_name, feature_columns=feature_list,
            label_column=label_column, test_size=test_size, model_type=model_type,
            evaluation_strategy=evaluation_strategy, cv_folds=cv_folds,
            cv_repeats=cv_repeats, stratify=stratify, primary_metric=primary_metric)

        metrics = metadata.get("metrics", {}) or {}
        primary = metadata.get("evaluation", {}).get("primary_metric")
        key = _pick_primary_metric(metrics, primary)
        metric_value = metrics.get(key) if key else None
        summary = f"{key}={metric_value:.4f}" if key and isinstance(metric_value, (int, float)) else "metrics: available"

        log_model_training(username, model_name, success=True, details=summary)
        db.add_usage_log(username, "MODEL_TRAINING", -1, "SUCCESS",
                         f"Trained {model_type} model '{model_name}'")

        return {"status": "success", "message": f"Model '{model_name}' trained",
                "metadata": metadata, "tokens_deducted": 1}

    except ValueError as e:
        refund_tokens(username, "train", f"Validation error: {str(e)}")
        log_validation_error("train", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        refund_tokens(username, "train", f"Training failed: {str(e)}")
        log_model_training(username, model_name, success=False, details=str(e))
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/predict")
async def predict_model(request: PredictRequest, current_user: dict = Depends(get_current_user)):
    """Make a prediction using a trained model."""
    username = current_user["sub"]
    validate_and_deduct_tokens(username, "predict")

    try:
        result = model_service.predict_with_model(request.model_name, request.features)
        log_prediction(username, request.model_name, success=True)
        db.add_usage_log(username, "PREDICTION", -5, "SUCCESS",
                         f"Prediction with '{request.model_name}': {result['prediction']}")
        result["tokens_deducted"] = 5
        return result
    except FileNotFoundError as e:
        refund_tokens(username, "predict", str(e))
        log_prediction(username, request.model_name, success=False, details=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        refund_tokens(username, "predict", str(e))
        log_validation_error("predict", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        refund_tokens(username, "predict", str(e))
        log_prediction(username, request.model_name, success=False, details=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("")
async def list_models(current_user: dict = Depends(get_current_user)):
    """Get list of all trained models."""
    try:
        models = model_service.list_all_models()
        return {"status": "success", "models": models, "count": len(models)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/{model_name}")
async def get_model_details(model_name: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific model."""
    try:
        metadata = model_service.get_model_details(model_name)
        return {"status": "success", "model": metadata}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model: {str(e)}")


@router.delete("/{model_name}")
async def delete_model(model_name: str, current_user: dict = Depends(get_current_user)):
    """Delete a trained model."""
    try:
        result = model_service.delete_model(model_name)
        db.add_usage_log(current_user["sub"], "MODEL_DELETION", 0, "SUCCESS",
                         f"Deleted model '{model_name}'")
        return {"status": "success", "message": result["message"]}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")