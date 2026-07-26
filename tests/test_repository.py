from backend.repository.artifact_versions import (
    create_artifact_version,
    update_artifact_approval,
)
from backend.repository.evidence_sources import (
    create_evidence_source,
    list_evidence_sources,
)
from backend.repository.jobs import create_job, update_job_status
from backend.repository.legacy_systems import create_legacy_system, get_legacy_system
from backend.repository.model_elements import list_model_elements, upsert_model_element


def make_system(session):
    return create_legacy_system(session, name="Test System")


def test_create_and_get_legacy_system(db_session):
    system = make_system(db_session)
    assert get_legacy_system(db_session, system.id).name == "Test System"


def test_upsert_model_element_updates_not_duplicates(db_session):
    system = make_system(db_session)
    args = {
        "session": db_session,
        "system_id": system.id,
        "layer": "application",
        "archimate_type": "Application Component",
        "git_path": "systems/s1/application/payment-service.json",
        "current_commit": "abc123",
    }
    first = upsert_model_element(name="Payment Service", **args)
    second = upsert_model_element(
        name="Payment Service (renamed)", **{**args, "current_commit": "def456"}
    )

    assert first.id == second.id
    elements = list_model_elements(db_session, system.id)
    assert len(elements) == 1
    assert elements[0].name == "Payment Service (renamed)"


def test_artifact_approval_is_idempotent(db_session):
    system = make_system(db_session)
    version = create_artifact_version(
        db_session,
        system_id=system.id,
        commit_sha="abc123",
        phase="as-is",
        author_type="agent",
    )

    once = update_artifact_approval(db_session, version.id, "approved", "reviewer")
    twice = update_artifact_approval(db_session, version.id, "approved", "reviewer")

    assert once.approval_status == twice.approval_status == "approved"
    assert once.approved_at == twice.approved_at


def test_job_status_update_twice_does_not_error_or_corrupt(db_session):
    system = make_system(db_session)
    job = create_job(db_session, system_id=system.id, phase="as-is")

    update_job_status(db_session, job.id, "running")
    first = update_job_status(db_session, job.id, "failed", "boom")
    second = update_job_status(db_session, job.id, "failed", "boom again")

    assert first.status == second.status == "failed"
    assert second.error_message == "boom"
    assert second.finished_at == first.finished_at


def test_evidence_sources_create_and_list(db_session):
    system = make_system(db_session)
    create_evidence_source(
        db_session, system_id=system.id, source_type="code", location="/evidence/code/"
    )
    sources = list_evidence_sources(db_session, system.id)
    assert len(sources) == 1
    assert sources[0].source_type == "code"
