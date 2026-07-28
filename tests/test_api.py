import json

import pytest
from fastapi.testclient import TestClient

from backend.main import app, get_session, verify_api_key
from backend.models import ArtifactVersion, ModelElementIndex


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[verify_api_key] = lambda: None
    app.dependency_overrides[get_session] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_ingest_creates_job(client, db_session, legacy_system):
    response = client.post(f"/systems/{legacy_system.id}/ingest")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"

    from backend.repository.jobs import get_job
    job = get_job(db_session, data["job_id"])
    assert job is not None
    assert job.status == "queued"


def test_get_job_status_not_found(client):
    response = client.get("/jobs/99999")
    assert response.status_code == 404


def test_get_job_status_found(client, db_session, legacy_system):
    from backend.repository.jobs import create_job
    job = create_job(db_session, system_id=legacy_system.id, phase="as-is")

    response = client.get(f"/jobs/{job.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job.id
    assert data["status"] == "queued"


def test_list_elements_empty(client, db_session, legacy_system):
    response = client.get(f"/systems/{legacy_system.id}/elements")
    assert response.status_code == 200
    assert response.json() == []


def test_list_elements_with_data(client, db_session, legacy_system):
    from backend.repository.model_elements import upsert_model_element
    upsert_model_element(
        db_session,
        system_id=legacy_system.id,
        layer="application",
        archimate_type="Application Service",
        name="Payment Service",
        git_path="systems/legacy-system/as-is/application/payment-service.json",
        current_commit="abc123",
    )

    response = client.get(f"/systems/{legacy_system.id}/elements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Payment Service"


def test_list_elements_filtered_by_layer(client, db_session, legacy_system):
    from backend.repository.model_elements import upsert_model_element
    upsert_model_element(
        db_session,
        system_id=legacy_system.id,
        layer="application",
        archimate_type="Application Service",
        name="Payment Service",
        git_path="systems/legacy-system/as-is/application/payment-service.json",
        current_commit="abc123",
    )
    upsert_model_element(
        db_session,
        system_id=legacy_system.id,
        layer="technology",
        archimate_type="Node",
        name="Server",
        git_path="systems/legacy-system/as-is/technology/server.json",
        current_commit="abc123",
    )

    response = client.get(f"/systems/{legacy_system.id}/elements?layer=application")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["layer"] == "application"


def test_get_element_detail_not_found(client):
    response = client.get("/elements/99999")
    assert response.status_code == 404


def test_get_element_detail_file_not_found(client, db_session, legacy_system, tmp_path):
    import backend.main as _bm
    _bm.SYSTEMS_ROOT = tmp_path

    element = ModelElementIndex(
        system_id=legacy_system.id,
        layer="application",
        archimate_type="Application Service",
        name="Test",
        git_path="systems/s1/as-is/application/test.json",
        current_commit="abc123",
    )
    db_session.add(element)
    db_session.commit()
    db_session.refresh(element)

    response = client.get(f"/elements/{element.id}")
    assert response.status_code == 404


def test_get_element_detail_success(client, db_session, legacy_system, tmp_path):
    import backend.main as _bm
    _bm.SYSTEMS_ROOT = tmp_path

    element = ModelElementIndex(
        system_id=legacy_system.id,
        layer="application",
        archimate_type="Application Service",
        name="Payment Service",
        git_path="systems/s1/as-is/application/payment-service.json",
        current_commit="abc123",
    )
    db_session.add(element)
    db_session.commit()
    db_session.refresh(element)

    file_path = tmp_path / element.git_path
    file_path.parent.mkdir(parents=True)
    content = {
        "id": "payment-service",
        "layer": "application",
        "archimate_type": "Application Service",
        "name": "Payment Service",
        "documentation": "Handles payments",
        "confidence": "observed",
        "evidence": [{"source_type": "code", "locator": "src/main.py"}],
        "relationships": [],
    }
    file_path.write_text(json.dumps(content), encoding="utf-8")

    response = client.get(f"/elements/{element.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "payment-service"
    assert data["name"] == "Payment Service"
    assert len(data["evidence"]) == 1


def test_list_artifact_versions_empty(client, db_session, legacy_system):
    response = client.get(f"/systems/{legacy_system.id}/artifact-versions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_artifact_versions_with_data(client, db_session, legacy_system):
    version = ArtifactVersion(
        system_id=legacy_system.id,
        commit_sha="abc123",
        phase="as-is",
        author_type="agent",
        run_id="run1",
        pr_number=42,
        approval_status="pending",
    )
    db_session.add(version)
    db_session.commit()

    response = client.get(f"/systems/{legacy_system.id}/artifact-versions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["commit_sha"] == "abc123"
    assert data[0]["approval_status"] == "pending"
    assert data[0]["pr_number"] == 42


def test_unauthorized_request_rejected():
    import backend.main as _bm
    _bm.API_KEY = "test-secret-key"

    from backend.main import get_session as _gs
    app.dependency_overrides[verify_api_key] = verify_api_key
    app.dependency_overrides[_gs] = lambda: None

    client = TestClient(app)
    response = client.get("/jobs/1")
    assert response.status_code == 401

    app.dependency_overrides.clear()
