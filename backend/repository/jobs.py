from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.models import Job

TERMINAL_STATUSES = {"succeeded", "failed"}


def create_job(
    session: Session, system_id: int, phase: str, run_id: str | None = None
) -> Job:
    job = Job(system_id=system_id, phase=phase, status="queued", run_id=run_id)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def update_job_status(
    session: Session, job_id: int, status: str, error_message: str | None = None
) -> Job | None:
    job = session.get(Job, job_id)
    if job is None:
        return None
    if job.status == status:
        return job

    now = datetime.now(UTC)
    if status == "running" and job.started_at is None:
        job.started_at = now
    if status in TERMINAL_STATUSES:
        job.finished_at = now
        if status == "failed":
            job.error_message = error_message

    job.status = status
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: int) -> Job | None:
    return session.get(Job, job_id)
