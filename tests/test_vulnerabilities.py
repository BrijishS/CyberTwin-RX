from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_vulnerabilities():
    response = client.get("/api/vulnerabilities/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 20


def test_vulnerability_crud_lifecycle():
    # Fetch an existing asset ID
    asset_res = client.get("/api/assets/")
    assert asset_res.status_code == 200
    asset_id = asset_res.json()[0]["id"]

    # 1. Create temporary vulnerability
    payload = {
        "asset_id": asset_id,
        "cve_id": "CVE-2026-DEMO-PHASE1-TEST",
        "title": "Temporary Test Vulnerability",
        "description": "Phase 1 verification test vulnerability",
        "cvss_score": 5.5,
        "epss_score": 0.25,
        "kev_status": False,
        "patch_available": True,
        "status": "Open"
    }
    create_res = client.post("/api/vulnerabilities/", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    vuln_id = created["id"]
    assert created["cve_id"] == "CVE-2026-DEMO-PHASE1-TEST"

    # 2. Read One
    get_res = client.get(f"/api/vulnerabilities/{vuln_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == vuln_id

    # 3. Update
    update_res = client.put(f"/api/vulnerabilities/{vuln_id}", json={"status": "Mitigated"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Mitigated"

    # 4. Delete (Clean up)
    del_res = client.delete(f"/api/vulnerabilities/{vuln_id}")
    assert del_res.status_code == 200

    # 5. Verify Deleted
    get_again = client.get(f"/api/vulnerabilities/{vuln_id}")
    assert get_again.status_code == 404


def test_vulnerability_validation_and_fk():
    # Non-existent asset_id (404)
    res_fk = client.post("/api/vulnerabilities/", json={
        "asset_id": 999999,
        "cve_id": "CVE-2026-DEMO-FK",
        "cvss_score": 5.0,
        "epss_score": 0.1,
        "status": "Open"
    })
    assert res_fk.status_code == 404

    asset_res = client.get("/api/assets/")
    asset_id = asset_res.json()[0]["id"]

    # Out of bounds CVSS score = 11 (422)
    res_cvss = client.post("/api/vulnerabilities/", json={
        "asset_id": asset_id,
        "cve_id": "CVE-2026-DEMO-CVSS",
        "cvss_score": 11.0,
        "epss_score": 0.1,
        "status": "Open"
    })
    assert res_cvss.status_code == 422

    # Out of bounds EPSS score = 1.5 (422)
    res_epss = client.post("/api/vulnerabilities/", json={
        "asset_id": asset_id,
        "cve_id": "CVE-2026-DEMO-EPSS",
        "cvss_score": 8.0,
        "epss_score": 1.5,
        "status": "Open"
    })
    assert res_epss.status_code == 422

    # Invalid status string (422)
    res_status = client.post("/api/vulnerabilities/", json={
        "asset_id": asset_id,
        "cve_id": "CVE-2026-DEMO-STATUS",
        "cvss_score": 8.0,
        "epss_score": 0.5,
        "status": "NotARealStatus"
    })
    assert res_status.status_code == 422
