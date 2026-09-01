import pytest
import os
import sys
from fastapi.testclient import TestClient

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.core.config import settings

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_admin_login(client):
    res = client.post(
        "/api/auth/login",
        json={"email": settings.ADMIN_EMAIL, "password": settings.ADMIN_PASSWORD}
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == settings.ADMIN_EMAIL
    assert data["user"]["role"] == "admin"

def test_load_demo_data(client):
    res = client.post("/api/demo/load")
    assert res.status_code == 200
    data = res.json()
    assert data["total_incidents"] == 100
    assert "top_incident" in data
    assert data["top_incident"]["priority_score"] > 70.0
    assert data["top_incident"]["why_number_one"] is not None

def test_ranked_incidents_queue(client):
    res = client.get("/api/incidents/ranking?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 100
    assert len(data["items"]) == 10
    
    # Check deterministic ordering: first item must have higher or equal priority to second item
    items = data["items"]
    for i in range(len(items) - 1):
        assert items[i]["priority_score"] >= items[i+1]["priority_score"]

def test_incident_detail_and_explainability(client):
    list_res = client.get("/api/incidents/ranking?limit=1")
    top_inc = list_res.json()["items"][0]
    inc_id = top_inc["id"]

    res = client.get(f"/api/incidents/{inc_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["id"] == inc_id
    assert detail["factor_contributions"] is not None
    assert len(detail["factor_contributions"]) > 5

def test_comparative_reasoning_endpoint(client):
    list_res = client.get("/api/incidents/ranking?limit=2")
    items = list_res.json()["items"]
    id_1 = items[0]["id"]
    id_2 = items[1]["id"]

    res = client.post(f"/api/incidents/{id_1}/compare/{id_2}")
    assert res.status_code == 200
    comp = res.json()
    assert "higher_priority_code" in comp
    assert "plain_language_justification" in comp
    assert "divergent_factors" in comp

def test_simulator_endpoint(client):
    payload = {
        "title": "Simulation Test Alert",
        "incident_type": "Ransomware",
        "asset_name": "CORP-DC-01.local",
        "asset_type": "Domain Controller",
        "severity": 95.0,
        "data_sensitivity": 90.0,
        "asset_importance": 98.0,
        "attack_confidence": 95.0,
        "raw_users": 3000,
        "raw_systems": 25,
        "time_risk": 0.85,
        "recurrence": 1
    }
    res = client.post("/api/simulator", json=payload)
    assert res.status_code == 200
    sim = res.json()
    assert sim["simulated_priority_score"] >= 80.0
    assert sim["simulated_priority_level"] == "CRITICAL"
    assert "explainability_summary" in sim

def test_pdf_report_generation(client):
    list_res = client.get("/api/incidents/ranking?limit=1")
    inc_id = list_res.json()["items"][0]["id"]

    # Generate executive report
    res = client.post("/api/reports", json={"incident_id": inc_id, "report_type": "executive"})
    assert res.status_code == 200
    rep = res.json()
    assert "download_url" in rep
    assert os.path.exists(rep["file_path"])

    # Test download endpoint
    dl_res = client.get(rep["download_url"])
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000

def test_analytics_endpoint(client):
    res = client.get("/api/analytics")
    assert res.status_code == 200
    an = res.json()
    assert an["total_incidents"] == 100
    assert len(an["type_distribution"]) > 0
    assert len(an["severity_distribution"]) == 4
    assert len(an["top_affected_assets"]) > 0

def test_model_performance_endpoint(client):
    res = client.get("/api/model/performance")
    assert res.status_code == 200
    perf = res.json()
    assert "metrics" in perf
    assert perf["metrics"]["r2_score"] > 0.80
    assert len(perf["feature_importances"]) == 12
