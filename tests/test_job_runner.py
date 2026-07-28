import sys
from unittest.mock import MagicMock, patch

import pytest

from backend.repository.jobs import create_job, get_job


def _make_job(session, system_id):
    return create_job(session, system_id=system_id, phase="as-is")


@pytest.fixture(autouse=True)
def _mock_orchestrator():
    mock = MagicMock()
    mock.run_as_is_ingestion.return_value = {
        "run_id": "test-run",
        "status": "succeeded",
        "commit_sha": "abc123",
        "pr_number": 1,
        "pr_url": "https://github.com/test/repo/pull/1",
    }
    sys.modules["agents.orchestrator"] = mock
    yield
    sys.modules.pop("agents.orchestrator", None)


def _run_job(db_session, job, legacy_system):
    with patch("backend.job_runner.SessionLocal", return_value=db_session):
        from backend.job_runner import run_ingestion_job
        run_ingestion_job(
            job_id=job.id,
            system_id="test-system",
            system_id_int=legacy_system.id,
            evidence_path="./evidence",
            systems_root="./systems",
            github_token="fake-token",
            github_model_repo="test/repo",
        )


def test_job_transitions_to_succeeded(db_session, legacy_system):
    job = _make_job(db_session, legacy_system.id)

    agents_orch = sys.modules["agents.orchestrator"]

    def fake_ingestion(**kwargs):
        kwargs["db_session"].commit()
        return {
            "run_id": "test-run",
            "status": "succeeded",
            "commit_sha": "abc123",
            "pr_number": 1,
            "pr_url": "https://github.com/test/repo/pull/1",
        }

    agents_orch.run_as_is_ingestion.side_effect = fake_ingestion

    _run_job(db_session, job, legacy_system)

    updated = get_job(db_session, job.id)
    assert updated.status == "succeeded"
    assert updated.run_id is not None
    assert len(updated.run_id) == 8


def test_job_transitions_to_failed_on_orchestrator_error(db_session, legacy_system):
    job = _make_job(db_session, legacy_system.id)

    agents_orch = sys.modules["agents.orchestrator"]
    agents_orch.run_as_is_ingestion.side_effect = RuntimeError("orchestrator crashed")

    _run_job(db_session, job, legacy_system)

    updated = get_job(db_session, job.id)
    assert updated.status == "failed"
    assert "orchestrator crashed" in updated.error_message


def test_job_status_starts_as_queued(db_session, legacy_system):
    job = _make_job(db_session, legacy_system.id)
    assert job.status == "queued"


def test_job_runner_updates_running_before_ingestion(db_session, legacy_system):
    job = _make_job(db_session, legacy_system.id)

    agents_orch = sys.modules["agents.orchestrator"]
    agents_orch.run_as_is_ingestion.side_effect = RuntimeError("crashed")

    _run_job(db_session, job, legacy_system)

    updated = get_job(db_session, job.id)
    assert updated.started_at is not None
