from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_assets():
    response = client.get("/api/assets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 12


def test_asset_crud_lifecycle():
    # Fetch an existing business service ID
    bs_res = client.get("/api/business-services/")
    assert bs_res.status_code == 200
    bs_id = bs_res.json()[0]["id"]

    # 1. Create temporary asset
    payload = {
        "name": "Phase1-Test-Asset",
        "asset_type": "Server",
        "hostname": "test-host-01",
        "ip_address": "10.0.99.1",
        "business_service_id": bs_id,
        "criticality": "Medium",
        "financial_value": 500000.0,
        "internet_exposed": False,
        "environment": "Development",
        "owner_department": "QA",
        "is_active": True
    }
    create_res = client.post("/api/assets/", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    asset_id = created["id"]
    assert created["name"] == "Phase1-Test-Asset"

    # 2. Duplicate Name Conflict (409)
    dup_res = client.post("/api/assets/", json=payload)
    assert dup_res.status_code == 409

    # 3. Read One
    get_res = client.get(f"/api/assets/{asset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == asset_id

    # 4. Update
    update_res = client.put(f"/api/assets/{asset_id}", json={"financial_value": 750000.0})
    assert update_res.status_code == 200
    assert update_res.json()["financial_value"] == 750000.0

    # 5. Delete (Clean up)
    del_res = client.delete(f"/api/assets/{asset_id}")
    assert del_res.status_code == 200

    # 6. Verify Deleted
    get_again = client.get(f"/api/assets/{asset_id}")
    assert get_again.status_code == 404


def test_asset_foreign_key_and_validation():
    # Non-existent business_service_id (404)
    res_fk = client.post("/api/assets/", json={
        "name": "Phase1-Orphan-Asset",
        "asset_type": "API",
        "business_service_id": 999999,
        "criticality": "High",
        "financial_value": 100.0
    })
    assert res_fk.status_code == 404

    # Negative financial value (422)
    bs_res = client.get("/api/business-services/")
    bs_id = bs_res.json()[0]["id"]
    res_val = client.post("/api/assets/", json={
        "name": "Phase1-Negative-Asset",
        "asset_type": "API",
        "business_service_id": bs_id,
        "criticality": "High",
        "financial_value": -500.0
    })
    assert res_val.status_code == 422
