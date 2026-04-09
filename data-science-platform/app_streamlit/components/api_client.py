# File: app_streamlit/components/api_client.py
"""
API Client for Streamlit to interact with FastAPI backend.

Handles authentication, token management, model operations, and admin functions.
"""

import requests
import streamlit as st
from typing import Dict, Optional

TIMEOUT = 5


class APIClient:
    """HTTP client for FastAPI backend communication."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def _get_headers(self) -> Dict:
        """Get headers with JWT token if available."""
        token = st.session_state.get("access_token")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Execute HTTP request with error handling."""
        try:
            url = f"{self.base_url}{endpoint}"
            kwargs.setdefault("timeout", TIMEOUT)
            kwargs.setdefault("headers", self._get_headers())
            response = getattr(requests, method)(url, **kwargs)
            if response.status_code == 200:
                return response.json()
            try:
                error_data = response.json()
                return {"error": error_data.get("detail", str(error_data)), "status_code": response.status_code}
            except Exception:
                return {"error": response.text, "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to server."}
        except requests.exceptions.Timeout:
            return {"error": "Server timeout."}
        except Exception as e:
            return {"error": str(e)}

    def check_server_health(self) -> bool:
        """Check if FastAPI server is running."""
        try:
            return requests.get(f"{self.base_url}/health", timeout=2).status_code == 200
        except Exception:
            return False

    def get_server_status(self) -> Dict:
        """Get detailed server status."""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            if resp.status_code == 200:
                return {"status": "online", "message": "FastAPI server is running"}
            return {"status": "error", "message": f"Server returned {resp.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "message": "Server not running",
                    "help": "uvicorn app_fastapi.app_fastapi:app --reload --port 8000"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def signup(self, username: str, password: str) -> Dict:
        """Register a new user."""
        return self._request("post", "/auth/signup", json={"username": username, "password": password})

    def login(self, username: str, password: str) -> Dict:
        """Login and get JWT token."""
        result = self._request("post", "/auth/login", json={"username": username, "password": password})
        if "error" not in result:
            st.session_state.update({"access_token": result["access_token"], "username": result["username"],
                                     "tokens": result["tokens"], "is_admin": result.get("is_admin", False)})
        return result

    def logout(self):
        """Clear session state."""
        st.session_state.clear()

    def get_tokens(self, username: str) -> Dict:
        """Get token balance for a user."""
        return self._request("get", f"/auth/tokens/{username}")

    def add_tokens(self, username: str, tokens: int) -> Dict:
        """Add tokens to user account."""
        return self._request("post", "/auth/add_tokens", json={"username": username, "tokens": tokens})

    def train_model(self, file, model_name: str, feature_columns: str, label_column: str,
                    test_size: float = 0.2, model_type: str = "linear_regression") -> Dict:
        """Train a model with uploaded CSV file."""
        data = {"model_name": model_name, "feature_columns": feature_columns,
                "label_column": label_column, "test_size": test_size, "model_type": model_type}
        return self._request("post", "/models/train", files={"file": file}, data=data)

    def predict(self, model_name: str, features: Dict) -> Dict:
        """Make a prediction with a trained model."""
        return self._request("post", "/models/predict", json={"model_name": model_name, "features": features})

    def list_models(self) -> Dict:
        """Get list of all trained models."""
        return self._request("get", "/models")

    def get_model_details(self, model_name: str) -> Dict:
        """Get detailed information about a model."""
        return self._request("get", f"/models/{model_name}")

    def delete_model(self, model_name: str) -> Dict:
        """Delete a trained model."""
        return self._request("delete", f"/models/{model_name}")

    def get_all_users(self) -> Dict:
        """Get all users (admin only)."""
        return self._request("get", "/auth/users")

    def create_user_admin(self, username: str, password: str, tokens: int = 10, is_admin: bool = False) -> Dict:
        """Create a new user (admin only)."""
        return self._request("post", "/auth/users",
                             json={"username": username, "password": password, "tokens": tokens, "is_admin": is_admin})

    def update_user_admin(self, username: str, new_username: str = None, new_password: str = None,
                          new_tokens: int = None, new_is_admin: bool = None) -> Dict:
        """Update user details (admin only)."""
        payload = {k: v for k, v in {"new_username": new_username, "new_password": new_password,
                                     "new_tokens": new_tokens, "new_is_admin": new_is_admin}.items() if v is not None}
        return self._request("put", f"/auth/users/{username}", json=payload)

    def delete_user_admin(self, username: str) -> Dict:
        """Delete a user (admin only)."""
        return self._request("delete", f"/auth/users/{username}")

    def get_usage_logs(self, username: Optional[str] = None, limit: int = 50) -> Dict:
        """Get usage logs."""
        params = {"limit": limit}
        if username:
            params["username"] = username
        return self._request("get", "/auth/usage_logs", params=params)