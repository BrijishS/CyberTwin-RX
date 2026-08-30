import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.ai.predictor import predictor
from backend.ai.service import get_ai_status
from backend.ai.train_model import MODEL_FILE, METADATA_FILE, train_and_save_model

client = TestClient(app)


def test_ai_model_files_exist():
    """Ensure trained model file and metadata json exist on disk."""
    if not os.path.exists(MODEL_FILE) or not os.path.exists(METADATA_FILE):
        train_and_save_model()

    assert os.path.exists(MODEL_FILE), "Model PKL file should exist."
    assert os.path.exists(METADATA_FILE), "Model metadata JSON file should exist."


def test_ai_model_loaded_successfully():
    """Ensure predictor loads model successfully."""
    status = predictor.get_status()
    assert status["loaded"] is True, "AI predictor should report loaded=true."
    assert status["model"] == "RandomForestClassifier"
    assert "metrics" in status
    assert status["metrics"]["accuracy"] > 0.5


def test_ai_model_predict_bounds():
    """Ensure prediction outputs are within valid mathematical ranges."""
    sample_features = {
        "cvss_score": 9.8,
        "epss_score": 0.85,
        "kev_status": 1,
        "internet_exposed": 1,
        "patch_available": 0,
        "asset_criticality": 3,
        "control_effectiveness": 0.2,
        "open_vulnerability_count": 5,
        "high_vulnerability_count": 3,
        "business_criticality": 3,
    }

    res = predictor.predict(sample_features)
    assert 0.0 <= res["exploitation_probability"] <= 1.0
    assert 0.0 <= res["percentage"] <= 100.0
    assert res["risk_level"] in ["Low", "Moderate", "High", "Critical"]
    assert res["confidence"] in ["Low", "Medium", "High"]
    assert isinstance(res["top_contributing_features"], list)
    assert len(res["top_contributing_features"]) >= 1


def test_api_ai_status_endpoint():
    """Test GET /api/ai/status endpoint."""
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["loaded"] is True
    assert data["model"] == "RandomForestClassifier"
    assert "metrics" in data


def test_api_ai_vulnerability_prediction_endpoint():
    """Test GET /api/ai/vulnerabilities/1 endpoint."""
    response = client.get("/api/ai/vulnerabilities/1")
    assert response.status_code == 200
    data = response.json()
    assert "cve_id" in data
    assert "exploitation_probability" in data
    assert 0.0 <= data["exploitation_probability"] <= 1.0
    assert 0.0 <= data["percentage"] <= 100.0
    assert data["risk_level"] in ["Low", "Moderate", "High", "Critical"]
    assert "top_contributing_features" in data
    assert "ai_assisted_priority_score" in data


def test_api_ai_top_threats_endpoint():
    """Test GET /api/ai/top-threats endpoint."""
    response = client.get("/api/ai/top-threats?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Ensure sorted by exploitation probability descending
    probs = [item["exploitation_probability"] for item in data]
    assert probs == sorted(probs, reverse=True)
