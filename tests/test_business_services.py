from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_business_services():
    response = client.get("/api/business-services/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 5


def test_business_service_crud_lifecycle():
    # 1. Create temporary business service
    payload = {
        "name": "Phase1-Test-Service",
        "description": "Temporary service for Phase 1 verification",
        "criticality": "Low",
        "financial_value": 100000.0,
        "department": "QA Testing",
        "is_active": True
    }
    create_res = client.post("/api/business-services/", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    service_id = created["id"]
    assert created["name"] == "Phase1-Test-Service"

    # 2. Duplicate Name Conflict (409)
    dup_res = client.post("/api/business-services/", json=payload)
    assert dup_res.status_code == 409

    # 3. Read One
    get_res = client.get(f"/api/business-services/{service_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == service_id

    # 4. Update
    update_res = client.put(f"/api/business-services/{service_id}", json={"financial_value": 200000.0})
    assert update_res.status_code == 200
    assert update_res.json()["financial_value"] == 200000.0

    # 5. Delete (Clean up)
    del_res = client.delete(f"/api/business-services/{service_id}")
    assert del_res.status_code == 200

    # 6. Verify Deleted
    get_again = client.get(f"/api/business-services/{service_id}")
    assert get_again.status_code == 404


def test_business_service_validation():
    # Negative financial value
    res1 = client.post("/api/business-services/", json={
        "name": "Invalid-BS-1",
        "criticality": "High",
        "financial_value": -100.0
    })
    assert res1.status_code == 422

    # Invalid criticality string
    res2 = client.post("/api/business-services/", json={
        "name": "Invalid-BS-2",
        "criticality": "SuperUltraCritical",
        "financial_value": 5000.0
    })
    assert res2.status_code == 422
