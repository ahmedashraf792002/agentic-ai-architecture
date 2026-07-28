import hashlib
import hmac
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.models import ArtifactVersion
from backend.webhook import create_webhook_router

WEBHOOK_SECRET = "test-secret"


def sign(payload: bytes, secret: str = WEBHOOK_SECRET) :
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def make_app(db_session, systems_root: Path, system_slug: str = "sys1"):
    app = FastAPI()
    router = create_webhook_router(
        webhook_secret=WEBHOOK_SECRET,
        systems_root=systems_root,
        system_slug_resolver=lambda system_id: system_slug,
        session_dependency=lambda: db_session,
    )
    app.include_router(router)
    return TestClient(app)


def merged_pr_payload(pr_number: int):
    return {
        "action": "closed",
        "pull_request": {
            "number": pr_number,
            "merged": True,
            "merged_by": {"login": "reviewer1"},
        },
    }


def test_webhook_rejects_invalid_signature(db_session, tmp_path: Path):
    client = make_app(db_session, tmp_path)
    body = json.dumps(merged_pr_payload(1)).encode()

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=wrongvalue"},
    )

    assert response.status_code == 401


def test_webhook_rejects_missing_signature(db_session, tmp_path: Path):
    client = make_app(db_session, tmp_path)
    body = json.dumps(merged_pr_payload(1)).encode()

    response = client.post("/webhooks/github", content=body)

    assert response.status_code == 401


def test_webhook_approves_on_valid_merge(db_session, legacy_system, tmp_path: Path):
    version = ArtifactVersion(
        system_id=legacy_system.id,
        commit_sha="abc123",
        phase="as-is",
        author_type="agent",
        run_id="run1",
        pr_number=99,
        approval_status="pending",
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)

    client = make_app(db_session, tmp_path)
    body = json.dumps(merged_pr_payload(99)).encode()

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-Hub-Signature-256": sign(body)},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"

    db_session.refresh(version)
    assert version.approval_status == "approved"
    assert version.approved_by == "reviewer1"


def test_webhook_duplicate_delivery_is_a_noop(db_session, legacy_system, tmp_path: Path):
    version = ArtifactVersion(
        system_id=legacy_system.id,
        commit_sha="abc123",
        phase="as-is",
        author_type="agent",
        run_id="run1",
        pr_number=100,
        approval_status="pending",
    )
    db_session.add(version)
    db_session.commit()

    client = make_app(db_session, tmp_path)
    body = json.dumps(merged_pr_payload(100)).encode()
    headers = {"X-Hub-Signature-256": sign(body)}

    first = client.post("/webhooks/github", content=body, headers=headers)
    second = client.post("/webhooks/github", content=body, headers=headers)

    assert first.json()["status"] == "approved"
    assert second.json()["status"] == "already_approved"


def test_webhook_refreshes_model_element_index_from_real_files(db_session, legacy_system, tmp_path: Path):
    system_dir = tmp_path / "sys1" / "as-is" / "application"
    system_dir.mkdir(parents=True)
    (system_dir / "app-1.json").write_text(
        json.dumps(
            {
                "id": "app-1",
                "layer": "application",
                "archimate_type": "Application Service",
                "name": "Payment Service",
                "documentation": "",
                "confidence": "observed",
                "evidence": [{"source_type": "docs", "locator": "x.md"}],
                "relationships": [],
                "current_commit": "abc123",
            }
        ),
        encoding="utf-8",
    )

    version = ArtifactVersion(
        system_id=legacy_system.id,
        commit_sha="abc123",
        phase="as-is",
        author_type="agent",
        run_id="run1",
        pr_number=101,
        approval_status="pending",
    )
    db_session.add(version)
    db_session.commit()

    client = make_app(db_session, tmp_path)
    body = json.dumps(merged_pr_payload(101)).encode()

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-Hub-Signature-256": sign(body)},
    )

    assert response.json()["elements_refreshed"] == 1


def test_webhook_ignores_non_merge_events(db_session, tmp_path: Path):
    client = make_app(db_session, tmp_path)
    payload = {"action": "opened", "pull_request": {"number": 1, "merged": False}}
    body = json.dumps(payload).encode()

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-Hub-Signature-256": sign(body)},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
