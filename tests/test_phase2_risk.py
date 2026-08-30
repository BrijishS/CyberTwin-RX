from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_risk_summary_api():
    response = client.get("/api/risk/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_assets" in data
    assert "total_vulnerabilities" in data
    assert "critical_assets" in data
    assert "average_risk_score" in data
    assert "total_financial_exposure" in data
    assert data["total_assets"] >= 0
    assert data["average_risk_score"] >= 0.0
    assert data["average_risk_score"] <= 100.0
    assert data["total_financial_exposure"] >= 0.0


def test_assets_risk_api():
    response = client.get("/api/risk/assets")
    assert response.status_code == 200
    assets_risk = response.json()
    assert isinstance(assets_risk, list)
    for a in assets_risk:
        assert 0.0 <= a["risk_score"] <= 100.0
        assert a["estimated_financial_exposure"] >= 0.0
        assert a["risk_level"] in ("Low", "Moderate", "Medium", "High", "Critical")


def test_top_assets_risk_api():
    response = client.get("/api/risk/top-assets?limit=5")
    assert response.status_code == 200
    top_assets = response.json()
    assert isinstance(top_assets, list)
    assert len(top_assets) <= 5
