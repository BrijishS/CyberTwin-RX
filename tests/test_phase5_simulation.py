from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import Vulnerability, SecurityControl

client = TestClient(app)


def test_what_if_simulation_api():
    db = SessionLocal()
    vuln_count_before = db.query(Vulnerability).count()
    ctrl_count_before = db.query(SecurityControl).count()
    db.close()

    response = client.post("/api/simulation/what-if", json={
        "asset_id": 4,
        "control_type": "MFA",
        "effectiveness": 0.85
    })
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == 4
    assert data["simulated_risk_score"] <= data["current_risk_score"]
    assert data["estimated_financial_risk_reduction"] >= 0.0

    # Verify Database Immutability
    db_after = SessionLocal()
    assert db_after.query(Vulnerability).count() == vuln_count_before
    assert db_after.query(SecurityControl).count() == ctrl_count_before
    db_after.close()


def test_portfolio_simulation_api():
    response = client.post("/api/simulation/portfolio", json={
        "controls": [
            {"asset_id": 4, "control_type": "MFA", "effectiveness": 0.85}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "enterprise_risk_before" in data
    assert "enterprise_risk_after" in data
    assert data["enterprise_risk_after"] <= data["enterprise_risk_before"]
