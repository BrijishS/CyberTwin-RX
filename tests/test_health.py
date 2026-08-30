from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "project": "CyberTwin-RX",
        "status": "running",
        "phase": "Phase 6 - Integrated Hackathon MVP"
    }



def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
