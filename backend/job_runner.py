import logging
import uuid
from pathlib import Path

from backend.database import SessionLocal
from backend.repository.jobs import update_job_run_id, update_job_status

logger = logging.getLogger(__name__)


def run_ingestion_job(
    job_id: int,
    system_id: str,
    system_id_int: int,
    evidence_path: str | Path,
    systems_root: str | Path,
    github_token: str,
    github_model_repo: str,
):
    session = SessionLocal()
    try:
        run_id = str(uuid.uuid4())[:8]
        update_job_status(session, job_id, "running")
        update_job_run_id(session, job_id, run_id)

        from agents.orchestrator import run_as_is_ingestion

        result = run_as_is_ingestion(
            system_id=system_id,
            evidence_path=evidence_path,
            systems_root=systems_root,
            github_token=github_token,
            github_model_repo=github_model_repo,
            system_id_int=system_id_int,
            db_session=session,
            run_id=run_id,
        )

        update_job_status(session, job_id, "succeeded")
        logger.info(
            "Job %d succeeded: run_id=%s PR=#%d", job_id, run_id, result["pr_number"]
        )

    except Exception as exc:
        logger.exception("Job %d failed", job_id)
        update_job_status(session, job_id, "failed", error_message=str(exc))
    finally:
        session.close()
