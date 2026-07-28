from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import ArtifactVersion


def create_artifact_version(
    session: Session,
    system_id: int,
    commit_sha: str,
    phase: str,
    author_type: str,
    run_id: str | None = None,
    pr_number: int | None = None,
) -> ArtifactVersion:
    version = ArtifactVersion(
        system_id=system_id,
        commit_sha=commit_sha,
        phase=phase,
        author_type=author_type,
        run_id=run_id,
        pr_number=pr_number,
        approval_status="pending",
    )

    session.add(version)
    session.commit()
    session.refresh(version)
    return version


def update_artifact_approval(
    session: Session,
    version_id: int,
    approval_status: str,
    approved_by: str | None = None,
) -> ArtifactVersion | None:
    version = session.get(ArtifactVersion, version_id)

    if version is None:
        return None

    if version.approval_status == approval_status:
        return version

    version.approval_status = approval_status
    version.approved_by = approved_by
    version.approved_at = (
        datetime.now(UTC)
        if approval_status == "approved"
        else None
    )

    session.commit()
    session.refresh(version)

    return version


def list_artifact_versions(
    session: Session,
    system_id: int,
) -> list[ArtifactVersion]:
    stmt = (
        select(ArtifactVersion)
        .where(ArtifactVersion.system_id == system_id)
    )

    return list(session.execute(stmt).scalars().all())


def get_artifact_version_by_run_id(
    session: Session,
    run_id: str,
) -> ArtifactVersion | None:
    stmt = (
        select(ArtifactVersion)
        .where(ArtifactVersion.run_id == run_id)
    )

    return session.execute(stmt).scalar_one_or_none()


def get_artifact_version_by_pr_number(
    session: Session,
    pr_number: int,
) -> ArtifactVersion | None:
    stmt = (
        select(ArtifactVersion)
        .where(ArtifactVersion.pr_number == pr_number)
    )

    return session.execute(stmt).scalar_one_or_none()