from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_sources_health():
    response = client.get("/sources/health")
    assert response.status_code == 200
    assert "We Work Remotely" in response.json()["primary"]["name"]


def test_get_jobs_and_count():
    response = client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    count_resp = client.get("/jobs/count")
    assert count_resp.status_code == 200
    assert "job_count" in count_resp.json()


def test_get_job_not_found():
    response = client.get("/jobs/99999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
