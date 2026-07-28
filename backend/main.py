import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_session
from backend.job_runner import run_ingestion_job
from backend.models import ModelElementIndex
from backend.repository.artifact_versions import list_artifact_versions
from backend.repository.jobs import create_job, get_job
from backend.repository.model_elements import list_model_elements
from backend.webhook import create_webhook_router

load_dotenv()

SYSTEMS_ROOT = Path(os.environ.get("SYSTEMS_ROOT", "../agentic-ai-models/systems"))
EVIDENCE_PATH = Path(os.environ.get("EVIDENCE_PATH", "evidence"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_MODEL_REPO = os.environ.get("GITHUB_MODEL_REPO", "")
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
API_KEY = os.environ.get("API_KEY", "dev-key")

app = FastAPI(title="Agentic AI Architecture API")


async def verify_api_key(x_api_key: str = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")


webhook_router = create_webhook_router(
    webhook_secret=GITHUB_WEBHOOK_SECRET,
    systems_root=SYSTEMS_ROOT,
    system_slug_resolver=lambda system_id: "legacy-system",
    session_dependency=get_session,
)
app.include_router(webhook_router, dependencies=[Depends(verify_api_key)])


@app.post("/systems/{system_id}/ingest")
async def trigger_ingestion(
    system_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    auth: None = Depends(verify_api_key),
):
    from backend.repository.legacy_systems import get_legacy_system

    system = get_legacy_system(session, system_id)
    if not system:
        raise HTTPException(status_code=404, detail="system not found")

    job = create_job(session, system_id=system.id, phase="as-is")

    background_tasks.add_task(
        run_ingestion_job,
        job_id=job.id,
        system_id=str(system_id),
        system_id_int=system.id,
        evidence_path=str(EVIDENCE_PATH),
        systems_root=str(SYSTEMS_ROOT),
        github_token=GITHUB_TOKEN,
        github_model_repo=GITHUB_MODEL_REPO,
    )

    return {"job_id": job.id, "status": "queued"}


@app.get("/jobs/{job_id}")
async def get_job_status(
    job_id: int,
    session: Session = Depends(get_session),
    auth: None = Depends(verify_api_key),
):
    job = get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "id": job.id,
        "system_id": job.system_id,
        "phase": job.phase,
        "status": job.status,
        "run_id": job.run_id,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }


@app.get("/systems/{system_id}/elements")
async def list_elements(
    system_id: int,
    layer: str = Query(None),
    session: Session = Depends(get_session),
    auth: None = Depends(verify_api_key),
):
    elements = list_model_elements(session, system_id)
    if layer:
        elements = [e for e in elements if e.layer == layer]
    return [
        {
            "id": e.id,
            "layer": e.layer,
            "archimate_type": e.archimate_type,
            "name": e.name,
            "git_path": e.git_path,
        }
        for e in elements
    ]


@app.get("/elements/{element_id}")
async def get_element_detail(
    element_id: int,
    session: Session = Depends(get_session),
    auth: None = Depends(verify_api_key),
):
    element = session.get(ModelElementIndex, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="element not found")

    element_path = SYSTEMS_ROOT / element.git_path
    if not element_path.exists():
        raise HTTPException(status_code=404, detail="element file not found on disk")

    content = json.loads(element_path.read_text(encoding="utf-8"))
    return content


@app.get("/systems/{system_id}/artifact-versions")
async def list_artifact_versions_endpoint(
    system_id: int,
    session: Session = Depends(get_session),
    auth: None = Depends(verify_api_key),
):
    versions = list_artifact_versions(session, system_id)
    return [
        {
            "id": v.id,
            "commit_sha": v.commit_sha,
            "phase": v.phase,
            "approval_status": v.approval_status,
            "pr_number": v.pr_number,
            "run_id": v.run_id,
            "created_at": v.created_at,
        }
        for v in versions
    ]
