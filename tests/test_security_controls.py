from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_security_controls():
    response = client.get("/api/security-controls/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 14


def test_security_control_crud_lifecycle():
    # Fetch an existing asset ID
    asset_res = client.get("/api/assets/")
    assert asset_res.status_code == 200
    asset_id = asset_res.json()[0]["id"]

    # 1. Create temporary security control
    payload = {
        "asset_id": asset_id,
        "name": "Phase1-Test-Control",
        "control_type": "Firewall",
        "description": "Phase 1 verification test control",
        "effectiveness": 0.8,
        "implementation_cost": 500000.0,
        "status": "Active",
        "implemented_at": None
    }
    create_res = client.post("/api/security-controls/", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    control_id = created["id"]
    assert created["name"] == "Phase1-Test-Control"

    # 2. Read One
    get_res = client.get(f"/api/security-controls/{control_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == control_id

    # 3. Update
    update_res = client.put(f"/api/security-controls/{control_id}", json={"effectiveness": 0.95})
    assert update_res.status_code == 200
    assert update_res.json()["effectiveness"] == 0.95

    # 4. Delete (Clean up)
    del_res = client.delete(f"/api/security-controls/{control_id}")
    assert del_res.status_code == 200

    # 5. Verify Deleted
    get_again = client.get(f"/api/security-controls/{control_id}")
    assert get_again.status_code == 404


def test_security_control_validation_and_fk():
    # Non-existent asset_id (404)
    res_fk = client.post("/api/security-controls/", json={
        "asset_id": 999999,
        "name": "Phase1-Orphan-Control",
        "control_type": "EDR",
        "effectiveness": 0.5,
        "implementation_cost": 100.0,
        "status": "Active"
    })
    assert res_fk.status_code == 404

    # Out of bounds effectiveness = 1.5 (422)
    res_eff1 = client.post("/api/security-controls/", json={
        "name": "Phase1-Eff-Control",
        "control_type": "MFA",
        "effectiveness": 1.5,
        "implementation_cost": 100.0,
        "status": "Active"
    })
    assert res_eff1.status_code == 422

    # Negative effectiveness = -0.2 (422)
    res_eff2 = client.post("/api/security-controls/", json={
        "name": "Phase1-Eff-Control2",
        "control_type": "MFA",
        "effectiveness": -0.2,
        "implementation_cost": 100.0,
        "status": "Active"
    })
    assert res_eff2.status_code == 422

    # Negative implementation cost = -100 (422)
    res_cost = client.post("/api/security-controls/", json={
        "name": "Phase1-Cost-Control",
        "control_type": "MFA",
        "effectiveness": 0.8,
        "implementation_cost": -100.0,
        "status": "Active"
    })
    assert res_cost.status_code == 422
