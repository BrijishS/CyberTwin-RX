from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_optimizer_recommend_api():
    budget = 5000000.0
    response = client.post("/api/optimizer/recommend", json={"budget": budget})
    assert response.status_code == 200
    data = response.json()
    assert data["total_investment"] <= budget
    assert "selected_controls" in data
    assert "portfolio_rosi" in data


def test_optimizer_budget_validation():
    response = client.post("/api/optimizer/recommend", json={"budget": -100.0})
    assert response.status_code == 422


def test_optimizer_zero_budget_validation():
    response = client.post("/api/optimizer/recommend", json={"budget": 0.0})
    assert response.status_code == 422
