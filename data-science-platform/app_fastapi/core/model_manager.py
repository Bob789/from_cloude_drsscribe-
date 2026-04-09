# File: Final_Project_v003/app_fastapi/core/model_manager.py
"""
Model Manager - Handles saving and loading of models and metadata
"""
import os
import json
import joblib
from typing import Dict, List
from datetime import datetime

MODELS_DIR = "app_fastapi/models/trained"
METADATA_DIR = "app_fastapi/models/metadata"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

def save_model(model_name: str, estimator, metadata: Dict):
    """Saves model and metadata"""
    model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
    metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

    joblib.dump(estimator, model_path)

    metadata["created_at"] = datetime.utcnow().isoformat()
    metadata["model_file"] = f"{model_name}.pkl"

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def load_model(model_name: str):
    """Loads model from disk"""
    model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model '{model_name}' not found")

    return joblib.load(model_path)

def load_metadata(model_name: str) -> Dict:
    """Loads model metadata"""
    metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

    if not os.path.exists(metadata_path):
        return {"model_name": model_name, "metadata": "Not available"}

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_all_models() -> List[Dict]:
    """Returns a list of all saved models"""
    models = []
    files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".pkl")]

    for file in files:
        model_name = file.replace(".pkl", "")
        try:
            metadata = load_metadata(model_name)
            models.append(metadata)
        except:
            models.append({"model_name": model_name, "error": "Could not load metadata"})

    return models

def delete_model(model_name: str) -> Dict:
    """Deletes model and metadata"""
    model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
    metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model '{model_name}' not found")

    os.remove(model_path)

    if os.path.exists(metadata_path):
        os.remove(metadata_path)

    return {"message": f"Model '{model_name}' deleted successfully"}