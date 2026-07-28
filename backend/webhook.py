import hashlib
import hmac
import json
from pathlib import Path
from typing import Callable

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from backend.repository.artifact_versions import (
    get_artifact_version_by_pr_number,
    update_artifact_approval,
)
from backend.repository.model_elements import upsert_model_element


def verify_signature(payload: bytes, signature_header: str | None, secret: str):
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    provided = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


def refresh_model_element_index(session: Session, systems_root: str | Path, system_id: int, system_slug: str):
    system_dir = Path(systems_root) / system_slug / "as-is"
    if not system_dir.exists():
        return 0

    count = 0
    for path in sorted(system_dir.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        upsert_model_element(
            session,
            system_id=system_id,
            layer=data["layer"],
            archimate_type=data["archimate_type"],
            name=data["name"],
            git_path=str(path.relative_to(systems_root)),
            current_commit=data.get("current_commit", ""),
        )
        count += 1
    return count


def handle_pull_request_event(
    session: Session,
    payload: dict,
    systems_root: str | Path,
    system_slug_resolver: Callable[[int], str],
) :
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    merged = pr.get("merged", False)
    pr_number = pr.get("number")

    if action != "closed" or not merged:
        return {"status": "ignored"}

    version = get_artifact_version_by_pr_number(session, pr_number)
    if version is None:
        raise HTTPException(status_code=404, detail=f"no artifact_versions row for PR {pr_number}")

    if version.approval_status == "approved":
        return {"status": "already_approved", "artifact_version_id": version.id}

    merged_by = (pr.get("merged_by") or {}).get("login")
    update_artifact_approval(session, version.id, "approved", approved_by=merged_by)

    system_slug = system_slug_resolver(version.system_id)
    refreshed = refresh_model_element_index(session, systems_root, version.system_id, system_slug)

    return {"status": "approved", "artifact_version_id": version.id, "elements_refreshed": refreshed}


def create_webhook_router(
    webhook_secret: str,
    systems_root: str | Path,
    system_slug_resolver: Callable[[int], str],
    session_dependency: Callable[..., Session],
):
    router = APIRouter()

    @router.post("/webhooks/github")
    async def github_webhook(
        request: Request,
        x_hub_signature_256: str | None = Header(default=None),
        session: Session = Depends(session_dependency),
    ):
        raw_body = await request.body()
        if not verify_signature(raw_body, x_hub_signature_256, webhook_secret):
            raise HTTPException(status_code=401, detail="invalid signature")

        payload = json.loads(raw_body)
        return handle_pull_request_event(session, payload, systems_root, system_slug_resolver)

    return router
