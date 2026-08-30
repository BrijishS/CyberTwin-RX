from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_digital_twin_graph_api():
    response = client.get("/api/digital-twin/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    node_ids = {n["id"] for n in data["nodes"]}
    assert "Internet" in node_ids


def test_attack_paths_api():
    response = client.get("/api/attack-paths")
    assert response.status_code == 200
    paths = response.json()
    assert isinstance(paths, list)
    for p in paths:
        assert len(p["path"]) >= 2
        assert 0.0 <= p["path_score"] <= 100.0
        assert p["potential_financial_exposure"] >= 0.0


def test_top_attack_path_api():
    response = client.get("/api/attack-paths/top")
    assert response.status_code == 200
    top_path = response.json()
    assert "path" in top_path
    assert "path_score" in top_path
